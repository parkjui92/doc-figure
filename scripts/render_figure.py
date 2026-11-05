#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-figure — 문서 삽도 렌더러 (정밀 경로)

spec JSON + 템플릿(HTML/CSS) → 헤드리스 크롬 스크린샷 → PNG.
한글 라벨·수치·정렬을 코드가 100% 정확히 그린다. 텍스트는 spec 원문을 그대로
DOM에 배치하므로 글자 깨짐이 구조적으로 불가능하다.

※ 이 스크립트는 '선택' 경로다. 크롬·파이썬 없이도 스킬이 자기완결 HTML을
   직접 써주며(기본 경로), 그 HTML을 브라우저로 열면 같은 그림이 나온다.
   이 스크립트는 PNG 자동 생성과 --verify 검증이 필요할 때 쓴다.

사용법:
  python3 render_figure.py <spec.json> [-o out.png] [--verify] [--preset NAME]
  python3 render_figure.py <spec.json> --html-only -o figure.html   # 렌더 없이 HTML만
  python3 render_figure.py --list                                    # 템플릿·프리셋 목록

옵션:
  -o/--out     출력 경로 (기본: spec 파일명 .png)
  --preset     프리셋 이름 (기본: spec의 "preset" 필드 → 없으면 house)
  --icons DIR  아이콘 PNG 디렉터리를 인라인 (기본: 없음 — 공개판은 아이콘 미탑재)
  --verify     렌더 후 spec의 모든 텍스트가 DOM에 실재하는지 대조
  --html-only  크롬 없이 자기완결 HTML만 출력 (설치 0 경로와 동일 산출)
  --scale      device pixel ratio (기본 2 = 고해상)
  --height     렌더 뷰포트 높이 (기본 1600, trim으로 자동 축소)
  --keep-html  중간 HTML을 남긴다 (디버그)

환경변수:
  CHROME_BIN   크롬 실행 경로 (기본: macOS Google Chrome)
