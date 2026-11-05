# doc-figure

**제안서·공문서·사업기획안·논문에 넣을 삽도를 만드는 Claude Code 스킬 — 잘 그린 국내 공공 도식 57장에서 잰 시각 문법으로, 내용에 맞춰 배치를 새로 짠 도식을 코드로 그린다. 한글이 깨지지 않고, 기본 경로는 API 키도 설치도 필요 없다.**

*Korean-first figure generator for government/business documents: code-rendered diagrams where Hangul labels, numbers, and grid alignment are exact by construction. No API key, no install.*

[English README](README.en.md) · [MIT License](LICENSE)

---

## v2.0 — 조립 도식 `board`

![조립 도식 예 — 운영 흐름](examples/preview/board-ops-flow.png)

v1.x 템플릿은 같은 크기 상자를 격자로 늘어놓았다. 잘 그린 공공 도식과 나란히 재 보니 차이가 숫자로 드러났다.

| | 흰 바탕 | 색 면적 |
|---|---|---|
| 잘 그린 공공 도식 57장 (중앙부처 기본계획·국책연구기관 보고서·예타·R&D 설명회·해외 공공기관) | 60% | 17% |
| v1.3 `report-classic` 산출물 | 93% | 1.7% |
| v2.0 `board` 레시피 | 40~63% | 14~29% |

잘 그린 도식은 ① 진한 머리띠 + 같은 색 옅은 몸의 **두 층 채움**, ② 층위를 박는 **왼쪽 이름표 열**, ③ 내용에 맞춰 **바뀌는 격자**, ④ **뜻을 나르는 색**, ⑤ 상자 안의 **2~3층 구조**를 쓴다. `board`는 이 문법을 부품(카드·띠·알약·쉐브론 단계·칩·판단 마름모·시간 띠·미니 매트릭스·지표 모듈·선 아이콘)으로 만들고, 행·열·묶음에 넣어 화살표를 잇는다. 레시피 10종(비전 체계도·추진체계도·번호 탭 절차·연차 로드맵·전환·후보 선정·병렬 검토·분석틀·계층 구성·운영 흐름)을 복사해 고치면 된다. `--verify`가 글자 넘침·화살표의 상자 관통·작은 글자·휑함까지 잡는다.

| | |
|---|---|
| ![비전 체계도](examples/preview/board-vision-system.png) | ![추진체계도](examples/preview/board-governance.png) |
| ![번호 탭 절차](examples/preview/board-process-tabs.png) | ![연차 로드맵](examples/preview/board-roadmap.png) |

근거: [references/benchmark-kr-2026.md](references/benchmark-kr-2026.md) · 사양: [references/board-spec.md](references/board-spec.md). 수집한 원본 그림은 저작권 때문에 저장소에 넣지 않았다.

## 왜 만들었나

문서에 넣을 조직도 하나를 이미지 모델에 시키면 이렇게 돌아온다.

- 한글 라벨이 **한글처럼 생긴 무의미한 획**이 된다
- "48억원"이 "4B억윈"이 된다
- 부문 4개를 요구했는데 3개나 5개가 나온다
- 표의 행·열이 어긋난다

고쳐 달라고 다시 시켜도 **다른 데가 깨진다.** 확산모델의 구조적 한계라서 프롬프트로는 못 넘는다.

