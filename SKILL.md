---
name: doc-figure
description: "제안서·연구개발계획서·공문서·사업기획안·보고서·논문에 들어가는 삽도(도식)를 만드는 스킬. 문서나 말로 전달받은 내용에서 '독자가 알아야 할 한 문장(의도)'을 뽑고 관계 유형을 판정한 뒤, 잘 그린 국내 공공 도식 57장과 사용자가 최종본에 채택한 그림 43장에서 잰 시각 문법(진한 머리띠+옅은 바탕의 두 층 채움, 왼쪽 이름표 열, 층마다 바뀌는 격자, 뜻을 나르는 색, 상자 안 2~3층 구조)으로 그린다. 기본은 조립 도식 엔진 board — 행·열·묶음에 카드·띠·알약·쉐브론 단계·칩·판단 마름모·시간 띠·미니 매트릭스·지표 모듈·선 아이콘을 넣고 화살표를 이어 내용에 맞춰 배치를 새로 짠다(비전 체계도·추진체계도·번호 탭 절차·연차 로드맵·전환 구조·후보 선정·분석틀·계층 구성도·운영 흐름 레시피 10종). 모양이 뜻을 나르는 관계는 도식 형태 25종(순환도·깔때기·벤·2×2·피라미드·동심원·허브·피시본·폭포·빙산·스윔레인·로직 트리·간트·히트맵 등)으로 그린다. 한글 라벨·수치는 코드가 그려 글자 깨짐이 없고, --verify가 글자 넘침·화살표 관통·작은 글자·휑함(흰 바탕 과다)을 잡는다. 이미지 모델용 설계 프롬프트(선택 시 GPT Image 생성본+OCR)도 함께 낸다. 삽도·삽화·도식·도해·인포그래픽·개념도·구조도·체계도·추진체계도·일정도·로드맵·조직도·흐름도·다이어그램을 그리거나, 문서의 그림 자리를 채우거나, '어떤 그림이 좋을까·이걸 그림으로', '디자인이 구리다·촌스럽다·안 예쁘다·밋밋하다·휑하다·와이어프레임 같다', '프롬프트도 같이 줘·GPT 이미지로', 그림 수정·재렌더·스타일 변경 요청 시 반드시 사용. 기본 경로는 외부 API 키 불필요. ※ 본문 표 조판이나 사진풍 일러스트에는 쓰지 않는다."
---

# doc-figure — 의도를 설명하는 도식 만들기

그림은 장식이 아니라 **관계를 보이는 장치**다. 먼저 전하려는 한 문장에 가장 빨리 닿는 모양을 고르고, 그다음 잘 그린 공공 도식의 문법으로 그린다.

## 핵심 흐름

```
① 의도 한 문장 → ② 관계 유형 판정 → ③ 경로 선택(조립 도식 / 도식 형태) → ④ 레시피를 복사해 spec 작성
   → ⑤ render --verify (글자·배치·인상) → ⑥ 눈으로 확인 → ⑦ 사용자가 고른다
```

판정 기준은 **[references/form-catalog.md](references/form-catalog.md)** — 그림을 그리기 전에 반드시 읽는다. 요지:

1. **의도** — "이 그림을 본 독자는 ___을 안다/믿는다/고른다." 주제가 아니라 주장. 한 문장으로 안 써지면 그림이 두 장이거나 아직 그릴 때가 아니다
2. **관계 유형** — 본문 신호 문구로 판정 (환류·다시 → 순환 / 걸러·선정률 → 선별 / 겹치는 → 교집합 / 비전·목표·전략 → 목표 분해 / 주관·참여·위탁 → 주체 간 역할 …)
3. **후보** — 형태가 애매하면 관점이 다른 것 2~3개. 후보마다 강점·손실 한 줄, 추천 하나
4. **모양이 거짓말하지 않는지** — 순환도는 되먹임을, 피라미드는 위계를, 벤은 겹침을 주장한다
5. **7±2** — 요소가 넘치면 묶거나 두 장으로

spec에는 판정 결과를 `intent`로 남긴다(그리지 않음. 이미지 프롬프트 PURPOSE 절과 후보 카드 머리가 된다).

## 어느 경로로 그릴까 — 조립 도식이 기본

