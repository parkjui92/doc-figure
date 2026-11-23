# viz 사양 — 디자인 보고서풍 구조도 6종 + 데이터 그래프 9종 (v2.2)

해외 보고서 벤치마크([benchmark-intl-2026.md](benchmark-intl-2026.md))에서 반복해 나온 형태 가운데 board·forms 로 그릴 수 없던 것을 `templates/viz.html` 한 파일이 그린다. spec 의 `"template"` 에 형태 이름을 바로 쓴다.

```bash
python3 scripts/render_figure.py examples/viz-funnel-stack.json -o out.png --verify
python3 scripts/render_figure.py examples/viz-slope.json --preset house -o out.png --verify   # 같은 사양, 평면
```

## 언제 이 경로로 가나

| 요청 | 경로 |
|---|---|
| "디자인 보고서처럼 · 유명 리포트처럼 · 발간물처럼 · 인포그래픽처럼" | viz 구조도 + 프리셋 `design-report` |
| "그래프로 · 차트로 · 수치를 그림으로 · 추이·순위·격차를 보여 줘" | viz 데이터 그래프 (프리셋은 문서에 맞춰 `house` 또는 `design-report`) |
| 체계도·절차·로드맵처럼 상자에 글이 여러 줄 들어가는 그림 | 종전대로 `board` (기본값 `house`) |

`house`·`house-report` 의 금지 규칙(그라데이션·입체 금지)은 그대로다. viz 형태를 `house` 로 그리면 평면으로 나온다. 그라데이션과 타원 테는 `design-report` 프리셋에서만 켜진다(토큰 `--gloss`·`--solid`).

## 공통 키

| 키 | 뜻 |
|---|---|
| `title` | 결론을 말하는 한 문장(권장). 그림 위 왼쪽 |
| `subtitle` · `takeaway` | 부제 / 그림 위에 한 줄로 두는 핵심 문장(왼쪽 주황 막대) |
| `conclusion` | 그림 바로 아래 색 글씨 결론 한두 줄. 제목을 `<그림 n>` 명사구로 둬야 하는 문서에서 결론을 적는 자리(IEA 보고서 방식) |
| `unit` | 단위. 그래프 위 왼쪽에 `(단위: …)` 로 적는다 |
| `source` · `footnote` · `caption` | 자료 줄 · 주 · 그림 번호와 제목 |
| `preset` | 기본 `house`. 디자인 보고서풍은 `design-report` |
| `tone` | 색의 뜻 — `main` 본체 · `sub` 보조 · `go` 산출·통과 · `wait` 강조·주의 · `stop` 제약 · `mute` 기존·비교 기준 |
| `highlight` | 제목이 말하는 그 한 항목. 그래프에서는 이 항목만 색을 쓰고 나머지는 회색 |
| `decimals` | 수치 소수 자릿수 |
| `print_cm` | 문서에 넣을 폭(기본 16). 글자 크기 점검의 기준 |

글자 크기는 프리셋과 무관하게 고정이다(16cm 폭에 넣을 때 본문 약 8.5pt, 가장 작은 글자 7pt 이상). 글이 길면 글자를 줄이지 않고 글을 줄인다.

## 구조도 6종

### funnel-stack — 쌓은 깔때기
언제: 후보를 단계마다 줄여 가는 절차(수집 → 선별 → 진단 → 확정). 모양이 하는 주장: **단계를 지날수록 수가 줄어든다.** 줄지 않는 절차에 쓰지 않는다.

```json
{"template":"funnel-stack","preset":"design-report","title":"…","numbered":true,
 "stages":[
  {"name":"후보 기술 수집","sub":"기술분류체계 기준","core":"기술 후보 600건",
   "desc":"논문·특허·과제 자료에서 분야별 후보를 수집함",
   "limit":{"tag":"한계","text":"자료에 없는 신생 분야는 설문으로 보완"},
   "next":{"text":"논문 인용 추이 분석, 전문가 의견 수렴","desc":"…"}},
  {"name":"지원 대상 확정","core":"지원 과제 3개","desc":"…"}]}
```
- 가로 옅은 띠 위에 왼쪽 이름(`name`·`sub`), 가운데 깔때기 안 핵심어(`core`·`core_sub`), 오른쪽 설명(`desc` 문자열 또는 배열)
- `next` — 이 단계의 결과를 다음 단계로 넘기는 활동. 두 깔때기 사이 흰 바탕에 적는다
- `limit` — 주황 꼬리표와 한 줄. 그 단계의 한계·유의점
- `numbered: true` 일 때만 옅은 큰 번호. 본문이 단계에 번호를 매겼을 때만 쓴다
- 단계는 3~5개. `core` 는 마지막 단계에서 칸이 좁으므로 8자 안팎. `tone` 을 주지 않으면 첫 단계 `go`, 마지막 `wait`
- `top_width`(기본 520)·`bottom_width`(기본 170)

