# 의도 → 도식 형태 판정

그림은 장식이 아니라 **관계를 보이는 장치**다. 도식의 모양은 그 자체로 주장을 한다 — 순환도는 "되먹임이 있다", 피라미드는 "위계가 있다", 벤은 "겹친다"고 말한다. 그래서 형태를 고르는 일은 색을 고르는 일보다 앞서고, 틀린 형태는 틀린 문장만큼 독자를 오도한다.

이 문서는 그 판정 절차다. 스킬은 그림을 그리기 전에 반드시 이 순서를 밟는다.

## 1단계 — 의도를 한 문장으로

> "이 그림을 본 독자는 ______ 을(를) 안다 / 믿는다 / 고른다."

- 빈칸에 들어가는 것이 **그림의 메시지**다. 주제("성과 관리")가 아니라 주장("평가가 끝이 아니라 다음 설계의 입력이다")이어야 한다
- 한 문장으로 안 써지면 그림이 두 장 필요하거나, 아직 그릴 때가 아니다
- 이 문장은 spec의 `intent.message`에 남긴다. 이미지 모델 프롬프트의 PURPOSE 절이 되고, 도식 카드의 머리가 된다

## 2단계 — 관계 유형 판정

본문에서 아래 신호 문구가 보이면 그 관계다. 둘 이상이면 **메시지에 더 가까운 쪽**이 주(主)다.

| 관계 | 본문 신호 | 1순위 형태 | 대안 | 쓰면 안 되는 형태 |
|---|---|---|---|---|
| **순서·절차** | 단계, 절차, ~를 거쳐, 먼저·다음 | `flow-process` | `staircase`(쌓여 오를 때) · `swimlane`(주체가 여럿일 때) | 순환도(되돌아가지 않는데) |
| **순환·되먹임** | 환류, 반영, 다시, 선순환, 피드백 | `cycle` | `flow-process`+되먹임 화살표(freeform) | 일렬 프로세스(되먹임이 사라짐) |
| **주체별 흐름** | 기관 간, 넘겨, 요청·회신, 역할 분담 | `swimlane` | `org-chart`(책임만 볼 때) | 단계 프로세스(누가 하는지 사라짐) |
| **수렴·선별** | 걸러, 통과, 선정률, 전환율, 이탈 | `funnel` | `decision-flow`(기준·탈락 사유가 주일 때) | 막대 그래프만(단계 인과가 안 보임) |
| **판정·기준** | 요건, 심사, 통과 기준, 탈락 시 | `decision-flow` | `funnel` | — |
| **위계·층위** | 상위·하위, 비전–목표–지표, 기반 | `pyramid` | `structure-block` · `layer-stack` | 동등 목록(무게 차이가 사라짐) |
| **포함·범위** | 안쪽일수록, 핵심–주변, 범위가 넓어지는 | `concentric` | `pyramid` | 벤(겹침이 아니라 포함인데) |
| **교집합·중복** | 겹치는, 공통, 중복, 사각지대 | `venn` | `comparison-matrix`(항목이 많을 때) | 동심원 |
| **구성·부분** | 구성, ~로 이루어진, 모듈, 계층 구조 | `structure-block` | `layer-stack` · `hub` | — |
| **중심–연결** | 허브, 플랫폼, 연계, 네트워크 | `hub` | `concept-argument`(근거가 좌우로 갈릴 때) | 조직도(대등한 연결을 위계로 왜곡) |
| **포지셔닝·우선순위** | 난이도 대비 효과, 두 기준, 우선 추진 | `quadrant` | `matrix-heatmap`(판정 단계가 있을 때) | 순위 목록(두 번째 기준이 사라짐) |
| **비교·평가** | 대안 비교, 장단점, 수단별 효과 | `comparison-matrix` | `matrix-heatmap` · `quadrant` | — |
| **대비·전환** | 현행 대비, 개선 후, 바뀌는 점 | `before-after` | `comparison-matrix`(항목 축이 명확할 때) | 두 개의 별도 목록 |
| **증감 분해** | 늘고 줄어, 요인별 기여, 증감 내역 | `waterfall` | `comparison-matrix`(숫자표) | 전후 두 막대만(무엇이 바꿨는지 안 보임) |
| **원인 분해** | 원인, 요인, 왜, ~때문에 | `fishbone` | `logic-tree`(원인→대책) · `iceberg` | — |
| **표면·심층** | 드러난 것은 일부, 근본 원인, 이면 | `iceberg` | `fishbone` | — |
| **목표 분해(MECE)** | 달성하려면, 과제 체계, 하위 과제 | `logic-tree` | `org-chart` · `structure-block` | 순서 없는 목록 |
| **근거·논증** | 필요성, 차별성, 왜 지금 | `concept-argument` | `logic-tree` · `hub` | — |
| **책임·체계** | 총괄, 부문, 자문, 추진체계 | `org-chart` | `swimlane` | — |
| **시간·일정** | 월별, 연차별, 착수·중간·결과 | `timeline-gantt` | `staircase`(성숙도) · `timeline-tracks`(여러 축) | — |
| **경과·대응** | 제도 도입 경과, 축별 연표 | `timeline-tracks` | `timeline-gantt` | — |
| **병목** | 막힌 곳, 지연 구간, 애로 | `pipe-mapping` | `funnel` · `fishbone` | — |