| 관계 | 경로 | 시작 레시피 |
|---|---|---|
| 목표 분해 (비전→목표→전략→과제) | **board** | `examples/board-vision-system.json` |
| 주체 간 역할·흐름 (추진체계·거버넌스) | **board** | `board-governance` |
| 순서 + 단계별 기준 (절차·방법) | **board** | `board-process-tabs` |
| 과업 × 연차 (로드맵) | **board** | `board-roadmap` |
| 전환 (현재 → 변화, As-Is/To-Be) | **board** | `board-transition` |
| 수렴 → 판정 → 분기 (후보 도출·선정) | **board** | `board-candidate-selection` |
| 병렬 검토 + 공통 관문 | **board** | `board-review-structure` |
| 입력 → 처리 → 산출 (분석틀·연구 방법) | **board** | `board-research-framework` |
| 계층 구성 (시스템·플랫폼) | **board** | `board-layered-architecture` |
| 판정 있는 운영 흐름 + 되먹임 | **board** | `board-ops-flow` |
| 순환 · 선별 깔때기 · 교집합 · 2×2 · 피라미드 · 동심원 · 허브 · 원인(피시본·빙산·로직 트리) · 증감(폭포) · 주체별 흐름(스윔레인) | 도식 형태 | `examples/form-*.json` |
| 일정(간트·다중 트랙) · 판정 히트맵 · 비교표 · 병목 매핑 | 템플릿 | `examples/<템플릿>.json` |
| 어디에도 없는 모양 | `freeform` 또는 board 조합 | — |

**board 규칙** — 사양은 [references/board-spec.md](references/board-spec.md). 새 그림은 **가장 가까운 레시피를 복사해** 내용만 바꾸고 배치를 고친다. 핵심 개념도를 같은 상자 격자 템플릿에 끼우지 않는다 — 이 사용자는 템플릿 그림을 "너무 별로"라며 거부하고 손배치 흐름도를 채택한 적이 있다(2026-09). board는 그 손배치를 사양 파일로 옮긴 것이다.

## 잘 그린 공공 도식의 규율 (2026-10 벤치마크)

중앙부처 기본계획·국책연구기관 보고서·예타 보고서·R&D 설명회·해외 공공기관 도식 57장과 사용자 채택본 43장에서 뽑았다. 근거·수치·출처는 **[references/benchmark-kr-2026.md](references/benchmark-kr-2026.md)**.

1. **위계는 칠한 면으로** — 진한 머리띠·이름표 + 같은 색 옅은 몸 + 흰 안쪽 카드. 회색 테두리 상자만으로 위계를 만들지 않는다(와이어프레임처럼 보인다)
2. **왼쪽 이름표 열** — 층위·행의 역할(비전·목표·전략, 응용·플랫폼·인프라, 과업 1·2·3)을 그림 폭 8~15%의 진한 칸에 박는다
3. **격자는 내용에 맞춰 바꾼다** — 층마다 1→3→2열, 열 폭은 항목 수나 담당 범위에 비례. 같은 크기 상자를 같은 간격으로 늘어놓지 않는다
4. **색은 뜻으로** — `tone`: main(본체·진행) · sub(보조) · go(산출·통과) · wait(주의·대기·예시) · stop(탈락·제약, 점선) · mute(현재·기존). 한 그림에서 같은 색은 같은 뜻, 셋 넘으면 범례
5. **상자 안에 2~3층** — 머리띠+목록, 번호+제목+설명, 기준값 ➜ 목표값(`kpi`). 라벨 하나만 든 상자를 늘어놓지 않는다
6. **관계에 이름을** — 이웃 단계는 `join`(▶·›·+), 그 밖은 화살표에 주고받는 것을 적는다("협약·연구비 지원", "단계 보고")
7. **아이콘은 범주를 알아보게 할 때만** — 같은 선 아이콘 세트, 카드당 하나, tone 색. 클립아트·3D·사진·그라데이션·광택·무지개 색은 쓰지 않는다
8. **인쇄 크기** — 글자는 pt로 정한다. 16cm 폭(A4 세로 본문)에 넣을 때 본문 약 10pt·최소 8pt(board는 `print_cm`·`body_pt`로 자동 계산, `--verify`가 pt로 잰다). 빽빽한 흐름도는 `print_cm: 24`(가로 쪽)로 넣거나 두 장으로 나눈다. 간트·다중 트랙·병목 매핑·폭포·2×2는 좌표 고정이라 세로 쪽에선 작다 — 세로 쪽엔 board 레시피를 쓴다. 흰 여백은 묶음 바깥에, 인상 기준은 흰 바탕 약 60% · 색 면적 약 17%
9. **결론형 제목** — 제목만 읽어도 결론을 안다("이용·제공·결합의 요건을 각각 검토한다"). 진하게 칠한 한 곳(`focus`)이 제목이 말하는 그것

편집 관례는 v1.3을 그대로 따른다 — 그림 번호·제목·`(단위)`·`주:`·`자료:` 자리, 직접 그린 도식은 `"source": "연구진 작성"`, **작성자가 매기지 않은 번호를 붙이지 않는다**, 없는 출처·수치를 만들지 않는다(설계 예시면 `tag`로 밝힌다).

## 프리셋 — 문서 성격으로 하나

