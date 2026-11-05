# 확장하기 — 템플릿·프리셋 추가

## 구조

```
doc-figure/
├─ SKILL.md          스킬 본체 — 무엇을 그릴지 판단
├─ references/       스키마·매핑·프리셋 사양 (읽기 전용 지식)
├─ templates/        도식 문법 11종 (HTML/CSS/JS)
├─ presets/          토큰 값 묶음 3벌
├─ scripts/          render_figure.py · selftest.sh (선택 경로)
└─ examples/         템플릿별 spec + 미리보기
```

각 층은 따로 갈아끼울 수 있다. 프리셋을 바꿔도 템플릿은 그대로고, 템플릿을 더해도 엔진은 그대로다.

## 마커 3개

템플릿은 **완성된 HTML 파일**이되, 세 자리를 비워 둔 것이다.

| 마커 | 치환되는 것 |
|---|---|
| `/*__STYLE_TOKENS__*/` | 프리셋 CSS 전문 |
| `/*__FIGURE_DATA__*/ null` | spec JSON 전문 |
| `/*__ICONS__*/ {}` | 아이콘 맵 (기본: 빈 객체) |

이 셋만 치환하면 자기완결 HTML이 된다. **파이썬 없이 손으로 해도 똑같다** — 그래서 설치 0 경로가 성립한다.

## 새 템플릿 만들기

1. 가장 가까운 기존 템플릿을 복사한다

```bash
cp templates/flow-process.html templates/my-template.html
```

2. 지켜야 할 것

- **색은 반드시 `var(--토큰)`.** 하드코딩한 색은 프리셋을 빠져나가 `mono-formal`에서 혼자 파랗게 남는다. `selftest.sh` 가 이걸 검사한다
- **캔버스 폭 1500px 고정.** 엔진이 이 폭으로 스크린샷을 뜬다
- 렌더가 끝나면 `window.__RENDER_DONE__=true`
- 텍스트는 `textContent`로 넣는다 (`innerHTML` 금지 — spec 문자열이 마크업으로 해석되면 안 된다)
- 줄바꿈(`\n`)을 받는 자리에는 `white-space:pre-line`

3. 예시 spec을 `examples/my-template.json` 에 만든다
4. 스키마를 `references/template-schemas.md` 에 적는다 — **이걸 빠뜨리면 아무도 그 템플릿을 못 쓴다**
5. 검사

```bash
bash scripts/selftest.sh
python3 scripts/render_figure.py examples/my-template.json -o /tmp/t.png --verify
```

6. **결과를 눈으로 본다.** `--verify`는 글자의 존재만 보지 겹침·이탈은 못 잡는다

## 새 프리셋 만들기

[references/preset-spec.md](../references/preset-spec.md) 참고. 요약하면:

```bash
cp presets/gov-navy.css presets/my-preset.css
# 값만 고친다. 토큰 이름·개수는 그대로
bash scripts/selftest.sh
python3 scripts/render_figure.py examples/matrix-heatmap.json --preset my-preset -o /tmp/t.png
```

`matrix-heatmap` 으로 확인하는 이유는 이 템플릿이 토큰을 가장 많이 소비하기 때문이다.

## 아이콘을 쓰고 싶다면

공개판은 아이콘을 탑재하지 않는다 — 외부 API 의존을 0으로 두기 위해서다. 직접 만든 아이콘 PNG가 있으면 디렉터리째 넘길 수 있다.

```bash
python3 scripts/render_figure.py spec.json --icons /path/to/icons -o out.png
```

`flow-process`(`steps[].icon`)와 `structure-block`(`boxes[].icon`)이 파일명(확장자 제외)으로 아이콘을 찾는다. 없으면 번호·텍스트로 안전하게 퇴화한다.

**단, 이 경로는 파이썬이 필요하다.** 아이콘을 base64로 인라인해야 하기 때문이다. 설치 0 경로에서는 아이콘이 빠지므로, 두 경로의 결과를 같게 유지하려면 아이콘을 쓰지 않는 편이 낫다.