### growing-circles — 커지는 원
언제: 세대·단계가 올라가며 범위나 규모가 커진 변천. 모양이 하는 주장: **뒤로 갈수록 커졌고, 지금(마지막)이 가장 크다.** 크기가 뜻을 갖지 않으면 쓰지 않는다.

```json
{"template":"growing-circles","items":[
  {"label":"시범","sub":"2018","note":"3개 기관이 참여해 절차를 시험함"},
  {"label":"고도화","sub":"2026","note_title":"현재 단계","note":"민간 자료와 연계하고 평가에 활용함"}]}
```
- 3~6개. `label` 은 6자 이내(첫 원이 작다). 메모는 원 옆에 왼쪽 위·오른쪽 아래로 번갈아 붙는다
- 마지막 원(또는 `highlight: true`)만 강조색. `tone`(기본 `go`)·`highlight_tone`(기본 `wait`)·`r_min`·`r_max`·`angle`·`note_w`

### circle-chain — 겹치는 원 사슬
언제: 서로 맞물린 2~5개 기준·조건을 함께 본다는 것. 모양이 하는 주장: **이웃한 것끼리 겹친다(따로 떨어진 기준이 아니다).**

```json
{"template":"circle-chain","head":"성숙도 진단","from":{"title":"기술 후보","sub":"분류체계 기준"},
 "items":[{"title":"기술 성숙도","desc":"시제품·실증 단계","note":"연구실 검증에서 현장 실증까지"}, …],
 "to":{"title":"지원 대상 선정","sub":"세 조건 충족"}}
```
- `from`·`to` 는 양 끝 알약(투입·결과), 없어도 된다. `note` 는 원 아래 한두 줄. 원 안 `title` 6자·`desc` 9자 안팎

### ring-core — 순환 고리와 핵심어
언제: 가운데 핵심어를 두고 네 갈래가 돌아가는 구조, 왼쪽에 문제·오른쪽에 목표. 모양이 하는 주장: **되풀이해 돈다.** 되먹임이 없으면 쓰지 않는다([form-catalog.md](form-catalog.md) 「모양이 하는 주장」).

```json
{"template":"ring-core","core":{"title":"자료\n순환"},
 "left":{"tag":"병목","text":"기관별 형식 차이"},"right":{"tag":"목표","text":"한 번 입력, 여러 곳 활용"},
 "panels":[{"num":1,"title":"수집","items":["…","…"]},{"num":2,"title":"정제","tone":"main","items":["…"]},
           {"num":4,"title":"환류","tone":"main","items":["…"]},{"num":3,"title":"활용","items":["…"]}]}
```
- `panels` 순서는 왼쪽 위 · 오른쪽 위 · 왼쪽 아래 · 오른쪽 아래. 0개(고리와 띠만)·2개·4개
- 핵심어는 두 줄 8자 이내. 패널 항목은 한 줄 22자 안팎

### ribbon-list — 꼬리표 목록
언제: 정의의 조건 2~4개, 단계 이름처럼 짧은 문장을 띠로 쌓아 보일 때. 아래로 갈수록 띠가 길어지고 마지막 띠가 둘째 색이다.

```json
{"template":"ribbon-list","numbered":true,"items":[{"text":"연구 성과가 이미 축적되어 있고"},{"text":"…","tone":"go"}]}
```
- 진한 면이 넓다. 한 문서에 한두 번, 정의·요건 같은 자리에만 쓴다

### stat-strip — 큰 숫자 묶음
언제: 수치 2~5개가 곧 메시지일 때(설문 응답률, 핵심 지표). 모양이 하는 주장: **이 숫자만 기억하면 된다.** 숫자마다 무엇의 숫자인지(`label`)와 기준(`note`)을 반드시 붙인다.