> 2026-09 기준 최신 GPT Image(2.5 세대)는 한글을 대체로 정확히 그린다. 그래서 v1.1에 [선택 경로](#이미지-모델-경로-선택--같은-spec을-gpt-image로)로 붙였다. 다만 "대체로 맞다"와 "구조적으로 틀릴 수 없다"는 다르다.

doc-figure는 반대로 간다. **글자·수치·정렬은 전부 코드가 그린다.** 텍스트는 사양(spec)에 쓴 원문 그대로 DOM에 놓이므로, 글자가 깨지는 일이 **구조적으로 불가능**하다.

## 30초 시작 — 설치 없음

```bash
git clone https://github.com/parkjui92/doc-figure.git
```

Claude Code에서:

> `doc-figure/` 폴더 참고해서 추진체계도 그려줘. 총괄은 정책기획관, 부문은 조사분석·제도개선·성과관리 3개, 자문위원회 붙여줘.

브라우저로 열리는 HTML 한 장이 나온다. 인쇄(PDF)하거나 캡처해서 문서에 넣으면 된다.

크롬과 파이썬이 있으면 PNG를 자동으로 뽑을 수도 있다.

```bash
cd doc-figure
python3 scripts/render_figure.py examples/org-chart.json -o 그림_01.png --verify
```

```
[doc-figure] ✓ 그림_01.png  (2932x937)  template=org-chart  preset=gov-navy
[verify] ✓ spec 텍스트 20건 전부 DOM에 실재 (글자 깨짐 0)
```

## 의도를 먼저, 모양은 그다음

그림의 모양은 그 자체로 주장이다. 순환도는 "되먹임이 있다", 피라미드는 "위계가 있다", 벤은 "겹친다"고 말한다. 그래서 doc-figure는 색보다 **형태**를 먼저 고른다.

1. **의도 한 문장** — "이 그림을 본 독자는 ___을 안다"
2. **관계 유형 판정** — 순환·선별·교집합·포지셔닝·위계·포함·원인·증감·전환·주체별 흐름·목표 분해…
3. **관점이 다른 후보 2~3개** — 같은 "성과 활용이 낮다"도 피시본(원인이 네 갈래), 빙산(숨은 것이 더 크다), 로직 트리(그래서 무엇을 할지)로 보이는 것이 다르다
4. **도식 + 프롬프트 한 벌** — `figure_pack.py`가 후보마다 코드 렌더 도식과 이미지 모델 프롬프트를 카드 한 장(`index.html`)에 묶는다

```bash
python3 scripts/figure_pack.py examples/form-fishbone.json examples/form-iceberg.json examples/form-logic-tree.json \
    -o pack --preset teal-lab            # --gpt 를 붙이면 GPT Image 생성본까지
```

판정 기준 전체는 [의도 → 도식 형태 판정](references/form-catalog.md).

## 도식 형태 14종 — 관계의 모양

<table>
<tr>
<td width="50%"><b>cycle</b> — 순환·되먹임<br><img src="examples/preview/form-cycle.png"></td>
<td width="50%"><b>funnel</b> — 단계별 선별<br><img src="examples/preview/form-funnel.png"></td>
</tr>
<tr>
<td><b>venn</b> — 교집합·중복<br><img src="examples/preview/form-venn.png"></td>
<td><b>quadrant</b> — 2×2 포지셔닝<br><img src="examples/preview/form-quadrant.png"></td>
</tr>
<tr>
<td><b>pyramid</b> — 위계<br><img src="examples/preview/form-pyramid.png"></td>
<td><b>concentric</b> — 포함·범위<br><img src="examples/preview/form-concentric.png"></td>
</tr>
<tr>
<td><b>hub</b> — 중심–연결<br><img src="examples/preview/form-hub.png"></td>
<td><b>fishbone</b> — 원인 분해<br><img src="examples/preview/form-fishbone.png"></td>
</tr>
<tr>
<td><b>staircase</b> — 단계 상승<br><img src="examples/preview/form-staircase.png"></td>
<td><b>before-after</b> — 전후 비교<br><img src="examples/preview/form-before-after.png"></td>
</tr>
<tr>
<td><b>waterfall</b> — 증감 분해 (합계 자동 대조)<br><img src="examples/preview/form-waterfall.png"></td>
<td><b>iceberg</b> — 표면·심층<br><img src="examples/preview/form-iceberg.png"></td>
</tr>
<tr>
<td><b>swimlane</b> — 주체별 흐름<br><img src="examples/preview/form-swimlane.png"></td>
<td><b>logic-tree</b> — 목표 분해<br><img src="examples/preview/form-logic-tree.png"></td>
</tr>
</table>

## 템플릿 11종 — 문서 도식의 기본기

<table>
<tr>
<td width="50%"><b>timeline-gantt</b> — 일정·간트<br><img src="examples/preview/timeline-gantt.png"></td>
<td width="50%"><b>timeline-tracks</b> — 다중 트랙 연표<br><img src="examples/preview/timeline-tracks.png"></td>
</tr>
<tr>
<td><b>flow-process</b> — 단계 프로세스<br><img src="examples/preview/flow-process.png"></td>
<td><b>decision-flow</b> — 판정 게이트 + 탈락 분기<br><img src="examples/preview/decision-flow.png"></td>
</tr>
<tr>
<td><b>org-chart</b> — 추진체계·조직<br><img src="examples/preview/org-chart.png"></td>
<td><b>structure-block</b> — 계층 구성도<br><img src="examples/preview/structure-block.png"></td>
</tr>
<tr>
<td><b>layer-stack</b> — 상·하 2단 스택<br><img src="examples/preview/layer-stack.png"></td>
<td><b>concept-argument</b> — 논증 도해<br><img src="examples/preview/concept-argument.png"></td>
</tr>
<tr>
<td><b>comparison-matrix</b> — 비교표<br><img src="examples/preview/comparison-matrix.png"></td>
<td><b>matrix-heatmap</b> — 3단 판정 히트맵<br><img src="examples/preview/matrix-heatmap.png"></td>
</tr>
<tr>
<td colspan="2"><b>pipe-mapping</b> — 레인–세그먼트 병목 매핑<br><img src="examples/preview/pipe-mapping.png"></td>
</tr>
</table>

각 그림의 사양은 [`examples/`](examples/)에 JSON으로 들어 있다. 그대로 고쳐 쓰면 된다.

## 절제판 — `report-classic` · `exhibit`

생성형 AI 확산 이전(2023년 이전)에 잘 만든 도판을 벤치마킹했다 — FT·이코노미스트·젤라즈니·영국 정부 통계 지침·국내 국책연구기관 원고 지침과 보고서 실물([메모](references/benchmark-classic.md), 검증 출처 13건). 그림 번호는 위, 자료는 아래 왼쪽, 회색 중심에 **제목이 말하는 요소 한 곳만** 진하게, 모서리·그림자·아이콘·번호 뱃지 없음.

```bash
python3 scripts/render_figure.py examples/form-funnel.json --preset report-classic -o out.png
```

## 프리셋 15벌 — 색이 아니라 생김새가 바뀐다

> v2.0 기본은 **`house`**(제안서·계획서, 사용자 채택본 팔레트 — 남색·파랑·청록=산출·주황=주의·적=탈락)와 **`house-report`**(보고서 본문, 직각). 모든 프리셋에 뜻 있는 색 토큰 `--tone-*`가 있어 `board`는 어느 프리셋으로도 그려진다.

문서 종류에 따라 옷을 갈아입는다. v1.1부터 프리셋이 색뿐 아니라 **제목 형식·강조 방식(칠함/외곽선)·모서리·뱃지 모양·바탕 패널·제목 글꼴**까지 바꾼다. 같은 spec이 전혀 다른 인상으로 나온다.

| 같은 프로세스 spec | |
|---|---|
| **`academic-serif`** — 학술논문<br>명조 제목·왼쪽 정렬·밑줄, 강조 상자를 칠하지 않고 외곽선만 | ![](examples/preview/_flow_academic-serif.png) |
| **`modern-charcoal`** — 민간 기획·IR<br>큰 왼쪽 제목, 차콜 + 주황, 각진 뱃지 | ![](examples/preview/_flow_modern-charcoal.png) |
| **`teal-lab`** — 연구기관·과학기술<br>옅은 바탕 패널 위 흰 카드, 둥근 16px | ![](examples/preview/_flow_teal-lab.png) |

같은 히트맵을 8벌로:

| | |
|---|---|
| **`gov-navy`** — 제안서·연구보고서 | ![](examples/preview/_preset_gov-navy.png) |
| **`mono-formal`** — 공문서·내부 보고<br>흑백 인쇄·팩스를 거쳐도 3단 판정이 구분되도록 **명도 차만으로** 위계를 만든다 | ![](examples/preview/_preset_mono-formal.png) |
| **`accent-plan`** — 사업기획안·민간 제안<br>강조색이 붉은 경고가 아니라 따뜻한 주황 | ![](examples/preview/_preset_accent-plan.png) |
| **`forest-green`** — 환경·농정·지역<br>숲색 + 호박색 표지, 장식선 없음 | ![](examples/preview/_preset_forest-green.png) |
| **`academic-serif`** — 학술논문·인문사회 | ![](examples/preview/_preset_academic-serif.png) |
| **`modern-charcoal`** — 민간 기획·스타트업<br>히트맵까지 주황 계열 | ![](examples/preview/_preset_modern-charcoal.png) |
| **`line-minimal`** — 선만<br>채움을 걷어 저가 인쇄·첨부 자료에 강하다 | ![](examples/preview/_preset_line-minimal.png) |
| **`teal-lab`** — 연구기관·데이터 | ![](examples/preview/_preset_teal-lab.png) |

```bash
python3 scripts/render_figure.py examples/matrix-heatmap.json --preset academic-serif -o out.png
```

새 프리셋은 토큰 57개의 값만 바꿔 만든다 — [프리셋 사양](references/preset-spec.md).

## 자유 도식 — 11종에 없는 모양

순환·깔때기·벤·피라미드처럼 **모양 자체가 뜻인 것**은 가장 가까운 템플릿에 억지로 끼우지 않는다. `freeform` 템플릿에 HTML/SVG로 짓되, 색은 프리셋 토큰을 쓰는 부품 클래스로만 칠한다. `--verify`가 본문의 `#hex`·`rgb()`를 적발한다.

| | |
|---|---|
| `freeform-cycle` — SVG 5단계 순환 | ![](examples/preview/freeform-cycle.png) |
| `freeform-funnel` — 단계 축소 + 탈락 사유 (`modern-charcoal`) | ![](examples/preview/freeform-funnel.png) |

## 이미지 모델 경로 (선택) — 같은 spec을 GPT Image로

OpenAI 키가 있으면 `scripts/gen_image.py`가 같은 spec·같은 프리셋에서 **구조화 프롬프트를 자동 설계**해 최신 GPT Image 모델로 뽑는다.

```bash
python3 scripts/gen_image.py examples/org-chart.json --preset academic-serif --dry-run   # 프롬프트만 (키 불필요)
python3 scripts/gen_image.py examples/org-chart.json --preset academic-serif -o org.gpt.png
python3 scripts/gen_image.py examples/timeline-gantt.json --preset teal-lab --from-render -o gantt.gpt.png
python3 scripts/gen_image.py examples/timeline-gantt.json --fix gantt.gpt.png --instruction "…"
```

| 코드 렌더를 참조로 (`--from-render`, teal-lab) | 새로 생성 (academic-serif) |
|---|---|
| ![](examples/preview/_gpt_timeline-gantt_teal-lab.png) | ![](examples/preview/_gpt_org-chart_academic-serif.png) |

- **모델 자동 선택** — API 목록에서 가장 최신 gpt-image 버전을 고르고 같은 버전 안에서는 정밀 변형을 우선한다. 고정하려면 `FIGURE_IMAGE_MODEL`
- **프롬프트 설계** — 구도(템플릿별 배치 규칙) · 내용(spec 계층 목록) · 스타일(프리셋 토큰에서 팔레트 hex·모서리·그림자·강조 방식 자동 추출) · 글자 규칙(넣을 문자열 전수, 그 외 금지)
- **검증** — 생성 직후 OCR(macOS Vision → tesseract)로 라벨 대조. **그래도 결과는 반드시 눈으로 읽는다.** 이미지 모델은 "대체로 맞다"이지 "구조적으로 틀릴 수 없다"가 아니다
- 2026-09 실측(gpt-image-2.5-sunburst): 4장 라벨 121개 전부 정확, 장당 25~33초. 기본 경로는 여전히 코드 렌더다 — [왜](references/image-prompt-spec.md)

## 스킬로 설치하기

`SKILL.md`가 들어 있어 Claude Code 스킬로 바로 쓸 수 있다.

```bash
git clone https://github.com/parkjui92/doc-figure.git ~/.claude/skills/doc-figure
```

이후 "삽도 그려줘", "추진체계도", "이 보고서에 넣을 그림 만들어줘" 같은 요청에 자동으로 걸린다.

문서를 통째로 주면 **어디에 어떤 그림이 필요한지 먼저 짚어 제안하고**, 승인한 것만 그린다.

## 검증

레포가 약속한 것을 실제로 지키는지 스스로 검사한다.

```bash
bash scripts/selftest.sh
```

```
── ① 프리셋 토큰 정합 ──      57개 토큰 × 프리셋 8벌 · 이름 집합 일치
── ② 템플릿 하드코딩 색 ──    프리셋을 빠져나가는 색(hex·rgba) 없음
── ③ 설치 0 경로 ──           자기완결 HTML 생성 (외부 요청 0)
── ④ 예시 스키마 ──           예시 27건 · 템플릿+도식 형태 27종 · 프리셋 8벌
── ⑤ 렌더 + 텍스트 검증 ──    27건 전부 글자 깨짐 0
── ⑥ 자유 도식 색 규율 ──     freeform 본문 색 누수 0
── ⑦ 이미지 모델 경로 ──      전 예시 프롬프트 설계 + 모델 자동 선택 규칙 (API 호출 없음)
── ⑧ 도식 형태 14종 ──        형태마다 예시·구도 묘사·이름 완비
  통과 34 · 실패 0
```

`--verify`는 spec의 모든 텍스트가 렌더 결과에 실재하는지 대조한다.

> **다만 `--verify` 통과가 "그림이 멀쩡하다"는 뜻은 아니다.** 텍스트의 존재만 보므로 라벨끼리 겹치거나 캔버스 밖으로 밀린 것은 잡지 못한다. 결과는 반드시 눈으로 확인한다. (이 저장소를 만드는 동안 실제로 그런 사례가 나왔고, 그래서 `pipe-mapping`에 라벨 단 분리 기능이 들어갔다.)

## 필요한 것

| | |
|---|---|
| 기본 경로 (HTML) | **없음.** 브라우저만 있으면 된다 |
| 정밀 경로 (PNG) | 크롬 + 파이썬 3. `pillow`가 있으면 여백을 자동으로 잘라낸다 (없어도 렌더는 된다) |
| 외부 API | 기본·정밀·자유 도식 경로는 **없음.** 이미지 모델 경로만 OpenAI 키 (`OPENAI_API_KEY` 또는 `~/.config/doc-figure/openai.key`) |
| OCR 대조 (이미지 모델 경로) | macOS면 내장 Vision(최초 1회 자동 컴파일), 아니면 `tesseract` + `kor` |

크롬 경로가 다르면 `export CHROME_BIN="/path/to/chrome"`.

## 하지 않는 일

- **본문 표 조판** — 표는 문서 편집기가 그린다. 이 저장소는 도식 이미지 전용이다
- **사진풍 일러스트** — 이미지 모델 경로도 도식·인포그래픽까지만 ([references/image-prompt-spec.md](references/image-prompt-spec.md))
- **범용 차트 라이브러리 대체** — 산점도·회귀선이 필요하면 matplotlib을 쓴다

## 문서

| | |
|---|---|
| [의도 → 도식 형태 판정](references/form-catalog.md) | 관계 유형 판정표, 후보 고르기, 모양이 거짓말하지 않게 |
| [템플릿·도식 형태 스키마](references/template-schemas.md) | 25종 + 자유 도식 필드 명세 |
| [문서 유형 매핑](references/doc-type-map.md) | 어떤 문서에 무엇을 몇 장 |
| [프리셋 사양](references/preset-spec.md) | 토큰 57개(형태 토큰 19개 포함), 새 프리셋 만들기 |
| [이미지 모델 경로](references/image-prompt-spec.md) | 프롬프트 설계 원리, 모델 선택, 점검 순서 |
| [설계 기록](docs/design.md) | 왜 이렇게 만들었나 — 형태 토큰·자유 도식·이미지 모델 경로 |
| [설치·확장](docs/) | 템플릿 추가하기 |

## 라이선스

MIT. 자유롭게 쓰고 고치고 재배포해도 된다.