| 프리셋 | 대상 | 인상 |
|---|---|---|
| **`house`** (기본) | **제안서·연구개발계획서·정책 보고자료** | 사용자 채택본 팔레트 — 남색 #16275C · 파랑 · 청록(산출) · 주황(주의) · 적(탈락), 옅은 파랑 바탕, 모서리 8px, Pretendard |
| **`house-report`** | **연구보고서 본문·예타식 보고서** | house의 직각(2px)판 — 국책연구기관 본문 도식 관측(직각 12/15장) |
| `report-classic` | 흑백 복사·절제가 우선인 보고서 | 회색 중심 + 남색 한 곳, 모서리 0 |
| `mono-formal` | 공문서·흑백 인쇄 | 무채색, 명도 차로만 위계 |
| `exhibit` | 기획·경영 자료 | 결론형 왼쪽 제목 + 짧은 색 막대, 외곽선 강조 |
| `gov-navy` | (v1.x 기본) | 네이비, 가운데 제목 + 장식선 |
| `accent-plan` · `forest-green` · `academic-serif` · `modern-charcoal` · `line-minimal` · `teal-lab` | 기획안·환경·학술·민간·저가 인쇄·연구소 | 색·글꼴 변주 |

**한 문서 안에서는 한 프리셋.** 다양성은 형태로 낸다. 모든 프리셋에 `--tone-*`가 있어 board는 어느 프리셋으로도 그려진다. 사양은 [references/preset-spec.md](references/preset-spec.md).

## 진입 2경로

### 경로 1 — 문서를 받았을 때

1. 본문을 읽고 **삽도 후보표**를 만든다 — 위치·의도 한 문장·관계 유형·경로/레시피(대안)·근거

   | # | 들어갈 위치 | 의도 (독자가 알아야 할 것) | 관계 | 레시피 (대안) |
   |---|---|---|---|---|
   | 1 | Ⅱ-2 추진체계 | 주관기관이 총괄하고 주고받는 것이 정해져 있다 | 주체 간 역할 | `board-governance` (`org-chart`) |

2. 문서 성격에 맞는 **프리셋 하나** (제안서 `house`, 보고서 본문 `house-report`)
3. **사용자 승인** — 승인된 것만 그린다. 문서에 없는 내용을 그림으로 지어내지 않는다
4. 승인분마다 spec → `render --verify` → 눈으로 확인 (형태가 애매한 그림은 `figure_pack`으로 후보 2~3개)

### 경로 2 — 말로 지시받았을 때

- 형태까지 지정했으면("추진체계도 그려줘") 해당 레시피로 바로 1장
- 내용만 줬으면 **후보 2~3개를 도식+프롬프트로** 보여 주고 고르게 한다
- 정보가 모자라면 **비워두지 말고 물어본다.** 도식은 빈칸이 그대로 드러난다

## 렌더와 검증

```bash
python3 scripts/render_figure.py examples/board-governance.json -o 그림_03_추진체계.png --verify
python3 scripts/render_figure.py <spec.json> -o out.png --verify --preset house-report
python3 scripts/render_figure.py --list          # 템플릿·도식 형태·프리셋 목록
```

`--verify`가 보는 것:

| 점검 | 실패 조건 |
|---|---|
| 글자 | spec 글자가 DOM에 없음 (exit 2) |
| 배치 (board) | 글자 넘침 · 그림 밖 이탈 · 글자 15.5px 미만 · 화살표가 다른 상자 관통 · 이름표가 상자를 덮음 · 없는 아이콘 (exit 4) |
| 인상 | 경고만 — 흰 바탕 85% 초과(휑함) · 색 면적 6% 미만(유채 프리셋) · 38% 초과(과채색) |

**통과해도 눈으로 본다** — 같은 크기 상자가 기계적으로 늘어서지 않았는지, 진한 면이 제목이 말하는 그것에 가 있는지, 클립아트 느낌은 없는지(수치로 못 잡는다).

### 기본 경로 — HTML 만들기 (설치 0)

크롬·파이썬이 없으면: `templates/<템플릿>.html`을 읽고 `/*__STYLE_TOKENS__*/` → `presets/<프리셋>.css` 전문, `/*__FIGURE_DATA__*/ null` → spec JSON, `/*__ICONS__*/ {}`는 그대로, board는 `/*__ICON_SET__*/ {}` → `templates/icons/tabler-outline.json`에서 쓰는 아이콘만 골라 `{"이름": "<path…>"}`. `그림_NN_<이름>.html` + spec `.json`을 함께 남긴다.

### 후보 묶음

```bash
python3 scripts/figure_pack.py 후보A.json 후보B.json 후보C.json -o figures/pack_01 --preset house
python3 scripts/figure_pack.py … --gpt                  # 이미지 모델 생성본까지 (후보당 1회 과금)
```