"""
import argparse, json, os, subprocess, sys, tempfile

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")
PRESETS   = os.path.join(ROOT, "presets")
DEFAULT_PRESET = "house"   # v2.0 — 사용자 채택본 팔레트 (references/benchmark-kr-2026.md)
# 관계의 모양으로 고르는 도식 14종 — 전부 templates/forms.html 한 파일이 그린다
FORMS = ["cycle", "funnel", "venn", "quadrant", "pyramid", "concentric", "hub", "fishbone",
         "staircase", "before-after", "waterfall", "iceberg", "swimlane", "logic-tree"]
CHROME    = os.environ.get(
    "CHROME_BIN",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
CANVAS_W  = 1500  # 템플릿 고정 폭 (board 는 spec "width" 로 바꿀 수 있다)
ICON_SET  = os.path.join(TEMPLATES, "icons", "tabler-outline.json")  # board 선 아이콘 (Tabler, MIT)


def available(dirpath, ext):
    if not os.path.isdir(dirpath):
        return []
    return sorted(f[:-len(ext)] for f in os.listdir(dirpath) if f.endswith(ext))


def resolve_form(spec):
    """"template": "venn" 처럼 형태 이름을 바로 쓴 spec 을 forms 템플릿으로 돌린다."""
    t = spec.get("template")
    if t in FORMS:
        spec = dict(spec, form=t, template="forms")
    return spec


def load_template(name):
    path = os.path.join(TEMPLATES, name + ".html")
    if not os.path.exists(path):
        sys.exit("[doc-figure] 템플릿 없음: %s\n  사용 가능: %s"
                 % (name, ", ".join(available(TEMPLATES, ".html"))))
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_preset(name):
    path = os.path.join(PRESETS, name + ".css")
    if not os.path.exists(path):
        sys.exit("[doc-figure] 프리셋 없음: %s\n  사용 가능: %s"
                 % (name, ", ".join(available(PRESETS, ".css"))))
    with open(path, encoding="utf-8") as f:
        return f.read()


def preset_color(tokens_css, name="--navy-deep"):
    """프리셋 CSS에서 토큰의 hex 값을 읽는다 (아이콘 리컬러용)."""
    import re
    m = re.search(r"%s:\s*(#[0-9A-Fa-f]{6})" % re.escape(name), tokens_css)
    return m.group(1) if m else None


def recolor_png(data, hexcolor):
    """단색 아이콘(알파 보유)의 RGB를 프리셋 주색으로 바꾼다. Pillow 없으면 원본."""
    try:
        from PIL import Image
        import io
    except ImportError:
        return data
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    rgb = tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    solid = Image.new("RGBA", im.size, rgb + (255,))
    solid.putalpha(im.getchannel("A"))
    out = io.BytesIO()
    solid.save(out, "PNG")
    return out.getvalue()


def inline_icons(icons_dir, color=None):
    """아이콘 PNG를 base64 data URI 맵으로 인라인. 디렉터리 미지정이면 빈 맵.

    공개판은 아이콘을 탑재하지 않는다(외부 API 의존 0). 템플릿은 아이콘이
    없으면 번호·텍스트로 안전하게 퇴화하도록 작성되어 있다.
    color 를 주면 아이콘을 그 색으로 리컬러한다 — 프리셋을 바꾸면 아이콘도 따라간다.
    """
    if not icons_dir:
        return {}
    import base64, glob
    if not os.path.isdir(icons_dir):
        sys.exit("[doc-figure] 아이콘 디렉터리 없음: %s" % icons_dir)
    icons = {}
    for p in glob.glob(os.path.join(icons_dir, "*.png")):
        name = os.path.splitext(os.path.basename(p))[0]
        with open(p, "rb") as f:
            data = f.read()
        if color:
            data = recolor_png(data, color)
        icons[name] = "data:image/png;base64," + base64.b64encode(data).decode()
    return icons


# 인쇄 글자 크기 측정 — 모든 템플릿 공통. 보이는 글자 조각마다 실제 글자 크기(px, SVG 배율 반영)와
# 글자 수를 적어 둔다. 렌더러가 PNG 폭과 삽입 폭(print_cm)으로 pt를 계산한다.
FONT_PROBE = """<pre id="__font_sizes" style="display:none"></pre>
<script>
(function(){
  function probe(){
    var out=[], root=document.getElementById('figure')||document.body;
    var w=document.createTreeWalker(root, NodeFilter.SHOW_TEXT), n;
    while((n=w.nextNode())){
      var s=(n.nodeValue||'').trim(); if(!s) continue;
      var e=n.parentElement; if(!e||e.closest('pre,script,style')) continue;
      var cs=getComputedStyle(e); if(cs.display==='none'||cs.visibility==='hidden'||parseFloat(cs.opacity)===0) continue;
      var r=document.createRange(); r.selectNodeContents(n); var rr=r.getBoundingClientRect(); if(!rr.width) continue;
      var fs=parseFloat(cs.fontSize);
      if(e instanceof SVGElement && e.getScreenCTM){ var m=e.getScreenCTM(); if(m) fs=fs*Math.sqrt(Math.abs(m.a*m.d-m.b*m.c)); }
      out.push([Math.round(fs*10)/10, s.length, s.slice(0,16)]);
    }
    document.getElementById('__font_sizes').textContent=JSON.stringify(out);
  }
  if(document.readyState==='complete') setTimeout(probe,300); else window.addEventListener('load',function(){ setTimeout(probe,300); });
})();
</script>
"""

PRINT_CM = 16.0      # 기본 삽입 폭 — A4 세로 본문(여백 제외 15~17cm)
BODY_PT_MIN = 9.0    # 본문(글자 수 가중 중앙값) 하한 — board 는 10pt 로 맞춘다. 사용자 승인 연구개발계획서 그림 약 10pt, 2026-10-27 "글씨가 너무 작다"
MIN_PT = 8.0         # 가장 작은 글자 하한 — 주석·화살표 이름표·자료 줄 포함


def print_sizes(dom, png_path, scale, print_cm):
    """인쇄했을 때의 글자 크기(pt). 그림을 print_cm 폭으로 넣는다고 보고 계산한다."""
    import re, html as _h
    m = re.search(r'<pre id="__font_sizes"[^>]*>(.*?)</pre>', dom, re.S)
    if not m or not m.group(1).strip():
        return None
    try:
        items = json.loads(_h.unescape(m.group(1)))
        from PIL import Image
        w = Image.open(png_path).size[0] / float(scale)
    except Exception:
        return None
    k = (print_cm / 2.54 * 72.0) / w           # pt per CSS px
    items = [(fs * k, n, t) for fs, n, t in items if n >= 2 or re.search(r"[가-힣0-9A-Za-z]", t)]
    if not items:
        return None
    tot = sum(n for _, n, _ in items); acc = 0; body = items[0][0]
    for pt, n, _ in sorted(items):
        acc += n
        if acc >= tot / 2:
            body = pt; break
    smallest = min(items, key=lambda x: x[0])
    return body, smallest[0], smallest[2], w


def build_html(template_html, spec, tokens_css, icons_dir=None):
    """템플릿의 마커 3개를 치환해 자기완결 HTML을 만든다.

    마커 규약 (템플릿을 새로 만들 때도 동일하게 쓴다):
      /*__STYLE_TOKENS__*/   → 프리셋 CSS 본문
      /*__FIGURE_DATA__*/    → spec JSON
      /*__ICONS__*/          → 아이콘 data URI 맵 (없으면 {})
    """
    html = template_html.replace("/*__STYLE_TOKENS__*/", tokens_css)
    icons = json.dumps(inline_icons(icons_dir, preset_color(tokens_css)), ensure_ascii=False)
    html = html.replace("/*__ICONS__*/ {}", icons)
    html = html.replace("/*__ICONS__*/", icons)
    if "/*__ICON_SET__*/" in html:
        iset = "{}"
        if os.path.exists(ICON_SET):
            with open(ICON_SET, encoding="utf-8") as f:
                iset = f.read()
        html = html.replace("/*__ICON_SET__*/ {}", iset).replace("/*__ICON_SET__*/", iset)
    if "</body>" in html and "__font_sizes" not in html:
        html = html.replace("</body>", FONT_PROBE + "</body>", 1)
    data = json.dumps(spec, ensure_ascii=False)
    # 두 형태 모두 대응: "/*__FIGURE_DATA__*/ null" 또는 단독 마커
    html = html.replace("/*__FIGURE_DATA__*/ null", data)
    html = html.replace("/*__FIGURE_DATA__*/", data)
    return html


def chrome(args):
    if not os.path.exists(CHROME):
        sys.exit("[doc-figure] 크롬을 찾을 수 없음: %s\n"
                 "  CHROME_BIN 환경변수로 경로를 지정하거나, --html-only 로\n"
                 "  HTML만 만들어 브라우저에서 직접 여세요." % CHROME)
    base = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--force-color-profile=srgb",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=2000"]
    return subprocess.run(base + args, capture_output=True, text=True)


def screenshot(html_path, out_path, height, scale, width=CANVAS_W):
    r = chrome(["--force-device-scale-factor=%s" % scale,
                "--window-size=%d,%d" % (width, height),
                "--default-background-color=FFFFFFFF",
                "--screenshot=%s" % out_path,
                "file://" + html_path])
    if not os.path.exists(out_path):
        sys.exit("[doc-figure] 크롬 렌더 실패:\n%s" % (r.stderr[-1000:] or r.stdout[-1000:]))


def trim_white(out_path, margin, scale, keep_x=False, width=CANVAS_W):
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return None  # Pillow 없으면 trim만 생략, 렌더는 성공
    im = Image.open(out_path).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bbox = ImageChops.difference(im, bg).getbbox()
    if not bbox:
        return im.size
    m = int(margin * scale)
    l, t, r, b = bbox
    if keep_x:   # 프리셋 --trim-x: none — 좌우는 그림 틀 폭 그대로 (문서 속 그림 폭 통일)
        l, r = 0, min(im.width, int(width * scale))
        m_x = 0
    else:
        m_x = m
    box = (max(0, l - m_x), max(0, t - m), min(im.width, r + m_x), min(im.height, b + m))
    im = im.crop(box)
    im.save(out_path)
    return im.size


# 잘 그린 공공 도식 57장(중앙부처·연구기관·R&D 기획·해외 공공기관)의 중앙값
# references/benchmark-kr-2026.md §2 — 흰 바탕 60%(갈래별 59~67%), 유채색 면적 17%(12~22%).
# 못 그린 9장은 색 39~67%(그라데이션·3D·무지개) 또는 흰 바탕 86%(휑함). 클립아트는 수치로 못 잡는다.
BENCH_WHITE = (0.55, 0.72)
BENCH_CHROMA = (0.12, 0.25)


def impression(out_path, grey=False):
    """흰 바탕·유채색 면적 비율. 와이어프레임처럼 휑한지(흰 바탕 과다), 색이 뜻을 싣는지를 잰다."""
    try:
        from PIL import Image
    except ImportError:
        return None
    im = Image.open(out_path).convert("RGB")
    im.thumbnail((900, 900))
    px = im.load(); w, h = im.size; n = w * h
    white = chroma = 0
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if min(r, g, b) >= 242:
                white += 1
            if max(r, g, b) - min(r, g, b) >= 28:
                chroma += 1
    return white / n, chroma / n


def dump_dom(html_path):
    return chrome(["--dump-dom", "file://" + html_path]).stdout or ""


def layout_issues(dom):
    """board 템플릿이 스스로 잰 배치 문제(글자 넘침·화살표 관통·작은 글자)를 읽는다."""
    import re, html as _h
    m = re.search(r'<pre id="__layout_issues"[^>]*>(.*?)</pre>', dom, re.S)
    if not m or not m.group(1).strip():
        return []
    try:
        return json.loads(_h.unescape(m.group(1)))
    except ValueError:
        return []


def dump_text(html_path, dom=None):
    import re
    dom = dom if dom is not None else dump_dom(html_path)
    dom = re.sub(r'(?s)<pre id="__layout_issues".*?</pre>', " ", dom)
    dom = re.sub(r'(?s)<pre id="__font_sizes".*?</pre>', " ", dom)
    dom = re.sub(r"(?is)<script.*?</script>", " ", dom)
    dom = re.sub(r"(?is)<style.*?</style>", " ", dom)
    dom = re.sub(r"(?s)<[^>]+>", " ", dom)
    dom = dom.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", dom).strip()


# 렌더되지 않는 구조·참조용 키(텍스트 대조에서 제외)
NON_TEXT_KEYS = {"template", "preset", "icon", "dept_icon", "highlight",
                 "recolor", "hash", "model", "size", "canvas_height", "form", "intent", "image_layout",
                 # board — 배치·모양 키
                 "id", "tone", "fill", "accent", "head_style", "num_style", "layout", "align", "valign",
                 "style", "bullet", "widths", "join", "gap", "route", "from", "to", "from_side", "to_side",
                 "via", "shape", "header", "indent", "indent_r", "lane_r", "lane_l", "offset", "label_side", "print_cm", "body_pt", "cols", "head_align", "justify", "label_at", "font_scale", "w", "h"}


# 마크업이 든 키 — 태그를 걷어낸 글자 조각을 대조한다 (freeform)
MARKUP_KEYS = {"body_html"}


def markup_text(markup):
    import html, re
    markup = re.sub(r"(?is)<(style|script)\b.*?</\1>", " ", markup)
    parts = re.split(r"<[^>]+>", markup)
    return [html.unescape(p).strip() for p in parts if html.unescape(p).strip()]


def color_leaks(spec):
    """freeform 본문에 프리셋을 빠져나가는 색(#hex·rgb·hsl)이 있는지."""
    import re
    body = spec.get("body_html") or ""
    return sorted(set(re.findall(r"#[0-9A-Fa-f]{3,8}\b|\b(?:rgba?|hsla?)\([^)]*\)", body)))


def collect_strings(obj, key=None):
    out = []
    if key is not None and (key in NON_TEXT_KEYS or key.startswith("_")):
        return out
    if key in MARKUP_KEYS and isinstance(obj, str):
        return markup_text(obj)
    if isinstance(obj, str):
        for line in obj.split("\n"):
            line = line.strip()
            if line:
                out.append(line)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out += collect_strings(v, k)
    elif isinstance(obj, list):
        for v in obj:
            out += collect_strings(v, key)
    return out


def verify(spec, html_path, dom=None):
    dom = dump_text(html_path, dom)
    norm = lambda s: "".join(s.split())
    domn = norm(dom)
    checkable = {k: v for k, v in spec.items() if k not in ("template", "preset", "form")}
    strings = collect_strings(checkable)
    missing = [s for s in strings if norm(s) not in domn]
    if "[forms 오류]" in dom:   # 도식 렌더러가 멈췄다 — 글자가 다 있어도 실패
        missing.append(dom[dom.index("[forms 오류]"):][:120])
    return strings, missing


def main():
    ap = argparse.ArgumentParser(description="doc-figure — 문서 삽도 렌더러")
    ap.add_argument("spec", nargs="?", help="spec JSON 경로")
    ap.add_argument("-o", "--out", help="출력 경로")
    ap.add_argument("--preset", help="프리셋 이름 (기본: spec의 preset → house)")
    ap.add_argument("--icons", help="아이콘 PNG 디렉터리 (선택)")
    ap.add_argument("--verify", action="store_true", help="텍스트 실재 대조")
    ap.add_argument("--html-only", action="store_true", help="크롬 없이 HTML만 출력")
    ap.add_argument("--list", action="store_true", help="템플릿·프리셋 목록")
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--height", type=int, default=1600)
    ap.add_argument("--margin", type=int, default=22)
    ap.add_argument("--keep-html", action="store_true")
    a = ap.parse_args()

    if a.list:
        print("템플릿 (%d): %s" % (len(available(TEMPLATES, ".html")),
                                   ", ".join(available(TEMPLATES, ".html"))))
        print("도식 형태 (%d, forms): %s" % (len(FORMS), ", ".join(FORMS)))
        print("프리셋 (%d): %s" % (len(available(PRESETS, ".css")),
                                   ", ".join(available(PRESETS, ".css"))))
        return
    if not a.spec:
        ap.error("spec JSON 경로가 필요합니다 (목록은 --list)")

    with open(a.spec, encoding="utf-8") as f:
        spec = resolve_form(json.load(f))
    template = spec.get("template")
    if not template:
        sys.exit("[doc-figure] spec에 'template' 필드가 필요합니다.\n"
                 "  사용 가능: %s" % ", ".join(available(TEMPLATES, ".html")))
    preset = a.preset or spec.get("preset") or DEFAULT_PRESET

    tokens = load_preset(preset)
    html = build_html(load_template(template), spec, tokens, a.icons)

    if a.html_only:
        out = a.out or os.path.splitext(a.spec)[0] + ".html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print("[doc-figure] ✓ %s  template=%s  preset=%s  (브라우저로 여세요)"
              % (out, template, preset))
        return

    out = a.out or os.path.splitext(a.spec)[0] + ".png"
    fd, html_path = tempfile.mkstemp(suffix=".html", prefix="docfigure_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html)

    width = max(CANVAS_W, int(spec.get("width") or CANVAS_W))
    try:
        screenshot(html_path, out, a.height, a.scale, width)
        import re as _re
        keep_x = bool(_re.search(r"--trim-x:\s*none", tokens))
        size = trim_white(out, a.margin, a.scale, keep_x, width)
        print("[doc-figure] ✓ %s  (%s)  template=%s  preset=%s"
              % (out, ("%dx%d" % size if size else "?"), template, preset))
        if a.verify:
            dom = dump_dom(html_path)
            strings, missing = verify(spec, html_path, dom)
            if missing:
                print("[verify] ✗ DOM 미출력 텍스트 %d건:" % len(missing))
                for s in missing:
                    print("   - %s" % s)
                sys.exit(2)
            leaks = color_leaks(spec)
            if leaks:
                print("[verify] ✗ 본문에 프리셋 밖 색 %d종: %s — ff-/s- 클래스나 var(--토큰)으로 바꾸세요"
                      % (len(leaks), ", ".join(leaks)))
                sys.exit(3)
            print("[verify] ✓ spec 텍스트 %d건 전부 DOM에 실재 (글자 깨짐 0)" % len(strings))
            issues = layout_issues(dom)
            if issues:
                print("[verify] ✗ 배치 문제 %d건 — 눈으로 보기 전에 고치세요:" % len(issues))
                for s_ in issues:
                    print("   - %s" % s_)
                sys.exit(4)
            if template == "board":
                print("[verify] ✓ 배치 점검 통과 (글자 넘침·화살표 관통·작은 글자 0)")
            ps = print_sizes(dom, out, a.scale, float(spec.get("print_cm") or PRINT_CM))
            if ps:
                body, small, small_t, cw = ps
                pc = float(spec.get("print_cm") or PRINT_CM)
                bad_body, bad_min = body < BODY_PT_MIN, small < MIN_PT
                mark = "✗" if (template == "board" and (bad_body or bad_min)) else ("⚠" if (bad_body or bad_min) else "✓")
                print("[verify] %s 인쇄 글자(%.0fcm 폭에 넣을 때): 본문 %.1fpt · 가장 작은 글자 %.1fpt '%s'  (권장 본문 %.1fpt 이상 · 최소 %.1fpt)"
                      % (mark, pc, body, small, small_t, BODY_PT_MIN, MIN_PT))
                if mark == "✗":
                    print("   - 글씨가 문서에 넣기엔 작다 — 글자를 줄이지 말고 한 줄 글을 줄이거나 열을 줄일 것")
                    sys.exit(5)
            imp = impression(out)
            if imp:
                wr, cr = imp
                grey = bool(_re.search(r"--tone-go:\s*#(3D3D3D|404040)", tokens)) or "mono" in preset or "print" in preset
                note = []
                if wr > 0.85:
                    note.append("흰 바탕이 %.0f%% — 와이어프레임처럼 휑해 보일 수 있음 (머리띠·옅은 바탕 채움을 늘리거나 글자를 키울 것)" % (100 * wr))
                if not grey and cr < 0.06:
                    note.append("색 면적 %.1f%% — 색이 뜻을 거의 싣지 않음" % (100 * cr))
                if cr > 0.38:
                    note.append("색 면적 %.0f%% — 무겁다 (진한 면은 머리·이름표·핵심 한 곳만)" % (100 * cr))
                print("[verify] %s 인상: 흰 바탕 %.0f%% · 색 면적 %.1f%%  (잘 그린 공공 도식 57장 중앙값 60%% · 17%%)"
                      % ("⚠" if note else "✓", 100 * wr, 100 * cr))
                for x in note:
                    print("   - " + x)
    finally:
        if a.keep_html:
            print("[doc-figure] HTML: %s" % html_path)
        else:
            os.unlink(html_path)


if __name__ == "__main__":
    main()
