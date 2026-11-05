# 템플릿 스키마 (11종 + 도식 형태 14종 + 자유 도식) — spec JSON 필드 명세

> **조립 도식 `board`의 사양은 [board-spec.md](board-spec.md)** — 제안서·계획서·보고서의 체계도·추진체계·절차·로드맵·전환·분석틀은 board 레시피(`examples/board-*.json`)가 먼저다. 이 문서는 나머지 템플릿 13종과 도식 형태 14종의 필드 명세다.

모든 spec은 최상위에 `"template": "<이름>"`을 갖는다. `"preset"`은 선택(기본 `gov-navy`).

**공통 선택 필드:** `source`(그림 아래 왼쪽 "자료: …" — 접두어가 없으면 붙인다) · `footnote`("주: …") · `intent`(의도 — `{"message","relation","why"}`, 그리지 않고 프롬프트·도식 카드에만 쓴다) · `title`(제목) · `subtitle`(부제) · `caption`(하단 `[그림 N] …` 캡션) · `image_layout`(이미지 모델 경로에서 구도 묘사를 직접 줄 때, 영문 권장 — 코드 렌더는 무시).

**밑줄로 시작하는 키(`_lane`·`_level`·`_w` 등)는 배치·강조 지시**다. 텍스트가 아니므로 `--verify` 대조에서 제외된다.

**줄바꿈:** 문자열의 `\n`은 줄바꿈으로 렌더된다(11종 전부 지원).

실물 spec은 `examples/<템플릿>.json`. 아래 명세와 1:1로 대응한다.

---

## 일정 계열

### 1. `timeline-gantt` — 일정·간트

```jsonc
{
  "template": "timeline-gantt",
  "title": "…", "subtitle": "…",
  "columns": ["9월","10월","11월","12월(12.15까지)"],  // 월 헤더(N칸)
  "top_note": "▲ …",        // (선택) 첫 행 위 주석
  "top_note_col": 0,         // 주석이 걸리는 컬럼 인덱스(0부터)
  "stages": [
    {"badge":"1단",
     "label":"1-1∥1-2\n병렬 착수",      // 좌측 레일 뱃지 텍스트
     "bar_label":"1-1∥1-2 병렬 착수",   // 바 안 텍스트
     "start":0, "end":1.05,             // 컬럼 단위 좌표(0=col0 시작). 소수 허용
     "gate":"자문\n검증\n게이트"}        // (선택) 바 우측 끝 게이트 ▼
  ],
  "milestones": [{"label":"착수보고","date":"(9.1)","col":0}],   // 하단 축 ◆
  "deliverable_boxes": [{"text":"산출물 16종","from_col":0,"to_col":2}],
  "cumulative": "누적\n산출물\n40종",   // (선택) 우측 강조 박스
  "footer": {                           // (선택) 하단 밴드
    "dept_label":"담당 부문", "dept_value":"6대 부문 8인",
    "dept_list":"정책환경 / 수요분석 / …",
    "donut_pct":57, "donut_headline":"병렬 구간 약 57%", "donut_sub":"…"
  }
}
```

### 2. `timeline-tracks` — 다중 트랙 연표

시간축 하나에 여러 축(제도·사업·평가 등)을 나란히 놓고 대응 관계를 보인다.

```jsonc
{
  "template": "timeline-tracks",
  "title": "…", "subtitle": "…",
  "axis": {"start":2015, "end":2026, "step":1},   // 눈금 시작·끝·간격
  "tracks": [
    {"name":"법·제도",
     "_tone":1,                      // 1=진함 2=중간 3=옅음 (축 굵기·색)
     "nodes":[
       {"at":2016,                   // 시점
        "year":"2016",               // 박스 안 좌측 연도 라벨
        "label":"기본법 제정\n추진 근거 마련",
        "_lane":0,                   // 같은 트랙 안 세로 단. 겹치면 1,2…로 내린다
        "_align":"start",            // 박스 정렬: start | center | end(기본)
        "_w":240},                   // 박스 폭(px). 좁으면 어절이 끊긴다
       {"at":2017, "to":2020,        // to를 주면 구간 막대
        "year":"2017~2020", "label":"1기 시범사업\n연 20과제 규모",
        "_anchor":"start",           // (선택) 박스를 시작점에 붙임(기본: 끝점)
        "_lane":0, "_align":"center", "_w":260}
     ]}
  ]
}
```