```json
{"template":"stat-strip","items":[
  {"value":"84","unit":"%","share":0.84,"label":"자료 연계가 필요하다","note":"응답 기업 1,200개 기준","highlight":true},
  {"value":"5.2","unit":"개월","label":"연계에 걸린 기간","note":"신청에서 제공까지 평균"}]}
```
- `value` 는 글자 그대로 적는다(문자열). `share`(0~1)를 주면 숫자 아래 가는 비율 막대. 강조 칸 하나만 옅은 바탕과 강조색

## 데이터 그래프 9종

공통 원칙(벤치마크 근거는 benchmark-intl-2026.md): 제목은 결론 한 문장 · 색은 강조 하나와 회색 · 범례보다 직접 이름표 · 눈금선은 옅게, 축 선은 0 기준선만 · 값은 막대 끝·선 끝에 적는다 · 3D·그림자·무지개 색을 쓰지 않는다.

| 형태 | 언제 쓰는가 | 모양이 하는 주장 | 핵심 키 |
|---|---|---|---|
| `bar-highlight` 강조 막대 | 순위·크기 비교에서 한 항목을 짚을 때 | 이 항목이 다른 것보다 얼마나 크다/작다 | `items[{label,value,highlight}]` · `ref{value,label}` 기준선 · `orient:"v"` 세로 |
| `bar-line` 막대+선 결합 | 양(막대)과 비율·증가율(선)을 한 시계열에 | 양은 이렇게 움직였고 비율은 다르게 움직였다 | `x[]` · `bars{label,unit,values}` · `line{label,unit,values}` · `highlight_x` |
| `line-highlight` 강조 선 | 여러 계열 가운데 하나의 추이를 짚을 때 | 이 계열만 다르게 움직였다 | `x[]` · `series[{label,values,highlight,tone}]` |
| `slope` 기울기 | 두 시점 사이 순위·수준 변화 | 누가 올랐고 누가 내렸다, 교차했다 | `from_label` · `to_label` · `items[{label,from,to,highlight}]` |
| `dumbbell` 아령 | 항목마다 두 값(계획·실적, 남·여, 전·후)의 격차 | 격차가 어디서 가장 큰가 | `a_label` · `b_label` · `rows[{label,a,b,highlight}]` |
| `range-bar` 범위 막대 | 항목마다 최소~최대 범위와 중앙값 | 범위가 어디가 넓고 어디에 몰려 있는가 | `rows[{label,min,max,mid}]` · `range_label` · `mid_label` |
| `bubble-compare` 비례 원 | 2~6개 양을 크기로 견줄 때(차이가 클 때) | 이것이 저것의 몇 배다 | `items[{label,value,note,highlight}]` — 넓이가 값에 비례 |
| `small-multiples` 작은 그래프 묶음 | 6~12개 분야·지역의 추이를 같은 눈금으로 | 어느 것만 다르게 움직이는가 | `x[]` · `panels[{title,values,highlight}]` · `cols` · `kind:"bar"` |
| `stacked-share` 구성비 누적 막대 | 집단별 구성비 비교 | 집단에 따라 구성이 이렇게 달라진다 | `series[{label}]` · `rows[{label,values,highlight}]` · `normalize:false` 면 합계 비교 |

세부:
- `bar-highlight` — 값이 큰 순서로 넣는다(자동 정렬하지 않는다 — 순서가 뜻일 수 있다). 12개 이하. 음수는 0 기준선 왼쪽으로 그린다. `highlight` 가 하나도 없으면 값 순서로만 말하는 단색 막대가 된다(`tone` 기본 `sub`)
- `bar-line` — 왼쪽 눈금은 막대, 선은 눈금 없이 점 위에 값을 적는다. 선 값은 `line_decimals`. 가로축 14칸 이하
- `line-highlight` — 계열 6개 이하면 모두 끝에 이름표, 넘으면 강조 계열만(다른 계열은 `label_end: true` 로 지정). `zero: false` 면 세로축을 0 에서 시작하지 않는다
- `slope` — 이름표가 겹치면 자동으로 벌린다. 항목 8개 이하
- `dumbbell`·`range-bar` — 눈금은 위쪽. `zero: true` 면 0 에서 시작. 강조 행은 옅은 띠
- `bubble-compare` — 값 차이가 작으면(최대/최소 2배 미만) 원보다 막대가 정확하다. 넓이로 비교하므로 정밀한 비교에는 쓰지 않는다
- `small-multiples` — 기본은 모든 칸이 같은 세로 눈금(`shared_y: false` 로 끌 수 있으나 그러면 칸끼리 높이를 견줄 수 없다). 가로축은 처음과 끝만 적는다
- `stacked-share` — 계열은 한 색의 농도 단계로 칠한다(순서가 있는 구성). 서로 다른 범주면 `series[].tone` 으로 지정하되 넷을 넘기지 않는다

