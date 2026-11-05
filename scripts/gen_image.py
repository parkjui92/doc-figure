#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-figure — 이미지 모델 경로 (GPT Image)

spec JSON + 프리셋 → **구조화 프롬프트 설계** → OpenAI 이미지 모델 → PNG → OCR 대조.
코드 렌더(render_figure.py)가 '정확함'을 보장한다면, 이 경로는 '표현의 폭'을 연다.
같은 spec·같은 프리셋을 쓰므로 두 경로의 그림이 한 문서 안에서 같은 집안으로 보인다.

세 가지 모드
  (기본)         spec → 프롬프트 → 새로 생성
  --from-render  코드 렌더 PNG를 참조 이미지로 넘겨 '배치는 그대로, 마감만 모델이'
                 (크롬 필요. 배치 정확도가 가장 높다)
  --fix IMAGE    이미 뽑은 그림의 특정 부분만 고친다 ("'검증 게이트' 글자가 틀렸다")

프롬프트 설계 (build_prompt)
  ① 목적 한 줄   ② 레이아웃 — 템플릿별 구도 묘사 + spec 내용을 계층 목록으로
  ③ 스타일 — 프리셋 토큰에서 팔레트 hex·모서리·그림자·제목 글꼴·강조 방식을 뽑아 문장화
  ④ 글자 규칙 — 넣을 문자열 전수 목록, 그 외 글자 금지, 번역 금지
  ⑤ 금지 — 워터마크·로고·영문 자리표시·3D·사진풍

검증
  생성 직후 OCR 로 라벨을 대조한다 — macOS Vision(1순위, 최초 1회 컴파일) → tesseract kor(대체).
  ✓ 확인 / △ OCR 불확실(눈으로 확인) / ✗ 누락 의심 — OCR 이 못 읽은 것 ≠ 모델이 틀린 것.
  △·✗ 는 반드시 이미지를 직접 보고 판정한다.

모델
  --model auto (기본) → /v1/models 를 조회해 가장 최신 gpt-image 버전을 고른다.
  같은 버전 안에서는 정밀 변형(sunburst)을 우선, --fast 면 빠른 변형(flare).
  env FIGURE_IMAGE_MODEL 로 고정할 수 있다. 실제로 쓴 모델 id 는 .meta.json 에 남는다.

사용법
  python3 gen_image.py <spec.json> [-o out.png] [--preset NAME] [--n 2]
  python3 gen_image.py <spec.json> --dry-run            # 프롬프트만 출력 (과금 0)
  python3 gen_image.py <spec.json> --from-render        # 코드 렌더를 참조로
  python3 gen_image.py <spec.json> --fix out.png --instruction "3단계 제목을 '타당성 검증'으로"
  python3 gen_image.py --models                         # 사용 가능한 이미지 모델과 auto 선택 결과

키 (값은 출력·로그에 남기지 않는다)
  env OPENAI_API_KEY → ~/.config/doc-figure/openai.key → ~/.config/figure-render/openai.key
