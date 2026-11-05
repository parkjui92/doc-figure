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
#   ⑨ board 부품 정합    — 레시피가 쓰는 아이콘이 묶음에 있는가, 레시피 10종 완비, tone 토큰 18개가 모든 프리셋에 있는가
#   (⑤ 에서 board 레시피는 배치 점검 통과 + 인상(흰 바탕·색 면적)이 기준 범위 안이어야 통과)
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
tpl = {os.path.basename(p)[:-5] for p in glob.glob('templates/*.html')} | set(RF.FORMS)
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
        board-*) if echo "$OUT" | grep -q "⚠ 인상"; then ng "$t — 인상 범위 밖"; echo "$OUT" | grep -A2 "⚠ 인상" | sed 's/^/     /'; continue; fi ;;
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
if len(recipes) < 10: print("     레시피 %d종 (10종 필요)" % len(recipes))
print("     레시피 %d종 · 아이콘 %d/%d개 사용 · tone 토큰 %d개 × 프리셋 %d벌" % (len(recipes), len(used), len(icons), len(need), len(glob.glob('presets/*.css'))))
sys.exit(1 if (bad or miss or len(recipes) < 10) else 0)
PY

echo
echo "───────────────────────────────"
printf "  통과 %d · 실패 %d\n" "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