후보마다 `NN_<형태>.png`(검증 통과분) · `.prompt.txt` · `.json` · (`--gpt`) `.gpt.png`, 그리고 카드 한 장 `index.html`. 사용자에게는 `index.html`을 보여 주고 **추천 하나와 그 이유**를 한두 줄로 말한다.

## 도식 형태 25종 (board 밖)

| 관계 | 형태 |
|---|---|
| 순서·절차 | `flow-process` · `staircase` · `swimlane` |
| 순환·되먹임 | `cycle` |
| 선별·판정 | `funnel` · `decision-flow` |
| 위계·포함·구성 | `pyramid` · `concentric` · `structure-block` · `layer-stack` · `org-chart` |
| 연결·중심 | `hub` · `concept-argument` |
| 교집합 | `venn` |
| 비교·포지셔닝 | `comparison-matrix` · `matrix-heatmap` · `quadrant` · `before-after` |
| 원인·분해 | `fishbone` · `iceberg` · `logic-tree` · `waterfall` |
| 시간 | `timeline-gantt` · `timeline-tracks` |
| 병목 | `pipe-mapping` |
| 그 밖 | `freeform` |

필드 명세는 [references/template-schemas.md](references/template-schemas.md). `structure-block`·`flow-process`·`org-chart`·`concept-argument`가 맡던 일은 이제 board 레시피가 더 잘한다 — 단순한 그림을 빨리 낼 때만 쓴다.

`freeform` — 모양이 뜻을 바꾸는데 맞는 형태가 없을 때. 색은 부품 클래스(`ff-*`, SVG `s-*`/`t-*`)나 `var(--토큰)`으로만(`#hex`·`rgb()`는 `--verify`가 적발).

## 이미지 모델 경로

```bash
python3 scripts/gen_image.py <spec.json> --preset house --dry-run         # 프롬프트만 (과금 0, 키 불필요)
python3 scripts/gen_image.py <spec.json> --preset house -o 그림.gpt.png
python3 scripts/gen_image.py <spec.json> --from-render -o 그림.gpt.png     # 코드 렌더를 참조로 — 배치 가장 정확
python3 scripts/gen_image.py <spec.json> --fix 그림.gpt.png --instruction "…"
```

- `house`·`house-report`는 프롬프트에 **KR-GOV DIAGRAM DISCIPLINE** 절(두 층 채움·뜻 있는 색·격자 변화·선 아이콘 조건부·인쇄 글자 크기)이 들어간다. `report-classic` 등은 종전 PRINT-FIGURE DISCIPLINE(아이콘·뱃지 금지)
- board spec도 프롬프트가 된다 — 배치 키는 빼고 구조(row·col·group·band·links)를 설명한다
- **검수가 끝이다** — OCR(macOS Vision → tesseract) 결과를 보고 이미지를 직접 열어 라벨을 전부 읽는다. 목록에 없는 번호·뱃지를 모델이 덧붙이지 않았는지도 본다. 틀리면 `--fix`, 두 번 안 되면 코드 렌더
- 모델은 API 목록의 최신 gpt-image 자동 선택(env `FIGURE_IMAGE_MODEL`로 고정). 키: env `OPENAI_API_KEY` → `~/.config/doc-figure/openai.key`. 없으면 `--dry-run` 프롬프트를 사용자가 ChatGPT에 붙여 넣게 한다

프롬프트 설계 원리는 [references/image-prompt-spec.md](references/image-prompt-spec.md).

## 문서에 넣을 때

`figures/삽입_가이드.md`에 그림번호·제목·파일경로·삽입 위치·대체텍스트·산출 경로를 적는다. 한글(.hwp/.hwpx) 문서에는 **그림(PNG)으로 삽입**하라고 안내한다. 문서 캡션을 한글 문단이 맡으면 `"header": "none"`으로 그림 안 제목을 뺀다. 16cm 폭에 넣는 것을 기준으로 글자 크기를 맞췄다(board 본문 약 6.5pt).

## 하지 않는 일

- **본문 표 조판** — 표는 문서 편집기가 그린다 (`comparison-matrix`처럼 표 형태의 *그림*은 그린다)
- **사진풍 일러스트**, 클립아트, 3D, 그라데이션 장식
- **없는 내용 지어내기**, **모양이 없는 주장 하기** — 되먹임 없는 순환도, 위계 없는 피라미드, 근거 없는 2×2 좌표
- **검수 없는 이미지 모델 결과 납품**

## 자체검사

`bash scripts/selftest.sh` — 프리셋 토큰 정합 · 템플릿 하드코딩 색 0 · 설치 0 경로 · 예시 스키마 · 전 예시 렌더(글자·배치) · 자유 도식 색 규율 · 이미지 프롬프트 설계 · 도식 형태 완비 · board 레시피 인상 범위.