> **`_w` 주의** — 박스는 `연도 라벨 + 본문`을 가로로 나눠 쓴다. 폭이 좁으면 "시행령 전부개/정"처럼 어절 중간이 끊긴다. 본문 최장 줄 기준으로 넉넉히 준 뒤 **렌더 결과를 눈으로 확인**한다.

---

## 흐름 계열

### 3. `flow-process` — 단계 프로세스

```jsonc
{
  "template":"flow-process", "title":"…","subtitle":"…",
  "steps":[
    {"num":"1", "title":"현황·수요 진단", "desc":"정책환경 분석\n수요·자원 진단",
     "highlight":true}          // (선택) 강조 단계 = 진한 채움
  ],
  "gates":[{"after":1, "label":"1차 자문"}]    // (선택) N번째 단계 뒤 게이트 ▼
}
```

### 4. `decision-flow` — 게이트 판정 + 탈락 분기

단계마다 "무엇을 보고 몇 건이 남았는가"와 "떨어진 건은 어떻게 되는가"를 함께 보인다.

```jsonc
{
  "template":"decision-flow", "title":"…",
  "layout": {"main":780, "branch":120, "action":520},   // (선택) 폭 조정
  "gates":[
    {"num":"1단", "name":"형식 요건 심사",
     "count":"접수 128건 → 통과 96건",
     "principles":[{"id":"①","text":"신청 자격·업종 요건 충족"}],
     "fail":"요건 미비 32건\n보완 요청 후 재접수"}     // (선택) 우측 점선 분기
  ],
  "final":"최종 선정 24건 · 총 지원규모 48억원",        // (선택) 하단 결론 밴드
  "legend":[{"text":"통과 — 다음 단계 진행"},
            {"text":"미통과 — 보완 또는 종결", "_kind":"fail"}]
}
```

---

## 구조 계열

### 5. `structure-block` — 계층 구성도

```jsonc
{
  "template":"structure-block", "title":"…","subtitle":"…",
  "layers":[
    {"label":"응용\n계층",                     // 좌측 강조 라벨
     "boxes":[{"title":"진단 도구","desc":"성과활용 진단"}]}
  ]
}
```

### 6. `layer-stack` — 상·하 2단 스택

두 층의 관계(제도↔실행, 정책↔현장 등)와 그 아래 추진 순서를 한 장에 담는다.

```jsonc
{
  "template":"layer-stack", "title":"…",
  "upper": {"title":"제도 층 — 근거와 권한", "flag":"법령·지침",
            "blocks":["기본계획 수립 근거","예산 편성 지침"]},
  "divider": {"up":"실행 결과의 제도 환류",     // ↑ 위로 가는 관계
              "down":"제도가 정한 권한·한계"},   // ↓ 아래로 가는 관계
  "lower": {"title":"실행 층 — 집행과 산출", "flag":"현장",
            "blocks":["과제 공모·선정","협약·자금 집행"]},
  "band": {                                     // (선택) 하단 추진 순서 띠
    "steps":[{"num":"1","text":"제도 정비","sub":"1~3월"}],
    "note":"성과 환류 결과는 차년도 제도 정비의 입력이 되어 순환한다."
  }
}
```

> `band`가 있으면 마지막 단계에서 상단 층으로 순환 화살표가 자동으로 그려진다.

### 7. `org-chart` — 추진체계·조직

```jsonc
{
  "template":"org-chart", "title":"…","subtitle":"…",
  "root":{"title":"연구책임자 (총괄)","desc":"…"},
  "advisory":{"title":"자문위원회","desc":"…"},        // (선택) 우측 점선 연결
  "children":[{"title":"정책환경","lead":"환경·동향 분석"}]   // 권장 3~7
}
```

---

## 논증 계열

### 8. `concept-argument` — 논증·개념 도해

```jsonc
{
  "template":"concept-argument", "title":"…","subtitle":"…",
  "center":{"title":"핵심 과제","desc":"…"},          // 중앙 허브
  "supports":[{"title":"근거 1","desc":"…"}]          // 좌·우 자동 분할, 짝수가 균형
}
```

---

## 비교 계열

### 9. `comparison-matrix` — 비교표

```jsonc
{
  "template":"comparison-matrix", "title":"…","subtitle":"…",
  "key_column":true,                    // (선택) 첫 열 강조
  "columns":["RFP 지정 산출물","설계 과업","결과예시"],
  "rows":[["성과활용 진단도구","활용 지표 설계·검증","진단도구(안)"]]
}
```

### 10. `matrix-heatmap` — 3단 히트맵 판정

기준선 열 하나 + 비교 대상 열 N개. 각 칸을 3단계 강도로 칠해 판정을 보인다.

