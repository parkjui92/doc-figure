#!/usr/bin/env bash
# doc-figure 자체검사 — 레포가 약속한 것을 실제로 지키는지 증거로 확인한다.
#
#   bash scripts/selftest.sh
#
# 검사 항목
#   ① 프리셋 토큰 정합   — 프리셋마다 토큰 '이름' 집합이 완전히 같은가
#   ② 템플릿 하드코딩 색 — 프리셋을 빠져나가는 색이 없는가
#   ③ 설치 0 경로        — 크롬 없이 자기완결 HTML이 나오는가
#   ④ 예시 스키마        — 모든 예시가 실재하는 템플릿·프리셋을 가리키는가
#   ⑤ 렌더 + 텍스트 검증 — (크롬 있을 때만) 예시 전건 렌더 후 글자 깨짐 0
#   ⑥ 자유 도식 색 규율 — freeform 예시 본문에 프리셋 밖 색이 없는가
#   ⑦ 이미지 모델 경로   — 전 예시 프롬프트 설계(과금 0) + 최신 모델 자동 선택 규칙
#   ⑧ 도식 형태 14종     — 형태마다 예시·프롬프트 구도 묘사·한국어 이름이 있는가 (빠진 형태 적발)
#   ⑨ board 부품 정합    — 레시피가 쓰는 아이콘이 묶음에 있는가, 레시피 11종 완비(v2.1 논리 흐름도 추가), tone 토큰 18개가 모든 프리셋에 있는가
#   (⑤ 에서 board 레시피는 배치 점검 통과 + 인상(흰 바탕·색 면적·진한 면)이 기준 범위 안 + 배치 권고 0 이어야 통과)
#   ⑩ board 회귀 (v2.1)   — 카드 body 배열이 그림을 멈추지 않는가, 스크립트 오류가 숨지 않는가, pill_tone, 카드 focus 가 통째로 칠해지지 않는가
#   ⑧-2 형태 14종 (v2.3)·템플릿 11종 (v2.4) 새 디자인 — 같은 사양이 viz 로 가는가, "classic": true 는 지난 모양으로 가는가
#   ⑪ viz 18종 (v2.2·v2.2.1)     — 디자인 보고서풍 구조도 7종·데이터 그래프 11종(유량도·연결도·연결망 포함)마다 예시·구도 묘사·한국어 이름이 있는가,
#                           기존 프리셋은 평면(--gloss 0·--solid 0)이고 design-report 만 켜는가, 도형보다 큰 글자를 실제로 잡는가
#   ⑫ 입체 층 도식 6종 (v2.5) — 형태마다 예시·구도 묘사·한국어 이름이 있는가, 이미지 프롬프트가 '3D 금지'와 부딪히지 않는가,
#                           칩이 판 밖으로 나간 것·이름표가 도형을 덮은 것·음수 막대를 실패(exit 4)로 잡는가
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PASS=0; FAIL=0
ok(){ printf "  \033[32m✓\033[0m %s\n" "$1"; PASS=$((PASS+1)); }
ng(){ printf "  \033[31m✗\033[0m %s\n" "$1"; FAIL=$((FAIL+1)); }

echo "── ① 프리셋 토큰 정합 ──"
python3 - <<'PY' && ok "프리셋 토큰 이름 집합 일치" || ng "프리셋 토큰 불일치"
import re, glob, os, sys
sets = {os.path.basename(p)[:-4]:
        set(re.findall(r'^\s*(--[\w-]+)\s*:', open(p, encoding='utf-8').read(), re.M))
        for p in sorted(glob.glob('presets/*.css'))}
if not sets: sys.exit("프리셋 없음")
base_name = 'gov-navy' if 'gov-navy' in sets else sorted(sets)[0]
base = sets[base_name]
bad = False
for n, s in sorted(sets.items()):
    if s != base:
        bad = True
        print("     %s: 누락 %s / 초과 %s" % (n, sorted(base-s), sorted(s-base)))
print("     %d개 토큰 × 프리셋 %d벌" % (len(base), len(sets)))
sys.exit(1 if bad else 0)
PY