## 유량·연결 3종 (v2.2.1)

해외 보고서의 유량·연결 그림(WEF 위험 연결 지도, 영국 GO-Science 원인–추세–부문 연결도 등)에서 가져왔다. **선이 많아지면 읽을 수 없다** — 띠·선은 20개 안팎까지, 제목이 말하는 한 갈래만 `highlight` 로 색을 준다.

### sankey — 유량도
언제: 무엇이 어디서 어디로 얼마나 가는가(인력 이동, 예산 배분, 단계별 전환). 모양이 하는 주장: **띠의 굵기만큼 흘러간다.** 양이 없는 연결에 쓰지 않는다(그때는 `link-map`).

```json
{"template":"sankey","unit":"명","col_titles":["학위 취득 기관","첫 취업 부문","취업 지역"],
 "nodes":[{"id":"u1","label":"수도권 대학","col":0},{"id":"s1","label":"기업","col":1,"highlight":true},{"id":"r1","label":"수도권","col":2}],
 "links":[{"from":"u1","to":"s1","value":520},{"from":"s1","to":"r1","value":690}]}
```
- 열은 `col`(0부터) 2~4개, 열 안 순서는 `nodes` 에 적은 순서(큰 것부터 넣는다). 마디 합계는 들어오는 값과 나가는 값 중 큰 쪽이고 이름 옆에 적힌다
- `highlight` 는 마디나 띠 하나에. 강조가 있으면 나머지 띠는 회색이 된다. 강조가 없으면 띠는 출발 마디의 색(`tone`, 기본 `sub`)
- 들어온 합과 나간 합이 다른 마디는 그 차이만큼 띠가 비어 보인다 — 수치가 맞는지 먼저 확인한다(`--verify` 는 합계를 검산하지 않는다)

### link-map — 연결도 (열 사이 연결)
언제: 원인–과제–분야처럼 두세 묶음 사이에 무엇이 무엇에 닿는지. 모양이 하는 주장: **이것이 저것에 이어진다(양은 말하지 않는다).** 선 굵기는 모두 같다.

```json
{"template":"link-map","columns":[
  {"title":"여건 변화","items":[{"id":"d1","label":"인구 구조 변화","tone":"wait"},{"id":"d2","label":"기술 발전","tone":"go"}]},
  {"title":"정책 과제","items":[{"id":"t1","label":"지역 대학 정원 조정"},{"id":"t2","label":"평생 학습 지원"}]},
  {"title":"영향 분야","items":[{"id":"a1","label":"교육","tone":"sub"}]}],
 "links":[{"from":"d1","to":"t1"},{"from":"d2","to":"t2"},{"from":"t1","to":"a1"},{"from":"t2","to":"a1"}]}
```
- 열 2~3개. 항목이 5개 이하인 열은 큰 상자, 넘는 열은 옅은 작은 상자가 된다. 칠한 큰 상자는 첫 열만이고(진한 칠은 한 곳) 다른 열의 큰 상자는 옅은 바탕에 색 테두리다 — 열에 `"fill": "solid"` 를 주면 칠한다. 선은 큰 상자의 색을 따른다
- 가운데 열 12개, 선 24개 안팎까지. 넘으면 선이 엉켜 읽을 수 없다 — 묶거나 두 장으로 나눈다

### network — 연결망
언제: 여러 대상이 서로 얼마나 이어져 있는지, 그 가운데 무엇이 중심인지(공동 연구, 위험 간 연결, 기관 협력). 모양이 하는 주장: **가운데 놓인 것(또는 선이 굵은 것)이 가장 많이 이어져 있다.**