"""
import argparse, base64, hashlib, json, os, re, shutil, ssl, subprocess, sys, tempfile, time
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import render_figure as RF  # noqa: E402  (프리셋·템플릿·텍스트 수집을 공유)

API = "https://api.openai.com/v1"
CACHE = os.path.expanduser("~/.cache/doc-figure")
FALLBACK_MODEL = "gpt-image-2.5-sunburst"
VARIANT_RANK_PRECISE = ["sunburst", "", "flare"]   # 도식은 세밀함 우선
VARIANT_RANK_FAST = ["flare", "", "sunburst"]


# ────────────────────────────── 공통 ──────────────────────────────
def ssl_ctx():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def read_key():
    k = os.environ.get("OPENAI_API_KEY")
    if k:
        return k.strip()
    for p in ("~/.config/doc-figure/openai.key", "~/.config/figure-render/openai.key"):
        p = os.path.expanduser(p)
        if os.path.isfile(p):
            return open(p).read().strip()
    sys.exit("[gen_image] OpenAI 키 없음 — env OPENAI_API_KEY 또는 ~/.config/doc-figure/openai.key (chmod 600)\n"
             "  키 없이 프롬프트만 받으려면 --dry-run")


def api_json(path, key, body=None, timeout=300):
    req = urllib.request.Request(
        API + path, data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit("[gen_image] API 오류 %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:600]))
    except urllib.error.URLError as e:
        sys.exit("[gen_image] 네트워크/SSL 오류: %s" % e.reason)


def api_multipart(path, key, fields, files, timeout=300):
    bnd = "----docfigure" + hashlib.sha1(str(time.time()).encode()).hexdigest()[:16]
    buf = []
    for k, v in fields.items():
        buf.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (bnd, k, v)).encode())
    for k, (fname, data, ctype) in files.items():
        buf.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
                    "Content-Type: %s\r\n\r\n" % (bnd, k, fname, ctype)).encode() + data + b"\r\n")
    buf.append(("--%s--\r\n" % bnd).encode())
    req = urllib.request.Request(API + path, data=b"".join(buf), headers={
        "Authorization": "Bearer " + key, "Content-Type": "multipart/form-data; boundary=" + bnd})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit("[gen_image] API 오류 %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:600]))


# ────────────────────────────── 모델 선택 ──────────────────────────────
def list_image_models(key):
    ids = [m["id"] for m in api_json("/models", key).get("data", [])]
    return sorted(i for i in ids if "image" in i)


def pick_latest(ids, fast=False):
    """gpt-image-<버전>[-<변형>] 중 최신 버전 → 변형 우선순위. 날짜 스냅샷·mini 는 제외."""
    rank = VARIANT_RANK_FAST if fast else VARIANT_RANK_PRECISE
    cands = []
    for i in ids:
        m = re.fullmatch(r"gpt-image-(\d+(?:\.\d+)?)(?:-([a-z]+))?", i)
        if not m or m.group(2) == "mini":
            continue
        ver, var = float(m.group(1)), m.group(2) or ""
        r = rank.index(var) if var in rank else len(rank)
        cands.append((-ver, r, i))
    return sorted(cands)[0][2] if cands else None


def resolve_model(arg, key, fast):
    env = os.environ.get("FIGURE_IMAGE_MODEL")
    if arg and arg != "auto":
        return arg, "지정"
    if env:
        return env, "env FIGURE_IMAGE_MODEL"
    os.makedirs(CACHE, exist_ok=True)
    cp = os.path.join(CACHE, "models.json")
    ids = None
    if os.path.exists(cp) and time.time() - os.path.getmtime(cp) < 86400:
        ids = json.load(open(cp))
    if ids is None:
        try:
            ids = list_image_models(key)
            json.dump(ids, open(cp, "w"))
        except SystemExit:
            return FALLBACK_MODEL, "목록 조회 실패 → 기본값"
    return (pick_latest(ids, fast) or FALLBACK_MODEL), "auto(최신)"


# ────────────────────────────── 프롬프트 설계 ──────────────────────────────
def tokens(css):
    return {k: v.strip() for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", css)}


def style_block(preset, css):
    t = tokens(css)
    hexv = lambda k: t.get(k, "") if t.get(k, "").startswith("#") else None
    mood = re.search(r"@image-style:\s*(.+)", css)
    mood = mood.group(1).strip() if mood else "clean flat government-report infographic, calm and precise"
    radius = int(re.sub(r"\D", "", t.get("--radius-box", "12")) or 12)
    corners = ("sharp, almost square corners" if radius <= 4 else
               "slightly rounded corners" if radius <= 8 else
               "softly rounded corners" if radius <= 13 else "generously rounded corners")
    shadow = "no drop shadows at all" if "transparent" in t.get("--shadow", "") or t.get("--shadow") == "none" \
        else "only a very subtle soft shadow under cards"
    def resolve(v, depth=0):
        v = (v or "").strip()
        m = re.fullmatch(r"var\((--[\w-]+)\)", v)
        return resolve(t.get(m.group(1)), depth + 1) if m and depth < 5 else v
    def light(hexv):
        return bool(re.fullmatch(r"#[0-9A-Fa-f]{6}", hexv)) and sum(int(hexv[i:i + 2], 16) for i in (1, 3, 5)) > 600
    sf, ff = resolve(t.get("--strong-fill")), resolve(t.get("--focus-fill", "var(--strong-fill)"))
    ring = "transparent" not in resolve(t.get("--strong-ring", "transparent"))
    if light(sf):
        strong = ("structural header cells and label boxes are %s" %
                  ("OUTLINED only (white inside, thin main-color border, main-color text)" if sf.upper() == "#FFFFFF"
                   else "a light grey fill %s with a thin grey border and dark text" % sf))
    else:
        strong = "structural header cells and label boxes are filled with the main color and use white text"
    strong += ("; the single highlighted element is filled solid %s with white text" % ff) if not light(ff) else \
              "; the highlighted element is outlined in the main color"
    serif = "Myeongjo" in t.get("--font-title", "") or "serif" == t.get("--font-title", "").split(",")[-1].strip()
    title_font = ("the title in an elegant Korean serif (Myeongjo) typeface; all other text in Korean gothic sans"
                  if serif else "all text in a clean Korean gothic sans-serif typeface")
    align = "left-aligned title with a thin rule under it" if t.get("--title-align") == "left" else "centered title"
    if t.get("--title-deco") != "none" and t.get("--title-align") != "left":
        align += ", flanked by thin horizontal rules with small dots at their ends"
    badge = "numbered badges are small circles" if "50%" in t.get("--badge-shape", "50%") else "numbered badges are small squares"
    bg = hexv("--bg")
    bgtxt = "pure white background" if (not bg or bg.upper() in ("#FFFFFF", "#FFF")) else \
        "the whole figure sits on a very light panel %s, with white cards floating on it" % bg
    pal = [("main", "--navy-deep"), ("secondary", "--navy-mid"), ("marker (gates, milestones)", "--navy-marker"),
           ("light tint", "--bar-fill"), ("border tint", "--bar-border"), ("accent (bottlenecks, failures)", "--accent"),
           ("text", "--ink"), ("muted text", "--ink-soft")]
    pal_s = ", ".join("%s %s" % (n, hexv(k)) for n, k in pal if hexv(k))
    base = ("STYLE (preset '%s'): %s. Palette ONLY: %s — no other hues. %s; %s; %s. %s. %s. %s. %s. "
            "Flat 2D vector look, crisp thin lines, no gradients, no 3D, no photographic texture."
            % (preset, mood, pal_s, bgtxt, corners, shadow, strong, title_font, align.capitalize(), badge))
    # 인쇄 도판 규율 — AI 확산 이전 전문 도판의 공통 원칙 (references/benchmark-classic.md D4)
    if re.search(r"@image-discipline:\s*kr-gov", css):
        disc = ["Render it as a diagram in a polished Korean government R&D proposal or ministry policy plan "
                "(연구개발계획서·기본계획), not as a web landing page, app UI or poster.",
                "Build hierarchy with fills, not outlines: solid deep-colour header bands and labels, pale same-hue tinted bodies, "
                "white inner cards. About 15-25% of the area carries colour; the rest is white or pale tint.",
                "Colour carries meaning and is used consistently (main=core, teal=output/pass, amber=caution/example, "
                "red dashed=failure). No rainbow of unrelated hues; at most one accent beyond the blue family.",
                "Change the grid to fit the content (1 → 3 → 2 columns, a left label column for layers); never an evenly "
                "repeated grid of identical boxes. Pack text inside boxes; keep white space outside the groups.",
                "Line icons only where the content lists an icon — thin uniform strokes in the tone colour, one per card at most. "
                "Number badges only where a number is listed.",
                "Text is crisp and large enough to print: labels at least about 1.4% of the figure width; bold for headings, regular for body.",
                "No 3D, isometric, glossy spheres, gradients, photos, clip-art people or decorative backgrounds."]
        return base + "\nKR-GOV DIAGRAM DISCIPLINE: " + " ".join(disc)
    disc = ["Render it as a figure printed in a 2010s government research report or a business newspaper, "
            "not as a web infographic, slide template or app UI.",
            "No icons, pictograms or emoji unless listed; no numbered circle badges; no decorative dots, flourishes "
            "or ornamental lines around the title.",
            "Give elements unequal visual weight by importance: only the item marked highlight (the thing the title "
            "is about) is dark; everything else stays grey or light. Avoid perfect symmetry and evenly repeated card grids.",
            "Label items directly next to the shapes instead of a separate legend where possible; keep all text horizontal.",
            "The impression should be restrained, dense but orderly — drawn by a professional information designer for print.",
            "Keep the title modest — about 1.3 times the label size, a report figure heading, never a poster headline."]
    if t.get("--caption-order", "0").strip() == "-1":
        disc.append("Put the figure caption line ABOVE the figure%s, and the unit, 'Note' and 'Source' lines in small grey "
                    "text at the bottom left." % (", centred" if t.get("--caption-align") == "center" else ", left-aligned"))
    if t.get("--title-tag", "none").strip() != "none":
        disc.append("Place one short solid accent-coloured bar at the top left above the headline — the only ornament.")
    return base + "\nPRINT-FIGURE DISCIPLINE: " + " ".join(disc)


HINTS = {
 "board": ("A composed Korean government proposal diagram. Read the nested content as a layout tree: items under 'row' sit side by side "
           "left→right (wider 'w' = wider box), items under 'col' stack top→bottom, a 'group' is a panel with a solid coloured header band "
           "and a pale tinted body holding its children, a 'band' is a full-width strip (optional dark 'label' block at its left), "
           "a 'pill' is a rounded label, 'steps' are chevron arrows in sequence, 'chips' are small rounded tags in one row, a 'diamond' "
           "is a decision diamond, 'timeline' is a horizontal phase bar with coloured segments, 'kv' are key→value rows. "
           "A card with 'head' has a coloured header strip on top; 'num' is a small number badge; 'items' are bullet lines; "
           "'icon' names a simple line pictogram to draw (e.g. database, users, search) — draw it as a thin-stroke outline icon, never "
           "as clip-art. 'tone' says what the colour MEANS: main=core/progress (deep navy), sub=secondary (blue), go=output/pass "
           "(teal), wait=caution/waiting/example (amber), stop=failure/constraint (red, dashed boxes), mute=existing/observed "
           "(grey). 'links' are arrows from one id to another, coloured by tone, dashed if dash=true, with the given label next to "
           "the arrow. 'legend' is a small legend row at the bottom right; 'note'/'source' are small grey lines at the bottom left."),
 "flow-process": "A left-to-right process of stages. Each stage: a numbered badge above a card with a bold heading and short description lines. Thin arrows between stages. Gate markers (small downward triangles with tiny labels) sit above the arrow that follows stage number `after`. A stage with highlight=true is the goal stage and uses the emphasis box style.",
 "org-chart": "Top-down organization chart: one root box in emphasis style at top center, connected by orthogonal connector lines to a single row of child boxes (white cards with main-color border). An optional advisory box sits at the upper right, linked to the root by a dashed line.",
 "structure-block": "Stacked horizontal layers, one row per layer. Each row: an emphasis-style label block on the left (layer name), and to its right a light-tinted band holding white cards side by side (bold title + small description).",
 "comparison-matrix": "A clean comparison table: header row in emphasis style with bold text; body rows separated by thin rules with a very light tint on every other row; if key_column is true the first column is bold on a light tint.",
 "concept-argument": "Hub-and-spoke argument map: the central claim in an emphasis-style rounded box in the middle; the supports split evenly into a left column and a right column of white cards, each linked to the center by smooth curved lines.",
 "decision-flow": "Vertical decision flow of sequential gates. Each gate is a bordered box containing a small pill with its number, the bold gate name, a count pill, and a row of small principle chips. From each gate a dashed accent-colored arrow branches right to a dashed accent box holding the `fail` action. Solid arrows connect gates downward and end in a final emphasis bar. A small legend: solid line = pass, dashed = fail.",
 "layer-stack": "Two stacked layers. Upper layer: light tint, dashed border, title with a small flag pill, a row of blocks. Then a divider: dashed line with a two-part pill in the middle (up label | down label). Lower layer: solid thick border, emphasis-style title bar with flag pill, a row of blocks. Below: a horizontal band of numbered step cards joined by arrows, then a one-line note.",
 "matrix-heatmap": "A judgment heat-map matrix. An arrow above the judgment columns carries the top_arrow label. Column headers: the first is a neutral grey 'baseline' column, the rest in emphasis style, each with a small tag pill. Rows are grouped under narrow vertical group bands on the far left; each row has a row label, a neutral baseline cell, then judgment cells whose fill follows `level` (1 = very light tint, 2 = medium tint, 3 = darkest main color with white text). A legend at the bottom.",
 "timeline-gantt": "A Gantt schedule. Month headers across the top in emphasis-style cells. One row per stage: an emphasis-style badge on the left (badge + label) and a light bar spanning from column `start` to `end` (0 = left edge of the first month, fractions allowed) with bar_label inside, and a small downward triangle gate marker with tiny gate text at the bar end. Below: a milestone axis with diamond markers at the given columns and labels above them, small deliverable boxes spanning from_col to to_col under the axis, and a cumulative emphasis box at the right end. A footer band: department chip, value, list, and a donut KPI filled to donut_pct percent.",
 "timeline-tracks": "A multi-track timeline. A year ruler along the bottom from axis.start to axis.end. Several horizontal tracks stacked; each has a vertical name tag on the left and a colored axis line. Each node is a dot on its track at year `at`, with a short vertical connector down to a small label box showing the year and label. Track tone 1 = main color, 2 = mid grey-blue, 3 = light grey.",
 "pipe-mapping": "A bottleneck map. Segment names across the top separated by small arrows. One row per lane: an emphasis-style lane label on the left; a long horizontal rounded grey pipe divided into the segments; accent-colored hourglass constriction marks where each block sits, with the block label in accent color just below; on the right, arrows run from the blocks to white response boxes (nodes), and an accent-tinted note sits under them.",
}
HINTS.update({
 "cycle": "A circular cycle diagram: the items are round nodes evenly spaced on a circle, joined clockwise by curved arrows so the last flows back into the first — the loop must be unmistakable. The optional center holds the system name in an emphasis circle. A highlighted item uses the emphasis style.",
 "funnel": "A vertical funnel: stacked trapezoid bands narrowing from top to bottom, one band per stage with its label and value inside; bands darken toward the bottom. To the right, notes align with their bands; each `drop` appears as an accent-colored dashed box with an arrow branching out between bands (what fell out at that step).",
 "venn": "A Venn diagram of 2 or 3 overlapping translucent circles in distinct palette hues. Each set's title and description sit in its exclusive area; overlap labels sit inside the pairwise intersections (key \"12\" = sets 1 and 2), and \"123\" sits in the triple center.",
 "quadrant": "A 2x2 positioning matrix: x axis low→high left to right, y axis low→high bottom to top, both with arrowheads, axis names and end labels. Four quadrants each titled in their outer corner (order: top-left, top-right, bottom-left, bottom-right); the `focus` quadrant is lightly tinted. Items are dots at their (x, y) positions on a 0–1 scale with labels; highlighted items are larger and accent-colored. The takeaway sits in an emphasis box to the right.",
 "pyramid": "A pyramid of horizontal layers, apex on top (darkest) to base at the bottom (lightest); each layer's title inside it; descriptions to the right aligned with each layer through thin dashed leader lines.",
 "concentric": "Concentric rings from the innermost core (emphasis fill) outward to the lightest outer ring; each ring's title sits in its band; a legend on the right repeats each ring with a color swatch and its description.",
 "hub": "Hub-and-spoke: a central emphasis box, nodes arranged evenly on an ellipse around it, each linked to the center by a straight line; nodes are white cards with main-color borders — peers, not a hierarchy.",
 "fishbone": "An Ishikawa fishbone: a thick horizontal spine pointing right into the effect box (emphasis style) at the right end; category ribs slant diagonally from the spine, alternating above and below, each ending in a small pill with the category name; causes attach to each rib with short horizontal ticks and labels.",
 "staircase": "An ascending staircase: blocks left to right, each taller than the one before, bottoms aligned; inside each block at its top a small tag (year), a bold title and a short description; the last and tallest block uses the emphasis style; a small accent flag box above it carries the goal.",
 "before-after": "A before/after comparison: a muted grey card on the left (current state, bullet list), a large light right-pointing arrow in the middle listing the transition levers, and a main-color bordered card on the right (future state, bullet list). Left and right lists read as a direct contrast.",
 "waterfall": "A waterfall (bridge) chart: the starting total bar on the left, floating bars for each increase (main color) or decrease (accent color) stepping up and down, dashed connectors at each running level, and the ending total bar in emphasis color on the right; signed value labels above the bars, category labels below. If the vertical axis is truncated, show a small break mark and the note.",
 "iceberg": "An iceberg: a small white peak above a dashed waterline and a much larger tinted mass below the water — the hidden part must look several times bigger. The `above` items are listed beside the peak; the `below` title and items are written inside the underwater mass.",
 "swimlane": "A swimlane chart: one horizontal lane per actor, actor names in emphasis tags on the left; phase headers across the top; each step box sits in its lane (lane index from 0) and column (col from 0); arrows connect the steps in the listed order with orthogonal elbows; the highlighted step uses the emphasis style.",
 "logic-tree": "A left-to-right logic (issue) tree: the root goal in an emphasis box on the left, first-level branches as light-tinted boxes in the middle, leaf actions as white cards on the right, all joined by orthogonal bracket connectors — mutually exclusive, collectively exhaustive.",
})
DROP = {"template", "preset", "layout", "_lane", "_align", "_w", "_lw", "_node", "image_layout", "body_html",
        "canvas_height", "form", "intent",
        # board 배치 키 — 그림 내용이 아니라 자리 잡는 값
        "gap", "widths", "align", "valign", "justify", "indent", "indent_r", "lane_r", "lane_l", "offset", "via",
        "from_side", "to_side", "from_x", "to_x", "from_y", "to_y", "from_shift", "to_shift", "label_at", "label_dx",
        "label_dy", "label_side", "label_w", "key_w", "size_w", "size_h", "pad", "width", "font_scale", "h", "spacer"}


def outline(o, ind=0, keep=()):
    """spec 내용을 사람이 읽는 계층 목록으로 — 문자열은 따옴표로 원문 그대로."""
    pad, out = "  " * ind, []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in DROP and k not in keep:
                continue
            name = k.lstrip("_")
            if isinstance(v, (dict, list)):
                out.append("%s- %s:" % (pad, name))
                out += outline(v, ind + 1, keep)
            else:
                out.append("%s- %s: %s" % (pad, name, json.dumps(v, ensure_ascii=False)))
    elif isinstance(o, list):
        for i, v in enumerate(o, 1):
            if isinstance(v, (dict, list)):
                out.append("%s- [%d]" % (pad, i))
                out += outline(v, ind + 1, keep)
            else:
                out.append("%s- %s" % (pad, json.dumps(v, ensure_ascii=False)))
    return out


def texts(spec):
    seen, out = set(), []
    for s in RF.collect_strings({k: v for k, v in spec.items() if k not in ("template", "preset", "form")}):
        if s not in seen:
            seen.add(s); out.append(s)
    return out


def build_prompt(spec, preset, css, from_render=False, hint=None):
    spec = RF.resolve_form(spec)
    tpl = spec.get("form") or spec.get("template", "")
    body = {k: v for k, v in spec.items() if k not in ("title", "subtitle", "caption")}
    L = ["Create a finished diagram figure for a Korean policy / research document (landscape, print quality)."]
    it = spec.get("intent") or {}
    if it.get("message"):
        L.append("\nPURPOSE (guidance only — do NOT draw this sentence): after one glance the reader must grasp "
                 "\"%s\"%s. Make that relationship the visual focal point; everything else is supporting detail."
                 % (it["message"], (" — the relationship type is %s" % it["relation"]) if it.get("relation") else ""))
    if from_render:
        L.append("\nREFERENCE: The attached image is an exact code-rendered draft of this figure. KEEP its layout, "
                 "positions, reading order, connections and every piece of text exactly as they are. Only upgrade the "
                 "visual finish to match the STYLE below (line quality, spacing rhythm, typographic polish, small "
                 "meaningful line icons where cards have room). Do not add, remove, move or reword anything.")
    L.append("\nLAYOUT:")
    if spec.get("title"):
        L.append("- Title: \"%s\"" % spec["title"] + (", with a smaller muted subtitle below it: \"%s\"" % spec["subtitle"] if spec.get("subtitle") else ""))
    lay = spec.get("image_layout") or HINTS.get(tpl) or "Arrange the content below as a clear, well-balanced diagram."
    L.append("- Composition: " + lay)
    if hint:
        L.append("- Additional direction: " + hint)
    L.append("- Content (render every item; field names are not text to draw):")
    L += ["  " + x for x in outline(body, keep=("_lane",) if tpl == "swimlane" else ())]
    if tpl == "freeform" and spec.get("body_html"):
        L.append("- The labels to place (from the draft markup): " + " / ".join('"%s"' % s for s in RF.markup_text(spec["body_html"])))
    tk = tokens(css)
    side = "left-aligned" if tk.get("--caption-align") == "left" else "centered"
    where = "at the very top, above the title" if tk.get("--caption-order", "0").strip() == "-1" else "at the bottom"
    if spec.get("caption"):
        L.append("- Figure caption %s, %s: \"%s\"" % (where, side, spec["caption"]))
    if spec.get("unit"):
        L.append("- Unit line, small, right-aligned just below the caption: \"%s\"" % (spec["unit"] if spec["unit"].startswith("(") else "(단위: %s)" % spec["unit"]))
    if spec.get("footnote"):
        L.append("- Note line, small grey, bottom left: \"%s\"" % spec["footnote"])
    if spec.get("source"):
        L.append("- Source line, small grey, bottom left (last line): \"%s\"" % (spec["source"] if spec["source"].startswith(("자료", "출처", "Source")) else "자료: " + spec["source"]))
    L.append("\n" + style_block(preset, css))
    ts = texts(spec)
    L.append("\nTEXT RULES: The image must contain exactly these %d Korean/number strings and nothing else — "
             "render each character for character, never translate, never paraphrase, never add filler words, "
             "English, lorem ipsum, logos or watermarks. Keep line breaks as given (\\n)." % len(ts))
    L += ["  %d. \"%s\"" % (i, s) for i, s in enumerate(ts, 1)]
    L.append("\nAVOID: 3D, isometric, gradients, photos, clip-art people, decorative backgrounds, drop shadows heavier "
             "than described, any text not listed above — including numbering badges, circled numbers or step numbers "
             "that are not in the list (added numbers imply an order or priority the author did not state).")
    return "\n".join(L), ts


# ────────────────────────────── OCR 대조 ──────────────────────────────
# 1순위 macOS Vision(한국어 인식이 tesseract 보다 월등 — 색 바탕 위 작은 글씨까지 읽는다)
# 2순위 tesseract kor. 둘 다 없으면 대조를 건너뛰고 '눈으로 확인'만 안내한다.
VOCR_SRC = r"""
import Foundation
import Vision
import AppKit
let path = CommandLine.arguments[1]
guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(2) }
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.recognitionLanguages = ["ko-KR", "en-US"]
req.usesLanguageCorrection = false
try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
for o in (req.results ?? []) { if let c = o.topCandidates(1).first { print(c.string) } }
"""


def vision_bin():
    if sys.platform != "darwin" or not shutil.which("swiftc"):
        return None
    b = os.path.join(CACHE, "vocr")
    if os.path.exists(b):
        return b
    os.makedirs(CACHE, exist_ok=True)
    src = os.path.join(CACHE, "vocr.swift")
    open(src, "w").write(VOCR_SRC)
    print("[ocr] macOS Vision 인식기 최초 컴파일 중 (1회, 30초 안팎)…")
    r = subprocess.run(["swiftc", "-O", src, "-o", b], capture_output=True, text=True)
    return b if r.returncode == 0 and os.path.exists(b) else None


def ocr_text(png):
    vb = vision_bin()
    if vb:
        r = subprocess.run([vb, png], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout, "macOS Vision"
    if shutil.which("tesseract"):
        got = ""
        for psm in ("11", "3"):
            got += subprocess.run(["tesseract", png, "-", "-l", "kor+eng", "--psm", psm],
                                  capture_output=True, text=True).stdout
        return got, "tesseract"
    return None, None


def norm_ocr(s):
    """OCR 이 흔히 바꿔 읽는 기호를 한 벌로 — 글자(한글·숫자) 대조에 집중한다."""
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[·•ㆍ・‧∙]", "·", s)
    s = re.sub(r"(\|\||∥|‖)", "|", s)
    s = re.sub(r"[—–→－-]+", "-", s)
    return s


def ocr_check(png, strings):
    got, engine = ocr_text(png)
    if got is None:
        return None, None
    got = norm_ocr(got)
    import difflib
    res = []
    for s in strings:
        for line in s.split("\n"):
            n = norm_ocr(line)
            if not n:
                continue
            if n in got:
                res.append(("✓", line)); continue
            best = 0.0
            for i in range(0, max(1, len(got) - len(n) + 1)):
                best = max(best, difflib.SequenceMatcher(None, n, got[i:i + len(n)]).ratio())
                if best > 0.99:
                    break
            res.append(("△" if best >= 0.6 else "✗", line))
    return res, engine


# ────────────────────────────── 실행 ──────────────────────────────
def save_images(data, out, n):
    paths = []
    for i, d in enumerate(data.get("data", []), 1):
        p = out if n == 1 else re.sub(r"(\.png)?$", "_%d.png" % i, out, count=1)
        with open(p, "wb") as f:
            f.write(base64.b64decode(d["b64_json"]))
        paths.append(p)
    return paths


def main():
    ap = argparse.ArgumentParser(description="doc-figure 이미지 모델 경로 (GPT Image)")
    ap.add_argument("spec", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--preset")
    ap.add_argument("--model", default="auto", help="auto(기본, 최신) 또는 모델 id")
    ap.add_argument("--fast", action="store_true", help="빠른 변형(flare) 우선")
    ap.add_argument("--size", default="1536x1024", help="1536x1024(기본·가로) / 1024x1536 / 1024x1024")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--n", type=int, default=1, help="후보 장수 (골라 쓰기)")
    ap.add_argument("--hint", help="레이아웃 추가 지시 (영문 권장)")
    ap.add_argument("--from-render", action="store_true", help="코드 렌더를 참조 이미지로 (크롬 필요)")
    ap.add_argument("--fix", metavar="IMAGE", help="이미 뽑은 그림을 부분 수정")
    ap.add_argument("--instruction", help="--fix 수정 지시")
    ap.add_argument("--dry-run", action="store_true", help="프롬프트만 출력 (API 호출·과금 0)")
    ap.add_argument("--no-ocr", action="store_true")
    ap.add_argument("--models", action="store_true", help="이미지 모델 목록과 auto 선택 결과")
    a = ap.parse_args()

    if a.models:
        key = read_key(); ids = list_image_models(key)
        print("이미지 모델 %d종: %s" % (len(ids), ", ".join(ids)))
        print("auto(정밀) → %s   /   auto --fast → %s" % (pick_latest(ids), pick_latest(ids, True)))
        return
    if not a.spec:
        ap.error("spec JSON 경로가 필요합니다")
    spec = json.load(open(a.spec, encoding="utf-8"))
    preset = a.preset or spec.get("preset") or RF.DEFAULT_PRESET
    css = RF.load_preset(preset)
    out = a.out or os.path.splitext(a.spec)[0] + ".gpt.png"

    if a.fix:
        if not a.instruction:
            ap.error("--fix 에는 --instruction 이 필요합니다")
        ts = texts(spec)
        prompt = ("Edit this diagram. Change ONLY the following and leave every other pixel, word and position "
                  "untouched: %s\nAll Korean text must stay exactly as in this list: %s"
                  % (a.instruction, " / ".join('"%s"' % s for s in ts)))
    else:
        prompt, ts = build_prompt(spec, preset, css, a.from_render, a.hint)

    if a.dry_run:
        print(prompt)
        print("\n[gen_image] (dry-run) 프롬프트 %d자 · 대조 문자열 %d건 · 프리셋 %s" % (len(prompt), len(ts), preset))
        return

    key = read_key()
    model, why = resolve_model(a.model, key, a.fast)
    print("[gen_image] 모델 %s (%s) · 프리셋 %s · %s %s" % (model, why, preset, a.size, a.quality))
    t0 = time.time()
    if a.fix or a.from_render:
        if a.fix:
            ref = open(a.fix, "rb").read()
        else:
            tmp = tempfile.mkdtemp(prefix="docfig_")
            refp = os.path.join(tmp, "ref.png")
            r = subprocess.run([sys.executable, os.path.join(HERE, "render_figure.py"), a.spec,
                                "--preset", preset, "-o", refp, "--scale", "1"], capture_output=True, text=True)
            if not os.path.exists(refp):
                sys.exit("[gen_image] 참조 렌더 실패:\n" + (r.stdout + r.stderr)[-800:])
            ref = open(refp, "rb").read()
        data = api_multipart("/images/edits", key,
                             {"model": model, "prompt": prompt, "size": a.size, "quality": a.quality, "n": str(a.n)},
                             {"image[]": ("ref.png", ref, "image/png")})
    else:
        data = api_json("/images/generations", key, {"model": model, "prompt": prompt, "size": a.size,
                                                     "quality": a.quality, "n": a.n})
    paths = save_images(data, out, a.n)
    dt = time.time() - t0
    usage = data.get("usage", {})
    print("[gen_image] ✓ %s  (%.0f초, 출력 토큰 %s)" % (", ".join(paths), dt, usage.get("output_tokens", "?")))

    base = os.path.splitext(out)[0]
    open(base + ".prompt.txt", "w", encoding="utf-8").write(prompt)
    meta = {"model": model, "model_reason": why, "preset": preset, "size": a.size, "quality": a.quality,
            "mode": "fix" if a.fix else ("from-render" if a.from_render else "generate"),
            "prompt_sha1": hashlib.sha1(prompt.encode()).hexdigest()[:12], "seconds": round(dt, 1),
            "usage": usage, "outputs": paths, "ocr": {}}
    if not a.no_ocr:
        for p in paths:
            res, engine = ocr_check(p, ts)
            if res is None:
                print("[ocr] 문자 인식기 없음(macOS Vision·tesseract) — 글자는 눈으로 확인하세요"); break
            ok = sum(1 for r in res if r[0] == "✓")
            print("[ocr] %s — ✓ %d / %d  (%s)" % (os.path.basename(p), ok, len(res), engine))
            for mark, s in res:
                if mark != "✓":
                    print("   %s %s" % (mark, s))
            if ok < len(res):
                print("   ↳ △·✗ 는 OCR 한계일 수 있습니다. 이미지를 직접 보고 판정하고, 틀렸으면 --fix 로 고치세요.")
            meta["ocr"][p] = {"engine": engine, "ok": ok, "total": len(res),
                              "flagged": [s for m, s in res if m != "✓"]}
    json.dump(meta, open(base + ".meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
