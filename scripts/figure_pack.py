#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-figure — 프롬프트 + 도식 묶음 (figure pack)

한 가지 의도를 여러 '도식 형태'로 그려 본 후보 spec 들을 받아, 후보마다
  ① 코드 렌더 도식 (PNG, --verify)
  ② 이미지 모델용 설계 프롬프트 (.prompt.txt)
  ③ (선택 --gpt) 이미지 모델 생성본 + OCR 대조
를 만들고, 전부를 한 장의 카드 페이지(index.html, 자기완결)로 묶는다.
사용자는 카드를 보고 형태를 고르며, 고른 형태의 도식과 프롬프트를 그대로 쓴다.

사용법
  python3 figure_pack.py 후보1.json 후보2.json 후보3.json -o pack/ [--preset teal-lab] [--gpt] [--title "…"]

각 spec 의 "intent" 가 카드 머리가 된다:
  "intent": {"message": "독자가 알아야 할 한 문장", "relation": "관계 유형", "why": "이 형태를 고른 이유"}
"""
import argparse, base64, html, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_figure as RF  # noqa: E402
import gen_image as GI      # noqa: E402

FORM_KO = {
    "cycle": "순환도", "funnel": "깔때기", "venn": "벤 다이어그램", "quadrant": "2×2 포지셔닝", "pyramid": "피라미드",
    "concentric": "동심원", "hub": "허브·방사", "fishbone": "피시본(원인 분해)", "staircase": "계단(단계 상승)",
    "before-after": "전후 비교", "waterfall": "폭포(증감 분해)", "iceberg": "빙산(표면·심층)", "swimlane": "스윔레인(주체별 흐름)",
    "logic-tree": "로직 트리(이슈 분해)", "timeline-gantt": "간트 일정", "timeline-tracks": "다중 트랙 연표",
    "flow-process": "단계 프로세스", "decision-flow": "판정 흐름", "structure-block": "계층 구성도", "layer-stack": "2단 스택",
    "org-chart": "추진체계도", "concept-argument": "논증 도해", "comparison-matrix": "비교표", "matrix-heatmap": "판정 히트맵",
    "pipe-mapping": "병목 매핑", "freeform": "자유 도식", "board": "조립 도식",
}


def b64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser(description="doc-figure 프롬프트+도식 묶음")
    ap.add_argument("specs", nargs="+")
    ap.add_argument("-o", "--out", default="figure_pack")
    ap.add_argument("--preset", help="모든 후보에 같은 프리셋 (기본: 각 spec 의 preset → house)")
    ap.add_argument("--gpt", action="store_true", help="이미지 모델 생성본도 만든다 (키 필요, 후보당 1회 과금)")
    ap.add_argument("--from-render", action="store_true", help="--gpt 일 때 코드 렌더를 참조로")
    ap.add_argument("--title", help="묶음 제목 (기본: 첫 spec 의 intent.message)")
    ap.add_argument("--scale", default="2", help="렌더 배율 (기본 2 = 인쇄용, 1 = 가벼운 카드)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    cards = []
    for i, sp in enumerate(a.specs, 1):
        spec = json.load(open(sp, encoding="utf-8"))
        rs = RF.resolve_form(spec)
        form = rs.get("form") or rs.get("template")
        preset = a.preset or spec.get("preset") or RF.DEFAULT_PRESET
        name = "%02d_%s" % (i, form)
        png = os.path.join(a.out, name + ".png")
        code, log = run([sys.executable, os.path.join(HERE, "render_figure.py"), sp, "--preset", preset, "-o", png, "--verify", "--scale", a.scale])
        vl = [l.replace("[verify] ", "") for l in log.splitlines() if l.startswith("[verify]")]
        verify = " · ".join(vl) if vl else (log.splitlines()[-1] if log else "")
        if code:
            verify = "✗ 검증 실패 — " + verify
        prompt, ts = GI.build_prompt(spec, preset, RF.load_preset(preset))
        open(os.path.join(a.out, name + ".prompt.txt"), "w", encoding="utf-8").write(prompt)
        json.dump(spec, open(os.path.join(a.out, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        gpt, gpt_log = None, ""
        if a.gpt:
            gp = os.path.join(a.out, name + ".gpt.png")
            cmd = [sys.executable, os.path.join(HERE, "gen_image.py"), sp, "--preset", preset, "-o", gp]
            if a.from_render:
                cmd.append("--from-render")
            c2, gpt_log = run(cmd)
            gpt = gp if os.path.exists(gp) else None
        print("[pack] %s  %s  %s" % (name, "✓" if code == 0 else "✗", verify))
        cards.append(dict(name=name, form=form, preset=preset, spec=spec, png=png if os.path.exists(png) else None,
                          ok=code == 0, verify=verify, prompt=prompt, gpt=gpt, gpt_log=gpt_log, strings=len(ts)))

    first = (cards[0]["spec"].get("intent") or {}) if cards else {}
    title = a.title or first.get("message") or "도식 후보"
    open(os.path.join(a.out, "index.html"), "w", encoding="utf-8").write(page(title, cards))
    print("[pack] ✓ %s/index.html — 후보 %d개" % (a.out, len(cards)))


def page(title, cards):
    e = html.escape
    items = []
    for n, c in enumerate(cards, 1):
        it = c["spec"].get("intent") or {}
        img = '<img src="%s" alt="%s">' % (b64(c["png"]), e(c["spec"].get("title", ""))) if c["png"] else '<div class="miss">렌더 실패</div>'
        gpt = ""
        if c["gpt"]:
            ocr = next((l for l in c["gpt_log"].splitlines() if l.startswith("[ocr]")), "")
            gpt = ('<details open><summary>이미지 모델 생성본</summary><img src="%s" alt="GPT"><p class="meta">%s — 라벨은 눈으로 다시 읽을 것</p></details>'
                   % (b64(c["gpt"]), e(ocr)))
        items.append('''
<section class="card">
  <header>
    <span class="no">후보 %d</span>
    <h2>%s <small>%s</small></h2>
    <p class="rel">%s</p>
    %s
  </header>
  <figure>%s</figure>
  <p class="meta %s">%s · 프리셋 %s · 대조 문자열 %d건</p>
  %s
  <details><summary>이미지 모델 프롬프트 <button type="button" onclick="cp(this)">복사</button></summary><pre>%s</pre></details>
</section>''' % (n, e(FORM_KO.get(c["form"], c["form"])), e(c["form"]),
                 e(("관계: " + it["relation"]) if it.get("relation") else ""),
                 ('<p class="why">%s</p>' % e(it["why"])) if it.get("why") else "",
                 img, "ok" if c["ok"] else "ng", e(c["verify"]), e(c["preset"]), c["strings"], gpt, e(c["prompt"])))
    return '''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>도식 후보 묶음</title>
<style>
:root{--bg:#F6F7F9;--card:#FFFFFF;--ink:#1B2233;--soft:#5A6478;--line:#DDE1E8;--acc:#1E3A78;--ok:#1F7A4D;--ng:#B03A3F}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#14171C;--card:#1C2027;--ink:#E7EAF0;--soft:#9AA3B2;--line:#2C323C;--acc:#9DB4E0;--ok:#6CC59A;--ng:#E58A8E}}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);font-family:"Apple SD Gothic Neo","Pretendard","Malgun Gothic",sans-serif;word-break:keep-all}
main{max-width:1180px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:24px;margin:0 0 6px} .lead{color:var(--soft);margin:0 0 24px;font-size:15px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;margin:0 0 22px}
.card header{margin-bottom:12px} .no{font-size:13px;color:var(--acc);font-weight:700}
h2{margin:4px 0 4px;font-size:20px} h2 small{font-weight:500;color:var(--soft);font-size:14px;margin-left:6px}
.rel{margin:0;color:var(--soft);font-size:14px} .why{margin:6px 0 0;font-size:15px}
figure{margin:0;background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden} figure img,details img{display:block;width:100%%;height:auto}
.meta{font-size:13px;color:var(--soft);margin:8px 0 0} .meta.ok{color:var(--ok)} .meta.ng{color:var(--ng)}
details{margin-top:12px;border-top:1px solid var(--line);padding-top:10px} summary{cursor:pointer;font-weight:600;font-size:15px}
pre{white-space:pre-wrap;font-size:12.5px;line-height:1.5;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:12px;max-height:420px;overflow:auto}
button{margin-left:8px;font:inherit;font-size:12px;padding:2px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink);cursor:pointer}
.miss{padding:40px;text-align:center;color:var(--ng)}
</style></head><body><main>
<h1>%s</h1>
<p class="lead">같은 의도를 서로 다른 도식 형태로 그린 후보입니다. 형태마다 독자에게 먼저 보이는 것이 다릅니다 — 전하려는 한 문장에 가장 빨리 닿는 것을 고르세요. 각 후보의 프롬프트는 이미지 모델에 그대로 넣을 수 있습니다.</p>
%s
</main>
<script>
function cp(b){ try{ const t=b.closest('details').querySelector('pre').innerText; navigator.clipboard.writeText(t); b.textContent='복사됨'; setTimeout(()=>b.textContent='복사',1500);}catch(e){} }
</script></body></html>''' % (e(title), "".join(items))


if __name__ == "__main__":
    main()