```json
{"template":"network","center":"data",
 "groups":[{"key":"g1","label":"기반 기술","tone":"go"},{"key":"g2","label":"응용 분야","tone":"sub"}],
 "nodes":[{"id":"data","label":"데이터","value":90,"group":"g1","highlight":true,"tone":"wait"},{"id":"ai","label":"인공지능","value":70,"group":"g1"},{"id":"bio","label":"바이오","value":60,"group":"g2"}],
 "links":[{"from":"data","to":"ai","weight":9},{"from":"data","to":"bio","weight":7},{"from":"ai","to":"bio","weight":3}],
 "footnote":"원 크기는 공동 연구 과제 수, 선 굵기는 함께 참여한 과제 수"}
```
- 마디는 타원 위에 `nodes` 순서대로 놓인다(같은 `group` 끼리 이어서 적는다). `center` 로 하나를 가운데 둘 수 있다. 5~16개
- 원 크기 = `value`, 선 굵기 = `weight`, 색 = `group`. **원 크기와 선 굵기가 무엇인지 `footnote` 에 반드시 적는다**
- `highlight` 마디에 닿는 선만 색, 나머지는 회색. 배치는 타원 고정이라 위치는 뜻이 없다(가까이 놓였다고 가까운 것이 아니다) — 그 점이 문제가 되면 쓰지 않는다

## 기존 도식 형태 14종의 새 디자인 (v2.3)

`cycle` · `funnel` · `venn` · `quadrant` · `pyramid` · `concentric` · `hub` · `fishbone` · `staircase` · `before-after` · `waterfall` · `iceberg` · `swimlane` · `logic-tree` — **사양은 [template-schemas.md](template-schemas.md)의 도식 형태와 같다.** 구조(키·배치 지시)는 그대로 받고 생김새만 바꿨다.

| 형태 | 새 디자인에서 달라진 것 |
|---|---|
| `cycle` | 원 다섯 개와 가는 화살표 → 서로 맞물린 굵은 화살 고리. 이름은 고리 바깥에 색 글씨, 가운데 옅은 원에 핵심어 |
| `funnel` | 옅은 가로 띠 위의 좁아지는 층. 단계 이름과 값은 층 안, 탈락 사유는 붉은 점선 화살표 |
| `venn` | 옅게 칠한 원 + 굵은 테. 겹침 이름은 흰 알약, 한가운데 겹침은 진한 알약 |
| `quadrant` | 네 칸을 둥근 판으로 띄우고 초점 칸만 색 테. 점은 흰 테를 두른 원, 이름표는 그림 가운데 쪽 |
| `pyramid` | 옅은 가로 띠 위의 잘린 피라미드. 위에서 아래로 한 방향 농도 |
| `concentric` | 안쪽이 진한 한 방향 농도의 원. 오른쪽에 점선 지시선과 설명 |
| `hub` | 가운데 진한 원 + 왼쪽 색 막대를 단 옅은 카드. 연결선은 굵고 옅게 |
| `fishbone` | 굵은 등뼈와 결과 상자(강조색), 갈래 끝에 알약 이름, 원인은 갈래 옆 |
| `staircase` | 옅은 단 + 진한 윗단, 마지막 단계만 진하게. 연도는 알약 |
| `before-after` | 현행은 회색 판, 개선 후는 색 머리띠 판. 가운데 화살표에 전환 수단 |
| `waterfall` | 합계는 남색, 증가는 청록, 감소는 붉은색. 값은 막대 위, 세로축을 줄이면 주에 밝힘 |
| `iceberg` | 물 아래를 옅은 띠로, 숨은 쪽을 진하게. 설명은 오른쪽 |
| `swimlane` | 왼쪽 진한 주체 이름표 + 번갈아 옅은 줄. 단계는 흰 카드, 강조 단계만 색 |
| `logic-tree` | 뿌리는 진한 상자, 가지는 색 상자, 잎은 왼쪽 색 막대를 단 옅은 카드. 곡선으로 이음 |

**템플릿 11종 (v2.4)** — `flow-process` · `org-chart` · `structure-block` · `layer-stack` · `concept-argument` · `comparison-matrix` · `matrix-heatmap` · `decision-flow` · `timeline-gantt` · `timeline-tracks` · `pipe-mapping`. 사양은 [template-schemas.md](template-schemas.md)와 같다.