```jsonc
{
  "template":"matrix-heatmap", "title":"…",
  "layout": {"band":38, "rlabel":250, "base":322, "col":270},   // (선택) 폭 조정
  "top_arrow": {"label":"도입 난이도 낮음  →  높음"},            // (선택) 상단 화살표
  "columns":[
    {"name":"현행 기준", "tag":"비교 기준선"},   // ← columns[0] 은 항상 '기준선' 열
    {"name":"정보 제공", "tag":"권고·안내"},
    {"name":"유인 설계", "tag":"보조·세제"},
    {"name":"규율 도입", "tag":"의무·기준"}
  ],
  "groups":[
    {"band":"수요 측",                       // 좌측 세로 그룹 밴드
     "rows":[
       {"label":"이용자 인식 개선",
        "base":"캠페인 산발 시행, 효과 측정 없음",     // columns[0] 에 들어갈 값
        "cells":[{"text":"효과 뚜렷\n저비용 즉시 적용","_level":3},
                 {"text":"보조 효과","_level":1},
                 {"text":"해당 없음","_level":1}],
        "_emphasis":true}                    // (선택) 행 테두리 강조
     ]}
  ],
  "legend":[{"text":"현행 기준선","_level":0},
            {"text":"효과 뚜렷 — 우선 채택","_level":3}]
}
```

> **`cells` 개수는 반드시 `columns` 개수 − 1** 이어야 한다(기준선 열은 `base`가 담당). 어긋나면 행이 캔버스 밖으로 밀린다. `_level`은 1(약)·2(중)·3(강).

### 11. `pipe-mapping` — 레인–세그먼트 병목 매핑

레인(사업 유형·대상 등)마다 진행 파이프를 그리고, 병목 지점과 대응수단을 선으로 잇는다.

```jsonc
{
  "template":"pipe-mapping", "title":"…",
  "layout": {"lane":168, "pipe":580, "gutter":118, "node":530,
             "label_step":46},              // (선택) 라벨 단 세로 간격
  "segments":["신청","심사","협약","집행"],   // 파이프를 N등분
  "rows":[
    {"lane":"창업 지원",                     // 좌측 레인 이름
     "blocks":[                              // 병목 표시
       {"label":"제출서류 과다\n신청 포기 31%",
        "_inlet":true,                       // 파이프 입구 막힘(구간 대신)
        "_node":0,                           // 연결할 nodes 인덱스
        "_lw":200,                           // 라벨 폭
        "_lane":0},                          // 라벨 단(0,1,2…)
       {"label":"심사 지연 평균 6주",
        "_from":1, "_to":2,                  // segments 인덱스 구간
        "_node":1, "_lw":200, "_lane":1}
     ],
     "nodes":["온라인 간소화 서식","심사위원 풀 2배 확대"],   // 우측 대응수단
     "note":"신청 단계 이탈이 가장 크다."}                    // (선택)
  ]
}
```

> **`_lane`을 반드시 다르게 준다.** 한 레인에 병목이 둘 이상인데 `_lane`이 같으면 라벨이 가로로 겹쳐 읽을 수 없게 된다. `--verify`는 이 겹침을 잡지 못한다.

---

## 매핑 팁

- 시간축이 있으면 `timeline-*`, 계층이면 `structure-block`/`layer-stack`, 조직·책임이면 `org-chart`
- 정형 데이터 비교는 `comparison-matrix`, 판정·강도 비교는 `matrix-heatmap`
- 단순 순서는 `flow-process`, 통과/탈락이 갈리면 `decision-flow`
- 인과·근거 구조는 `concept-argument`
- 순환·되먹임·깔때기·포함 관계(벤)·위계 피라미드·허브처럼 **모양 자체가 의미인 것**은 억지로 끼우지 말고 `freeform`
- 가까운 템플릿으로 뜻이 온전히 전달되면 그것을 쓴다. 모양이 뜻을 바꾸면 `freeform`

---

## 자유 도식

### 12. `freeform` — 11종에 없는 모양

| 필드 | 형식 | 설명 |
|---|---|---|
| `body_html` | 문자열 | 캔버스(폭 1412px)에 들어갈 HTML 또는 인라인 `<svg>` |
| `canvas_height` | 숫자 (선택) | 캔버스 높이 고정(px). 절대 배치를 쓸 때 |
| `image_layout` | 문자열 (선택) | 이미지 모델 경로용 구도 묘사 |

**색은 부품 클래스나 `var(--토큰)`으로만** — `--verify` 가 `#hex`·`rgb()`·`hsl()` 을 적발한다.