echo "── ② 템플릿 하드코딩 색 ──"
LEAK=$( { grep -nEo '#[0-9A-Fa-f]{6}' templates/*.html 2>/dev/null | grep -viE '#fff|#ffffff|#000000';
          grep -nEo 'rgba?\([0-9 ,.]+\)' templates/*.html 2>/dev/null | grep -vE 'rgba?\(255, ?255, ?255'; } || true)
if [ -z "$LEAK" ]; then ok "프리셋을 빠져나가는 색 없음"; else ng "하드코딩 색 발견"; echo "$LEAK" | sed 's/^/     /'; fi

echo "── ③ 설치 0 경로 (크롬 없이 HTML) ──"
TMP=$(mktemp -d)
if python3 scripts/render_figure.py examples/org-chart.json --html-only -o "$TMP/t.html" >/dev/null 2>&1 \
   && grep -q "추진체계\|figure" "$TMP/t.html" \
   && ! grep -qE 'src="http|href="http' "$TMP/t.html"; then
  ok "자기완결 HTML 생성 (외부 요청 0)"
else ng "HTML 생성 실패 또는 외부 의존 발견"; fi

echo "── ④ 예시 스키마 ──"
python3 - <<'PY' && ok "예시 전건이 실재 템플릿·프리셋 참조" || ng "예시 참조 오류"
import json, glob, os, sys
sys.path.insert(0, 'scripts'); import render_figure as RF
tpl = {os.path.basename(p)[:-5] for p in glob.glob('templates/*.html')} | set(RF.FORMS) | set(getattr(RF, 'VIZ', [])) | set(getattr(RF, 'ISO', []))
pre = {os.path.basename(p)[:-4] for p in glob.glob('presets/*.css')}
bad = False
for p in sorted(glob.glob('examples/*.json')):
    s = json.load(open(p, encoding='utf-8'))
    t, r = s.get('template'), s.get('preset')
    if t not in tpl:      bad = True; print("     %s: 템플릿 '%s' 없음" % (p, t))
    if r and r not in pre: bad = True; print("     %s: 프리셋 '%s' 없음" % (p, r))
print("     예시 %d건 · 템플릿+도식 형태 %d종 · 프리셋 %d벌" % (len(glob.glob('examples/*.json')), len(tpl), len(pre)))
sys.exit(1 if bad else 0)
PY

echo "── ⑤ 렌더 + 텍스트 검증 ──"
CB="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ ! -x "$CB" ]; then
  echo "     크롬 없음 — 건너뜀 (설치 0 경로는 ③에서 확인됨)"
else
  for f in examples/*.json; do
    t=$(basename "$f" .json)
    OUT=$(python3 scripts/render_figure.py "$f" -o "$TMP/$t.png" --verify 2>&1); RC=$?
    if [ $RC -eq 0 ] && echo "$OUT" | grep -q "글자 깨짐 0"; then
      case "$t" in
        board-*) if echo "$OUT" | grep -q "⚠ 인상"; then ng "$t — 인상 범위 밖"; echo "$OUT" | grep -A3 "⚠ 인상" | sed 's/^/     /'; continue; fi
                 if echo "$OUT" | grep -q "⚠ 배치 권고"; then ng "$t — 배치 권고(긴 글 꺾임·focus 여러 곳·진한 띠)"; echo "$OUT" | grep -A4 "⚠ 배치 권고" | sed 's/^/     /'; continue; fi ;;
      esac
      ok "$t"
    else ng "$t"; echo "$OUT" | grep -E "✗|^   - " | head -6 | sed 's/^/     /'; fi
  done
fi
rm -rf "$TMP"

echo "── ⑥ 자유 도식 색 규율 ──"
python3 - <<'PY' && ok "freeform 예시 본문 색 누수 0" || ng "freeform 본문에 프리셋 밖 색"
import json, glob, sys
sys.path.insert(0, 'scripts'); import render_figure as RF
bad = 0
for p in glob.glob('examples/*.json'):
    s = json.load(open(p, encoding='utf-8'))
    if s.get('template') == 'freeform':
        l = RF.color_leaks(s)
        if l: bad += 1; print("     %s: %s" % (p, l))
sys.exit(1 if bad else 0)
PY

echo "── ⑦ 이미지 모델 경로 (API 호출 없음) ──"
python3 - <<'PY' && ok "전 예시 프롬프트 설계 + 모델 자동 선택 규칙" || ng "이미지 모델 경로 오류"
import json, glob, sys
sys.path.insert(0, 'scripts'); import gen_image as G, render_figure as RF
bad = 0
for p in sorted(glob.glob('examples/*.json')):
    s = json.load(open(p, encoding='utf-8'))
    for pr in ('gov-navy', 'academic-serif'):
        prompt, ts = G.build_prompt(s, pr, RF.load_preset(pr))
        miss = [t for t in ts if '"%s"' % t not in prompt]
        if miss or not ts: bad += 1; print("     %s/%s: 글자 목록 누락 %s" % (p, pr, miss[:3]))
ids = ["gpt-image-1", "gpt-image-1-mini", "gpt-image-2", "gpt-image-2-2026-04-21", "gpt-image-2.5-flare",
       "gpt-image-2.5-sunburst", "gpt-image-2.5-sunburst-2026-09-08", "chatgpt-image-latest"]
cases = [(G.pick_latest(ids), "gpt-image-2.5-sunburst"), (G.pick_latest(ids, True), "gpt-image-2.5-flare"),
         (G.pick_latest(["gpt-image-2", "gpt-image-3"]), "gpt-image-3"), (G.pick_latest(["gpt-image-1-mini"]), None)]
for got, want in cases:
    if got != want: bad += 1; print("     pick_latest: %s ≠ %s" % (got, want))
print("     예시 %d건 × 프리셋 2벌 프롬프트 · 모델 선택 %d케이스" % (len(glob.glob('examples/*.json')), len(cases)))
sys.exit(1 if bad else 0)
PY

echo "── ⑧ 도식 형태 14종 ──"
python3 - <<'PY' && ok "형태마다 예시·구도 묘사·이름 완비" || ng "형태 누락"
import sys, os
sys.path.insert(0, 'scripts'); import render_figure as RF, gen_image as G, figure_pack as P
bad = [f for f in RF.FORMS if not os.path.exists('examples/form-%s.json' % f) or f not in G.HINTS or f not in P.FORM_KO]
src = open('templates/forms.html', encoding='utf-8').read()
bad += [f for f in RF.FORMS if ("'%s'" % f not in src and (f + ',') not in src and (f + '}') not in src)]
if bad: print("     누락:", sorted(set(bad)))
print("     %d종" % len(RF.FORMS)); sys.exit(1 if bad else 0)
PY

echo "── ⑧-2 도식 형태 14종의 새 디자인 (v2.3) ──"
python3 - <<'PY' && ok "형태 14종이 새 디자인(viz)으로 가고 classic 은 지난 모양으로 감" || ng "형태 경로 오류"
import sys
sys.path.insert(0, 'scripts'); import render_figure as RF
src = open('templates/viz.html', encoding='utf-8').read()
bad = [f for f in RF.FORMS if ("'%s':" % f) not in src]
for f in RF.FORMS:
    a = RF.resolve_form({"template": f}); b = RF.resolve_form({"template": f, "classic": True})
    if a.get("template") != "viz" or a.get("viz") != f: bad.append(f + ' 기본 경로')
    if b.get("template") != "forms" or b.get("form") != f: bad.append(f + ' classic 경로')
for f in getattr(RF, 'TPL_X', []):   # v2.4 — 템플릿 11종
    a = RF.resolve_form({"template": f}); b = RF.resolve_form({"template": f, "classic": True})
    if ("'%s':" % f) not in src: bad.append(f + ' viz 에 없음')
    if a.get("template") != "viz" or a.get("viz") != f: bad.append(f + ' 기본 경로')
    if b.get("template") != f: bad.append(f + ' classic 경로')
if bad: print("     오류:", bad)
print("     형태 %d종 + 템플릿 %d종" % (len(RF.FORMS), len(getattr(RF, "TPL_X", [])))); sys.exit(1 if bad else 0)
PY
CB="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ -x "$CB" ]; then
  RT=$(mktemp -d)
  python3 - "$RT" <<'PY'
import json, sys
s = json.load(open('examples/form-pyramid.json', encoding='utf-8')); s['classic'] = True
json.dump(s, open(sys.argv[1] + '/c.json', 'w', encoding='utf-8'), ensure_ascii=False)
PY
  OUT=$(python3 scripts/render_figure.py "$RT/c.json" -o "$RT/c.png" --verify 2>&1); RC=$?
  if [ $RC -eq 0 ] && echo "$OUT" | grep -q "template=forms" && echo "$OUT" | grep -q "글자 깨짐 0"; then ok "classic: true 로 지난 모양 렌더"; else ng "classic 렌더 실패 (rc=$RC)"; fi
  python3 - "$RT" <<'PY'
import json, sys
s = json.load(open('examples/org-chart.json', encoding='utf-8')); s['classic'] = True
json.dump(s, open(sys.argv[1] + '/d.json', 'w', encoding='utf-8'), ensure_ascii=False)
PY
  OUT=$(python3 scripts/render_figure.py "$RT/d.json" -o "$RT/d.png" --verify 2>&1); RC=$?
  if [ $RC -eq 0 ] && echo "$OUT" | grep -q "template=org-chart" && echo "$OUT" | grep -q "글자 깨짐 0"; then ok "템플릿 classic: true 로 지난 모양 렌더"; else ng "템플릿 classic 렌더 실패 (rc=$RC)"; fi
  rm -rf "$RT"
fi

echo "── ⑨ board 부품 정합 ──"
python3 - <<'PY' && ok "아이콘·레시피·tone 토큰 정합" || ng "board 부품 정합 오류"
import json, glob, re, sys, os
icons = json.load(open('templates/icons/tabler-outline.json', encoding='utf-8'))
used = set()
def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'icon' and isinstance(v, str): used.add(v)
            walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
recipes = sorted(glob.glob('examples/board-*.json'))
for p in recipes: walk(json.load(open(p, encoding='utf-8')))
bad = sorted(used - set(icons))
need = ['--tone-%s%s' % (t, s) for t in ('main', 'sub', 'go', 'wait', 'stop', 'mute') for s in ('', '-tint', '-line')]
miss = [os.path.basename(p) for p in glob.glob('presets/*.css') if not all(re.search(r'%s:' % re.escape(n), open(p, encoding='utf-8').read()) for n in need)]
if bad: print("     묶음에 없는 아이콘:", bad)
if miss: print("     tone 토큰 빠진 프리셋:", miss)
if len(recipes) < 11: print("     레시피 %d종 (11종 필요)" % len(recipes))
print("     레시피 %d종 · 아이콘 %d/%d개 사용 · tone 토큰 %d개 × 프리셋 %d벌" % (len(recipes), len(used), len(icons), len(need), len(glob.glob('presets/*.css'))))
sys.exit(1 if (bad or miss or len(recipes) < 11) else 0)
PY

echo "── ⑩ board 회귀 (v2.1) ──"
CB="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ ! -x "$CB" ]; then
  echo "     크롬 없음 — 건너뜀"
else
  RT=$(mktemp -d)
  # 카드 body 배열 — v2.1 전에는 그림 전체가 멈췄다(2026-11-12 다른 작업 세션의 그림에서 발견)
  cat > "$RT/a.json" <<'J'
{"template":"board","title":"회귀","body":[{"row":[{"head":"카드","pill":"표식","pill_tone":"wait","body":[{"pill":"알약","tone":"wait"},{"items":["항목 하나","항목 둘"]}]},{"title":"옆 카드","text":"정상","focus":true}]}],"source":"시험"}
J
  OUT=$(python3 scripts/render_figure.py "$RT/a.json" -o "$RT/a.png" --verify --keep-html 2>&1); RC=$?
  if [ $RC -eq 0 ] && echo "$OUT" | grep -q "글자 깨짐 0"; then ok "카드 body 배열·pill_tone 렌더"; else ng "카드 body 배열 렌더"; echo "$OUT" | grep -E "✗|^   - " | head -4 | sed 's/^/     /'; fi
  H=$(echo "$OUT" | sed -n 's/^\[doc-figure\] HTML: //p')
  if [ -n "$H" ] && grep -q "pillin.toned" "$H" && grep -q "card.focus { --card-bg: var(--tone-main-tint)" "$H"; then ok "pill_tone·가벼운 카드 focus 규칙 탑재"; else ng "pill_tone·카드 focus 규칙 없음"; fi
  [ -n "$H" ] && rm -f "$H"
  # 스크립트 오류는 숨지 않고 원인과 함께 실패해야 한다
  cat > "$RT/b.json" <<'J'
{"template":"board","title":"오류 시험","body":[{"row":[{"title":"카드","fill":{"bad":1}}]}]}
J
  OUT=$(python3 scripts/render_figure.py "$RT/b.json" -o "$RT/b.png" --verify 2>&1); RC=$?
  if [ $RC -eq 4 ] && echo "$OUT" | grep -q "board 오류"; then ok "스크립트 오류를 원인과 함께 실패(exit 4)"; else ng "스크립트 오류가 숨음 (rc=$RC)"; fi
  rm -rf "$RT"
fi

echo "── ⑪ viz 18종 (v2.2·v2.2.1) ──"
python3 - <<'PY' && ok "형태마다 예시·구도 묘사·이름 완비, 그라데이션 스위치는 design-report 만" || ng "viz 형태·스위치 오류"
import sys, os, re, glob
sys.path.insert(0, 'scripts'); import render_figure as RF, gen_image as G, figure_pack as P
src = open('templates/viz.html', encoding='utf-8').read()
bad = [f for f in RF.VIZ if not os.path.exists('examples/viz-%s.json' % f) or f not in G.HINTS or f not in P.FORM_KO or ("'%s'" % f) not in src]
on = []
for p in sorted(glob.glob('presets/*.css')):
    c = open(p, encoding='utf-8').read()
    i = c.find(':root {'); m_ = re.search(r'^\}\s*$', c[i:], re.M) if i >= 0 else None
    c = c[i:i + m_.start()] if m_ else ''   # 토큰은 :root 블록 안에 있어야 한다 (파생 프리셋은 :root 뒤에 규칙이 더 있다)
    g = re.search(r'^\s*--gloss:\s*([0-9.]+)', c, re.M); s_ = re.search(r'^\s*--solid:\s*([0-9.]+)', c, re.M)
    if not g or not s_: bad.append(os.path.basename(p) + ' 토큰 없음'); continue
    if float(g.group(1)) > 0 or float(s_.group(1)) > 0: on.append(os.path.basename(p)[:-4])
if on != ['design-report']: bad.append('그라데이션·입체가 켜진 프리셋: %s (design-report 만 허용)' % on)
if bad: print("     누락·오류:", bad)
print("     구조도 %d종 + 그래프 %d종 · 켜진 프리셋 %s" % (len(RF.VIZ_SHAPES), len(RF.VIZ_CHARTS), on)); sys.exit(1 if bad else 0)
PY
CB="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ ! -x "$CB" ]; then
  echo "     크롬 없음 — 건너뜀"
else
  RT=$(mktemp -d)
  # 도형보다 긴 글은 실패해야 한다
  cat > "$RT/a.json" <<'J'
{"template":"ribbon-list","title":"넘침 시험","first_width":300,"items":[{"text":"이 띠보다 훨씬 긴 글을 넣으면 도형을 넘는다는 것을 점검이 잡아야 한다"},{"text":"둘째"}]}
J
  OUT=$(python3 scripts/render_figure.py "$RT/a.json" -o "$RT/a.png" --verify 2>&1); RC=$?
  if [ $RC -eq 4 ] && echo "$OUT" | grep -q "도형보다 큼"; then ok "도형보다 큰 글자를 실패로 잡음(exit 4)"; else ng "넘친 글자를 못 잡음 (rc=$RC)"; fi
  cat > "$RT/b.json" <<'J'
{"template":"slope","title":"오류 시험","from_label":"전","to_label":"후","items":"목록이 아님"}
J
  OUT=$(python3 scripts/render_figure.py "$RT/b.json" -o "$RT/b.png" --verify 2>&1); RC=$?
  if [ $RC -eq 4 ] && echo "$OUT" | grep -q "스크립트 오류"; then ok "viz 스크립트 오류를 원인과 함께 실패(exit 4)"; else ng "viz 스크립트 오류가 숨음 (rc=$RC)"; fi
  # 같은 사양을 house 로 그리면 그라데이션·입체가 꺼져 있어야 한다 (평면)
  python3 scripts/render_figure.py examples/viz-funnel-stack.json --preset house --html-only -o "$RT/h.html" >/dev/null 2>&1
  if grep -q -- "--gloss: 0;" "$RT/h.html" && grep -q -- "--solid: 0;" "$RT/h.html"; then ok "house 프리셋에서는 평면(그라데이션·입체 꺼짐)"; else ng "house 에서 그라데이션 스위치가 켜짐"; fi
  rm -rf "$RT"
fi

echo "── ⑫ 입체 층 도식 6종 (v2.5) ──"
python3 - <<'PY2' && ok "형태마다 예시·구도 묘사·이름 완비, 프롬프트가 투영을 막지 않음" || ng "입체 형태 누락·프롬프트 충돌"
import sys, os, json
sys.path.insert(0, 'scripts'); import render_figure as RF, gen_image as G, figure_pack as P
src = open('templates/viz.html', encoding='utf-8').read()
bad = [f for f in RF.ISO if not os.path.exists('examples/%s.json' % f) or f not in G.HINTS or f not in P.FORM_KO or ("'%s'" % f) not in src]
for f in RF.ISO:
    if RF.resolve_form({"template": f}).get("template") != "viz": bad.append(f + ' 경로')
    if os.path.exists('examples/%s.json' % f):
        pr, _ = G.build_prompt(json.load(open('examples/%s.json' % f, encoding='utf-8')), 'house', RF.load_preset('house'))
        if 'AVOID: 3D, isometric' in pr or 'oblique' not in pr: bad.append(f + ' 프롬프트')
if bad: print("     누락·오류:", bad)
print("     %d종" % len(RF.ISO)); sys.exit(1 if bad else 0)
PY2
CB="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ ! -x "$CB" ]; then
  echo "     크롬 없음 — 건너뜀"
else
  RT=$(mktemp -d)
  # 오른쪽 판이 좁아 칩이 판 밖으로 나가면 실패해야 한다
  cat > "$RT/a.json" <<'J'
{"template":"iso-compare","split":0.6,"left":{"title":"왼쪽","pillars":[{"label":"가"},{"label":"나"}]},"right":{"title":"오른쪽","layers":[{"title":"위층","chips":["긴 칩 글자 하나","긴 칩 글자 둘","긴 칩 글자 셋"]},{"title":"아래층","chips":["기반"]}]}}
J
  OUT=$(python3 scripts/render_figure.py "$RT/a.json" -o "$RT/a.png" --verify 2>&1); RC=$?
  if [ $RC -eq 4 ] && echo "$OUT" | grep -q "칩이 판 밖"; then ok "칩이 판 밖으로 나간 것을 실패로 잡음(exit 4)"; else ng "판 밖 칩을 못 잡음 (rc=$RC)"; fi
  # 긴 기둥 이름표가 옆 기둥을 덮으면 실패해야 한다
  cat > "$RT/b.json" <<'J'
{"template":"iso-pillars","base":{"title":"판"},"pillars":[{"label":"아주 긴 기둥 이름표 하나"},{"label":"아주 긴 기둥 이름표 둘"},{"label":"셋"},{"label":"넷"},{"label":"다섯"},{"label":"여섯"},{"label":"일곱"},{"label":"여덟"},{"label":"아홉"},{"label":"열"}]}
J
  OUT=$(python3 scripts/render_figure.py "$RT/b.json" -o "$RT/b.png" --verify 2>&1); RC=$?
  if [ $RC -eq 4 ] && echo "$OUT" | grep -q "이름표가 도형을 덮음"; then ok "이름표가 도형을 덮은 것을 실패로 잡음(exit 4)"; else ng "도형을 덮은 이름표를 못 잡음 (rc=$RC)"; fi
  cat > "$RT/c.json" <<'J'
{"template":"iso-bars","items":[{"label":"가","value":-3},{"label":"나","value":5}]}
J
  OUT=$(python3 scripts/render_figure.py "$RT/c.json" -o "$RT/c.png" --verify 2>&1); RC=$?
  if [ $RC -eq 4 ] && echo "$OUT" | grep -q "0 이상인 값만"; then ok "입체 막대의 음수 값을 실패로 잡음(exit 4)"; else ng "음수 입체 막대를 못 잡음 (rc=$RC)"; fi
  rm -rf "$RT"
fi

echo
echo "───────────────────────────────"
printf "  통과 %d · 실패 %d\n" "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