| 템플릿 | 새 디자인에서 달라진 것 |
|---|---|
| `flow-process` | 윗단에 색 띠를 단 옅은 카드와 번호 원, 강조 단계만 진하게. 단계 사이는 겹화살, 게이트는 마름모와 알약 |
| `org-chart` | 뿌리는 진한 상자, 부문은 색 윗단 카드, 곡선으로 이음. 자문은 점선으로 붙인 강조색 테 카드 |
| `structure-block` | 층마다 색이 다른 진한 이름표와 옅은 띠, 흰 카드 |
| `layer-stack` | 위층은 점선 테, 아래층은 실선 테. 가운데 위·아래 화살표와 설명, 아래 쉐브론 단계 띠 |
| `concept-argument` | 가운데 진한 원, 좌우에 색 막대 카드, 곡선 연결 |
| `comparison-matrix` | 진한 머리줄, 번갈아 옅은 행, 기준 열은 옅은 색과 왼쪽 막대 |
| `matrix-heatmap` | 칸을 띄운 둥근 판. 3단은 옅음 → 중간 → 진함(흰 글씨), 강조 행은 강조색 테 |
| `decision-flow` | 머리띠 단 흰 카드와 아래로 가는 굵은 화살표, 탈락은 붉은 점선 가지 |
| `timeline-gantt` | 알약 머리, 색 막대, 게이트는 마름모. 산출물 상자·누적 상자·담당 부문과 도넛 |
| `timeline-tracks` | 축마다 진한 이름표와 옅은 줄, 흰 카드 이름표(연도는 색 굵은 글씨). 이름표 글자를 본문 크기로 키워 카드 폭 하한 270px |
| `pipe-mapping` | 유형마다 진한 이름표, 막힌 구간은 붉은 칠, 대응수단은 색 막대 카드, 점선 화살표로 이음 |

- 프리셋을 주지 않으면 `design-report` (사용자 선택 2026-11-21). `--preset house` 는 같은 모양의 평면판
- 지난 모양: 사양에 `"classic": true`
- `waterfall` 은 증감 합계가 `end.value` 와 다르면 그리지 않고 멈춘다(종전과 같음)

## 입체 층 도식 6종 (v2.5)

필자가 '보다 입체적으로'를 요청해 다시 그린 층 쌓기 시안(2026-11-23, 사용자 승인)을 형태로 옮겼다. 평면 상자로는 '아래가 위를 받친다·층이 쌓인다·단계가 오른다'는 느낌이 약할 때 쓴다. **입체는 관계를 나르는 모양일 때만** 쓴다 — 쌓임·받침·상승이 없는 내용을 입체로 그리지 않는다.

투영은 하나로 고정한다: 바닥 x 는 오른쪽 아래(가로 0.92 · 세로 0.30), y 는 왼쪽 아래, 높이는 위. 윗면은 빛 받은 면(밝게), 앞 두 면은 그늘(검정 덮개 20%·36%), 윗면 테두리는 흰 선. `design-report` 에서는 윗면에 옅은 그라데이션이 더해지고, `house` 등 평면 프리셋에서는 그라데이션 없이 같은 투영으로 나온다.

| 형태 | 보이려는 것 | 주요 키 |
|---|---|---|
| `iso-stack` 층 쌓기 | 기반층 → 중간층 → 상위층이 차례로 받친다 | `layers[{title,desc,chips[],tone,look,highlight}]` 위→아래 · `link`(층 사이 화살표 글, 예: "뒷받침") · `link_dir` up·down · `span`(판 화면 폭) · `thick` · `gap` · `label_w` |
| `iso-pillars` 단층 판 위 기둥 | 한 판 위에 받침 조건 여러 개가 선다 | `base{title,desc,tone,look}` · `pillars[{label,tone,highlight,h}]`(`h` 는 높이 배수) · `rows_title` · `rows[{before,after}]`(조건의 변화 줄) · `pillar_tone` · `pillar_size` · `pillar_h` · `depth` |
| `iso-compare` 두 모델 비교 | 단층 모델과 다층 모델을 나란히 견준다 | `left`·`right` 각각 `{title,sub,short,tone}` + `iso-pillars` 사양(`pillars`) 또는 `iso-stack` 사양(`layers`) · `shift`(가운데 진한 띠 한 문장) · `rows[{label,left,right}]`(대조표) · `split`(왼쪽 몫, 기본 0.34) |
| `iso-steps` 입체 계단 | 단계가 앞 단계 위에서 오른다 | `steps[{tag,title,desc,tone,highlight}]` 왼쪽→오른쪽 · `goal`(맨 윗단 칩) · `step_w` · `rise` · `base_h` |
| `iso-bars` 기둥 높이 비교 | 몇 항목의 크기 차이를 입체로 보인다 | `items[{label,value,highlight,tone}]` · `unit` · `decimals` · `max_h` · `bar_w` · `highlight_tone` |
| `iso-pyramid` 입체 피라미드 층 | 위로 갈수록 좁아지는 층(성숙 단계·위계) | `levels[{title,desc,tone,highlight}]` 위→아래 · `thick` · `base_size` · `top_ratio`(맨 위 판 / 맨 아래 판, 기본 0.36) |