11종·14종 어디에도 없는 모양(벤 4개, 피라미드 옆 화살표 등)은 `freeform`으로 짓는다.

### 제안서·계획서·보고서 본문에서는 조립 도식(board)이 먼저 (v2.0)

아래 관계는 위 표의 1순위 형태보다 **board 레시피를 먼저** 권한다. 잘 그린 국내 공공 도식 57장의 문법(두 층 채움·왼쪽 이름표 열·층마다 바뀌는 격자·뜻 있는 색)을 그대로 쓸 수 있고, 내용에 맞춰 배치를 짤 수 있기 때문이다 — [benchmark-kr-2026.md](benchmark-kr-2026.md), 사양 [board-spec.md](board-spec.md).

| 관계 | board 레시피 | 위 표의 형태를 쓸 때 |
|---|---|---|
| 순서·절차 (단계마다 기준·산출) | `board-process-tabs` | 단계 이름만 잇는 짧은 흐름 → `flow-process` |
| 책임·체계, 주체별 흐름 | `board-governance` | 시간 축이 중요하면 `swimlane` |
| 위계·층위, 목표 분해 (비전–목표–전략) | `board-vision-system` | 위계 자체가 메시지면 `pyramid`, 이슈 분해면 `logic-tree` |
| 구성·부분 (계층 구조) | `board-layered-architecture` | — |
| 대비·전환 | `board-transition` | 항목이 1:1로 짝지어지면 `before-after` |
| 수렴·선별 + 판정 | `board-candidate-selection` · `board-ops-flow` | 단계별 건수가 메시지면 `funnel` |
| 판정·기준 (병렬 검토 + 공통 관문) | `board-review-structure` | 탈락 사유가 주면 `decision-flow` |
| 시간·일정 (연차 × 과업) | `board-roadmap` | 월 단위·마일스톤이 주면 `timeline-gantt` |
| 근거·논증, 연구 방법 (입력→분석→산출) | `board-research-framework` | 근거가 좌우로 갈리면 `concept-argument` |

모양이 뜻을 나르는 관계(순환·포함·교집합·포지셔닝·원인·증감·병목)는 위 표의 도식 형태가 맞다.

## 3단계 — 후보 2~3개, 서로 다른 관점으로

같은 내용도 형태에 따라 **독자에게 먼저 보이는 것**이 다르다. 후보는 같은 형태의 변주가 아니라 **관점이 다른 것**으로 고른다.

| 같은 내용 | 후보 A | 후보 B | 후보 C |
|---|---|---|---|
| 성과 활용이 낮다 | `fishbone` — 원인이 **네 갈래**다 | `iceberg` — 드러난 것보다 **숨은 것이 크다** | `logic-tree` — 그래서 **무엇을 할지** |
| 과제 선정 결과 | `funnel` — **어디서 많이** 떨어지나 | `decision-flow` — **무슨 기준으로** 거르나 | `waterfall` — 예산이 **무엇 때문에** 줄었나 |
| 부처 사업 정비 | `venn` — **겹치는 곳** | `quadrant` — **정비 우선순위** | `before-after` — 정비 **전과 후** |
| 추진 계획 | `timeline-gantt` — **언제** | `staircase` — **쌓여 오르는** 성숙도 | `swimlane` — **누가** |

각 후보에는 한 줄씩 적는다.

- **강점**: 이 형태가 먼저 보여 주는 것
- **손실**: 이 형태에서 사라지는 것 (예: 깔때기는 탈락 *기준*을 못 보인다)
- **추천**: 1단계 문장에 가장 빨리 닿는 것 하나

## 4단계 — 형태가 거짓말하지 않는지 확인

도식의 모양은 주장이다. 본문에 없는 주장을 모양이 하게 두지 않는다.