| HTML 부품 | 모양 |
|---|---|
| `ff-row` `ff-col` `ff-center` | 가로·세로 배치, 가운데 정렬 |
| `ff-card` (`.edge`) | 흰 카드 (테두리 강조) |
| `ff-strong` | 강조 상자 — 프리셋에 따라 칠함/외곽선 |
| `ff-soft` `ff-faint` `ff-muted` | 옅은 틴트 / 더 옅은 바탕 / 무채색 |
| `ff-accent` | 강조색 점선 상자 (병목·탈락·주의) |
| `ff-heat1` `ff-heat2` `ff-heat3` | 판정 3단 채움 |
| `ff-badge` `ff-pill` | 번호 뱃지 / 알약 칩 |
| `ff-title` `ff-desc` `ff-note` | 굵은 제목 / 설명 / 보조 글 |
| `ff-arrow` `ff-hline` `ff-dline` | → 글리프 / 실선 / 점선 |
| `ff-icon` | 아이콘 자리 — `src="{{img:이름}}"` 는 `--icons` 로 넣은 아이콘으로 치환 |

| SVG 부품 | 모양 |
|---|---|
| `s-line` `s-dash` `s-accent` | 선 (보조색 / 점선 / 강조색) |
| `s-strong` `s-soft` `s-card` `s-faint` | 도형 채움 |
| `s-heat1~3` `s-deep` `s-mid` `s-marker` `s-accent-fill` `s-accent-soft` | 단색 채움 (화살촉 `<marker>` 에도) |
| `t-strong` `t-title` `t-body` `t-soft` `t-accent` `t-heat3` | `<text>` 글자색 |

실물: `examples/freeform-cycle.json`(SVG 5단계 순환), `examples/freeform-funnel.json`(HTML 단계 축소 + 탈락 사유).


---

## 도식 형태 14종 — `templates/forms.html`

`"template"` 에 형태 이름을 바로 쓴다 (`"template": "venn"`). 데이터는 `"data"` 아래에 둔다(최상위에 둬도 된다). 어떤 형태를 고를지는 [form-catalog.md](form-catalog.md). 실물은 `examples/form-<형태>.json`.

| 형태 | `data` 필드 |
|---|---|
| `cycle` | `items[{title, desc, tag?, highlight?}]` 3~8 · `center{title, desc}?` |
| `funnel` | `stages[{label, value?, note?, drop?}]` — `drop`은 이 단계로 오며 빠진 것(강조색 상자) |
| `venn` | `sets[{title, desc}]` 2~3 · `overlaps{"12","13","23","123"}` (숫자 = 집합 번호) |
| `quadrant` | `x{label, low, high}` · `y{label, low, high}` · `quadrants[4]` (좌상·우상·좌하·우하 순) `{title, desc}` · `items[{label, _x, _y, highlight?}]` (0~1) · `_focus` (`TL`/`TR`/`BL`/`BR`) · `takeaway?` |
| `pyramid` | `levels[{title, desc?}]` 위→아래 |
| `concentric` | `rings[{title, desc}]` 안→밖 |
| `hub` | `center{title, desc}` · `nodes[{title, desc, highlight?}]` 3~8 |
| `fishbone` | `effect{title, desc}` · `categories[{title, causes[]}]` 4~6 (홀수 번째 위, 짝수 번째 아래) |
| `staircase` | `steps[{tag?, title, desc}]` 아래→위 · `goal?` |
| `before-after` | `before{title, items[]}` · `after{title, items[]}` · `levers[]` · `lever_title?` |
| `waterfall` | `start{label, value}` · `steps[{label, value(±)}]` · `end{label, value?}` · `unit?` — `end.value`를 적으면 `start+Σsteps`와 맞아야 한다(틀리면 렌더 실패) |
| `iceberg` | `above{title, items[]}` · `below{title, items[]}` · `note?` |
| `swimlane` | `lanes[]` · `phases[]?` · `steps[{text, _lane, _col, highlight?}]` — 배열 순서대로 화살표 |
| `logic-tree` | `root{title, desc}` · `children[{title, desc?, children[{title}]}]` |

- 밑줄 키(`_x` `_y` `_lane` `_col` `_focus`)는 배치 지시라 글자 대조에서 빠진다
- 폭포 차트는 증감이 총액의 절반보다 작으면 **세로축 하단을 자동 생략**하고 ≈ 표시와 주석을 단다
- 렌더러가 멈추면 그림 안에 `[forms 오류] …` 가 찍히고 `--verify` 가 실패한다