`look`: `dark`(진한 윗면, 기본) · `line`(중간) · `tint`(옅은 판). `highlight: true` 는 주황(`wait`).

배치 규율 (시안을 다시 그리며 겪은 문제에서 나왔다):

1. **판 위 칩은 화면 가로 한 줄** — 투영 방향으로 비스듬히 늘어놓으면 서로 겹친다. 칩 줄 위·아래 끝은 판의 비스듬한 변을 따라 옆으로 밀리므로, 판 폭은 칩 폭 합계에 그 몫(칩 높이 × 0.92/0.30 ≈ 123px)을 더해 잡는다. 칩이 4개를 넘거나 글이 길면 칩 글을 줄인다
2. **층 이름은 오른쪽 열** — 판 오른쪽 끝에서 띄워 둔다. 층 사이 관계는 이름 열 사이의 주황 화살표와 한 낱말(`link`)로
3. **그림 폭 안에 배치** — 판·이름표가 그림 밖으로 나가지 않게 판 폭을 남는 폭에서 정한다. 넘치면 점검이 실패로 잡는다
4. **기둥 이름표는 기둥 위** — 기둥이 오른쪽 아래로 내려가며 놓이므로 이웃 이름표가 겹치지 않을 만큼 간격을 벌린다
5. **그림 위 제목 줄을 넣지 않는다** — 입체 도식의 예시는 `title` 없이 그린다(사용자 지시 2026-11-23 "그림 위에 설명글 길게 한 줄 있는 거 다 없애라"). 그림 번호·제목은 문서 캡션이 맡는다. `title` 을 주지 않으면 왼쪽 위 짧은 색 막대도 그리지 않는다
6. **입체 막대(`iso-bars`)는 높이를 실제와 다르게 읽히게 한다** — 값은 늘 글자로 적고(렌더러가 지우지 못하게 그린다), 0에서 시작하며(음수는 그리지 않고 멈춘다), 순위·정밀 비교는 `bar-highlight` 로 그린다. 문서에 넣을 때 `footnote` 에 그 뜻을 적는다

`--verify` 가 입체 형태에서 더 보는 것: 칩이 판 윗면 밖으로 나감 · 칩이 앞(위) 판에 가려짐 · 바깥 이름표가 판·기둥을 덮음 · 판이 그림 밖으로 나감 → 실패(exit 4). 인상 점검의 '진한 면' 경고는 남색 판이 클 때 나온다(승인 시안 전체는 흰 바탕 64% · 색 면적 20% · 진한 면 10%) — 판을 줄이거나 맨 아래 판을 `look: "line"` 으로.

## `--verify` 가 보는 것

- spec 의 모든 글자가 그림에 있는가(가로축 `x` 눈금은 칸이 좁으면 건너뛰어 적으므로 대조에서 뺀다)
- 배치: 글자끼리 겹침 · 그림 밖으로 나간 글자 · 도형보다 큰 글자 → 실패(exit 4). 스크립트 오류도 원인과 함께 실패
- 인쇄 글자: 16cm 폭에 넣을 때 본문 8pt·최소 7pt 미만이면 실패(exit 5)
- 인상(흰 바탕·색 면적·진한 면): 데이터 그래프는 흰 바탕이 넓은 것이 정상이다 — 기준 범위는 benchmark-intl-2026.md

자동 점검이 못 보는 것: 값이 맞는지(사양에 적힌 수치를 그대로 그린다), 제목이 그림과 같은 말을 하는지, 강조한 항목이 제목이 말하는 그 항목인지. 눈으로 확인한다.

## 그리지 않는 것

등각 투영 아이콘·건물 그림, 지도, 산점도, 사진 합성은 코드로 그리지 않는다(유량도·연결도·연결망은 v2.2.1부터 그린다. 판·기둥·계단을 비스듬히 쌓는 입체 층 도식 6종은 v2.5부터 그린다 — 사물·건물을 입체로 그리는 그림은 여전히 그리지 않는다). 필요하면 이미지 모델 경로(`scripts/gen_image.py`, [image-prompt-spec.md](image-prompt-spec.md))로 가고, 글자·수치는 코드 렌더와 대조한다.