| 형태 | 모양이 하는 주장 | 이 주장이 사실이 아니면 쓰지 않는다 |
|---|---|---|
| 순환도 | 마지막이 처음으로 되돌아간다 | 되먹임 경로가 제도·일정에 실제로 있는가 |
| 피라미드 | 위가 아래보다 적고 무겁다, 아래가 위를 떠받친다 | 층 사이에 실제 위계가 있는가 |
| 벤 | 영역이 겹친다, 겹친 곳에 무엇이 있다 | 겹침이 실제로 확인되는가 (없으면 칸이 빈다) |
| 동심원 | 안이 밖에 포함된다 | 포함관계인가, 단순 나열인가 |
| 깔때기 | 단계마다 줄어든다 | 수량이 실제로 단조 감소하는가 |
| 계단 | 앞 단계 위에 쌓인다 | 다음 단계가 앞 단계를 전제하는가 |
| 2×2 | 두 기준이 독립이고 점의 위치에 근거가 있다 | 좌표에 근거(평가·자료)가 있는가 — 없으면 "개념 배치"라고 캡션에 쓴다 |
| 폭포 | 시작값 + 증감 = 끝값 | 합이 맞는가 (코드가 끝값을 계산해 대조한다) |
| 빙산 | 숨은 것이 드러난 것보다 크다 | 비중 주장을 본문이 뒷받침하는가 |
| 허브 | 중심과 주변이 대등하게 연결된다 | 실제로는 위계라면 조직도 |
| 로직 트리 | 하위 항목이 빠짐없고 겹치지 않는다 | MECE가 아니면 "주요 과제" 정도로 캡션을 낮춘다 |

## 5단계 — 강조는 한 곳

형태를 골랐으면 **제목이 말하는 요소 하나**에만 `highlight` 를 준다. 나머지는 회색으로 두어야 눈이 그곳으로 간다. 모든 칸이 같은 무게면 그림이 아무것도 주장하지 않는다 (젤라즈니·이코노미스트·GSS 공통 — [benchmark-classic.md](benchmark-classic.md)).

## 6단계 — 크기 규율

- **요소 7±2개.** 넘으면 묶거나 두 장으로 나눈다. 순환도 8개, 허브 8개, 피시본 6갈래가 사실상 한계다
- **한 그림 한 메시지.** 두 관계를 한 그림에 넣으면 둘 다 약해진다
- **글자는 짧게.** 도식 안 설명은 한 줄 15자 안팎. 긴 설명은 본문이나 캡션으로

## 산출 — 프롬프트 + 도식

판정이 끝나면 후보마다 spec을 쓰고 `figure_pack.py`로 묶는다.

```bash
python3 scripts/figure_pack.py 후보A.json 후보B.json 후보C.json -o figures/pack_03 --preset teal-lab [--gpt]
```

- 후보마다 **코드 렌더 도식**(검증 통과) + **이미지 모델 프롬프트**(의도 문장·형태 구도·프리셋 스타일·글자 전수 목록)가 나온다
- `index.html` 한 장에 후보 카드가 나란히 놓인다 — 사용자는 보고 고른다
- `--gpt` 를 주면 후보마다 이미지 모델 생성본과 OCR 대조까지 붙는다 (후보당 1회 과금)

## 형태별 요약 카드 (14종 신규)

| 형태 | 답하는 질문 | 데이터 모양 | 한계 | 예시 |
|---|---|---|---|---|
| `cycle` | 어떻게 되풀이되나 | items[3~8] (+center) | 8개 | `form-cycle.json` |
| `funnel` | 어디서 얼마나 걸러지나 | stages[{label,value,note,drop}] | 6단 | `form-funnel.json` |
| `venn` | 어디가 겹치나 | sets[2~3], overlaps{"12","13","23","123"} | 3개 | `form-venn.json` |
| `quadrant` | 무엇부터 하나 | x·y 축, quadrants[4], items[{_x,_y}] | 점 10개 | `form-quadrant.json` |
| `pyramid` | 무엇이 무엇을 떠받치나 | levels[위→아래] | 6층 | `form-pyramid.json` |
| `concentric` | 어디까지가 어디 안인가 | rings[안→밖] | 5겹 | `form-concentric.json` |
| `hub` | 무엇이 중심에서 무엇과 잇나 | center, nodes[3~8] | 8개 | `form-hub.json` |
| `fishbone` | 왜 생겼나 | effect, categories[{title,causes}] | 6갈래×3 | `form-fishbone.json` |
| `staircase` | 어떻게 쌓아 오르나 | steps[{tag,title,desc}], goal | 6단 | `form-staircase.json` |
| `before-after` | 무엇이 어떻게 바뀌나 | before, after, levers | 항목 6개씩 | `form-before-after.json` |
| `waterfall` | 무엇이 총량을 바꿨나 | start, steps[±value], end, unit | 8항목 | `form-waterfall.json` |
| `iceberg` | 드러난 것 아래 무엇이 있나 | above, below | 아래 7개 | `form-iceberg.json` |
| `swimlane` | 누가 언제 무엇을 넘기나 | lanes, phases, steps[{_lane,_col}] | 5레인×6열 | `form-swimlane.json` |
| `logic-tree` | 목표를 이루려면 무엇을 하나 | root, children[{children}] | 잎 12개 | `form-logic-tree.json` |

필드 명세는 [template-schemas.md](template-schemas.md) 「도식 형태 14종」.
