# board — 조립형 도식 사양

`"template": "board"`. 내용에 맞춰 배치를 새로 짠다. 행(`row`)·열(`col`)·묶음(`group`) 안에 부품을 넣고, `id`로 화살표를 잇는다. 국내 공공 도식에서 잰 시각 문법(두 층 채움·왼쪽 이름표 열·층마다 바뀌는 격자·뜻 있는 색)을 부품으로 옮긴 것이다. 근거는 [benchmark-kr-2026.md](benchmark-kr-2026.md).

레시피 10종이 `examples/board-*.json`에 있다. **새 그림은 가장 가까운 레시피를 복사해 고친다.**

| 레시피 | 관계 | 이런 그림 |
|---|---|---|
| `board-vision-system` | 목표 분해 | 비전 → 목표(지표) → 전략 열 → 기반 |
| `board-governance` | 주체 간 역할 | 추진체계도 — 주관·참여·수요·자문, 화살표마다 주고받는 것 |
| `board-process-tabs` | 순서 + 단계별 기준 | 번호 탭 단계 카드(아이콘·요약·목록) + 아래 지표·원칙 + 결과 칩 |
| `board-roadmap` | 과업 × 연차 | 연차 쉐브론 + 과업 행, 도달 상태만 진하게 |
| `board-transition` | 전환 | 현재 상황(회색) → 본 연구가 만드는 변화(남색) + 기대효과 띠 |
| `board-candidate-selection` | 수렴 → 판정 → 분기 | 근거 세 갈래 → 검토 항목 → 세 갈래 결과 → 전문기관 띠 |
| `board-review-structure` | 병렬 검토 + 공통 관문 | 전제 띠 → 카드 3열 → 주황 횡단 점검 → 결과 띠 |
| `board-research-framework` | 입력 → 처리 → 산출 | 분석틀 — 입력 자료 · 분석 단계 · 산출물 + 정책 활용 띠 |
| `board-layered-architecture` | 계층 구성 | 왼쪽 계층 이름표 + 가로 카드 |
| `board-ops-flow` | 판정 있는 운영 흐름 + 되먹임 | 시간 띠, 묶음 안 미니 매트릭스, 판단 마름모, 점선 탈락, 결과 띠, 범례 |

## 맨 위 필드

| 필드 | 뜻 |
|---|---|
| `header` | `headline`(머리말 + 굵은 결론형 제목, 왼쪽 색 막대) · `bar`(남색 막대에 "그림 N │ 제목") · `plain`(왼쪽 제목 + 부제) · `center` · `none`(캡션은 문서 문단이 맡을 때). 생략하면 `kicker`→headline, `fignum`→bar, `title`→plain |
| `kicker` · `title` · `subtitle` | 머리말 · 제목(결론형 문장 권장) · 부제 |
| `fignum` | `bar` 머리의 "그림 3" |
| `tag` | 오른쪽 위 주황 꼬리표 — "설계 예시 · 실제 조사 결과 아님" |
| `caption` | 그림 위 가운데 캡션 줄(보고서식) |
| `body` | 부품 목록 — 위에서 아래로 쌓인다 |
| `gap` | 본문 부품 사이 간격(px, 기본 18) |
| `links` | 화살표 목록 (아래) |
| `legend` | 범례 `[{tone, label, dash?, swatch?}]` — 오른쪽 아래 |
| `note` · `footnote` · `source` | 아래 왼쪽 주석 · "주:" · "자료:" |
| `width` | 그림 폭(기본 1500, 최대 1800 권장) |
| `font_scale` | 글자 배율(기본 1). 0.9 미만은 쓰지 않는다 — 인쇄에서 흐려진다 |
| `lane_r` · `lane_l` | 오른쪽·왼쪽에 되돌림 화살표가 지나갈 빈 차선(px) |
| `intent` | `{message, relation, why}` — 그리지 않음. 이미지 프롬프트 PURPOSE 절 |

## 배치

| 부품 | 필드 |
|---|---|
| `{"row": [...]}` | 가로로 나란히. `widths`(비율 또는 px), 자식의 `w`(비율, 20 초과면 px, `"auto"`), `gap`, `align`(center·start·end), `join`(arrow·chevron·plus·eq·none, 또는 자식 사이마다 배열) |
| `{"col": [...]}` | 세로로 쌓기. `gap`, `justify`(center·between), `join` |
| `{"group": "제목", "body": [...]}` | 머리띠 + 옅은 바탕 패널. `group_sub`, `tone`, `style`(soft=옅은 머리·bare=틀 없음·dash), `head_align`(left), `gap`, `pad` |
| `{"spacer": 20}` | 빈칸. 행 안에서 `w`를 주면 비율로 자리만 차지 |

모든 부품 공통: `id`(화살표 끝점), `w`, `h`(최소 높이), `tone`, `focus`(진하게 칠해 '제목이 말하는 그것'으로), `indent`·`indent_r`(좌우 들여쓰기 — 화살표 길을 비울 때).

## 부품

| 부품 | 필드 |
|---|---|
| 카드 (기본) | `title` · `sub`(문자열/배열) · `items`(글머리 목록) · `text` · `icon` · `num` · `pill`(카드 안 회색 요약줄) · `value`+`unit` · `kpi` · `body`(안에 부품) |
| | `head`(머리띠 제목) + `head_sub` · `head_style: soft` · `num`과 함께 쓰면 번호 원이 띠 왼쪽 위에 걸린다(`num_style: inline`이면 띠 안) |
| | `fill`: white(기본)·tint(옅은 바탕)·panel·solid(진한 면)·dash(점선 — 탈락·미통과) |
| | `accent`: left(왼쪽 색 막대)·top · `align: center` · `valign: middle` · `layout`: side(아이콘 왼쪽·글 오른쪽)·stack(아이콘 위) |
| | `bullet`: dot(기본)·check·num·dash·none · `tight` |
| `kpi` | `{"from":"52","from_at":"'25","to":"70","to_at":"'30","unit":"점"}` — 기준값 ➜ 목표값, 목표값이 가장 크다 |
| `{"band": "문장"}` | 전폭 띠. `sub`, `label`(왼쪽 진한 이름표) + `icon` + `label_w`, `style`(soft·line·plain), `align: left`, `body`(띠 안에 부품 — `band: ""`) |
| `{"pill": "글"}` | 알약. `style: soft`, `shape: square`, `inline` |
| `{"steps": [...]}` | 쉐브론 단계. 항목은 문자열 또는 `{title, sub, on, tone, id}`. `on`(진하게 칠할 단계 번호, 0부터), `style: solid` |
| `{"chips": [...]}` | 칩 줄. 항목은 문자열 또는 `{text, icon, tone}`. `label` + `label_en`(왼쪽 진한 이름표), `check`(✓), `fill`(폭 균등), `shape: square` |
| `{"diamond": "시장이\n열렸나?"}` | 판단 마름모. `size_w`·`size_h`, `tone`(기본 go) |
| `{"timeline": [...]}` | 시간 띠. `[{label, sub, tone, w, mark}]` — 구간 길이는 `w` 비율 |
| `{"matrix": {...}}` | 미니 매트릭스 `{cols, rows, cells}` — 1=점, 문자열=값 |
| `{"kv": [["키","값"], ...]}` | 키-값 행. `key_w` |
| `{"text": "..."}` | 글. `size`(s·l), `bold`, `align`, `tone` |
| `{"icon": "database", "size": 48}` | 아이콘만 |

## 화살표 `links`

```json
{"from": "a", "to": "b", "tone": "go", "label": "예", "dash": true}
```

| 필드 | 뜻 |
|---|---|
| `from` · `to` | 부품 `id` (steps 항목의 `id`도 된다) |
| `tone` | 색(기본 sub) — 범례와 같은 뜻으로 |
| `route` | elbow(기본, 직교) · straight · curve |
| `from_side` · `to_side` | top·bottom·left·right. 생략하면 상대 위치로 정한다 |
| `offset` | 같은 두 상자 사이 왕복 화살표를 나란히 띄울 때(px) |
| `from_x`·`to_x`·`from_y`·`to_y` | 변 위의 위치(0~1). 생략하면 겹치는 구간 가운데로 곧게 |
| `via` | 꺾이는 위치(px) 또는 `"right"`·`"left"`(여백 차선 — `lane_r`·`lane_l`과 함께) |
| `dash` · `both` · `head:false` · `width` | 점선 · 양방향 · 화살촉 없음 · 굵기 |
| `label` · `label_side` · `label_at` · `label_dx`·`label_dy` | 이름표. 화살표가 이름표보다 짧으면 자동으로 옆(세로선)·위(가로선)로 비켜 놓는다 |

화살표는 **관계가 있는 곳에만** 쓴다. 이웃한 단계를 잇는 것만이면 `join`이 낫다(정렬이 깨지지 않는다).

## 뜻으로 고르는 색 `tone`

| tone | 별칭 | 뜻 | house 값 |
|---|---|---|---|
| `main` | navy | 본체·진행·핵심 | `#16275C` |
| `sub` | blue | 보조·두 번째 주체 | `#3D5BA9` |
| `go` | teal, green | 산출·통과·투입·환류 | `#197D86` |
| `wait` | amber, orange | 주의·대기·예시·횡단 점검 | `#B77718` |
| `stop` | red | 탈락·제약·미통과 (점선 상자와 함께) | `#A84945` |
| `mute` | gray | 현재·기존·관찰 대상·비교 기준 | `#6B778C` |

한 그림에서 같은 색은 같은 뜻이다. 색을 셋 넘게 쓰면 범례(`legend`)를 단다.

## 아이콘

`templates/icons/tabler-outline.json` — Tabler Icons(MIT, `LICENSE-tabler.txt`) 136개. 이름 목록은 `python3 -c "import json;print(sorted(json.load(open('templates/icons/tabler-outline.json'))))"`. 자주 쓰는 것: database · users · user-check · building · building-bank · school · search · zoom-check · chart-bar · trending-up · report-analytics · file-text · clipboard-check · checklist · settings · adjustments-horizontal · shield-check · scale · gavel · target · bulb · rocket · link · refresh · route · sitemap · stack-2 · world · calendar · flag · award · binoculars · alert-triangle.

규칙: 카드당 하나, 같은 세트, tone 색. 범주를 알아보게 할 때만 쓴다 — 빽빽한 흐름도에는 넣지 않는다. 없는 이름을 쓰면 `--verify`가 실패한다.

## 점검

`render_figure.py <spec> --verify`

1. spec 글자가 전부 그려졌는가
2. **배치** — 글자 넘침 · 그림 밖 이탈 · 글자 15.5px 미만 · 화살표가 다른 상자를 관통 · 이름표가 상자를 덮음 → 하나라도 있으면 실패(exit 4)
3. **인상** — 흰 바탕·색 면적을 잘 그린 공공 도식 57장 중앙값(60%·17%)과 비교, 흰 바탕 85% 초과·색 6% 미만·38% 초과면 경고

통과해도 눈으로 본다. 특히 같은 크기 상자가 기계적으로 늘어서지 않았는지, 진한 면이 '제목이 말하는 그것'에 가 있는지.
