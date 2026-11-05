# 프리셋 사양

## 규율 — 값만 바꾸고 이름은 건드리지 않는다

프리셋은 CSS 커스텀 속성 **105개의 값 묶음**이다(v2.0에서 board 토큰 29개 추가). 템플릿 14종(11종 + `forms` + `freeform` + `board`)은 `var(--토큰)`만 쓰므로, 값을 갈아끼우면 전부 한꺼번에 옷을 갈아입는다.

v1.0의 38개는 거의 전부 **색**이었다. 그래서 프리셋을 바꿔도 네이비의 명도만 달라지고 모양은 그대로여서 "다 비슷하다"는 인상을 줬다. v1.1은 **생김새를 바꾸는 형태 토큰 19개**를 더했다. 기본값이 v1.0 모양과 같아서 `gov-navy` 그림은 픽셀 단위로 그대로다.

**토큰 이름을 더하거나 빼면 이 구조가 무너진다.** 어떤 템플릿이 없는 토큰을 참조하면 그 자리만 조용히 기본색으로 렌더되고, 아무도 알아채지 못한다. 그래서 `scripts/selftest.sh` 가 프리셋 간 토큰 이름 집합이 완전히 같은지 매번 검사한다.

토큰을 **추가**하려면 모든 프리셋에 추가한다.

## 토큰 105개

| 묶음 | 토큰 | 쓰임 |
|---|---|---|
| 주색 | `--navy-deep` `--navy-mid` `--navy-marker` | 뱃지·헤더밴드·게이트▼·마일스톤◆ |
| 채움 | `--bar-fill` `--bar-fill-2` `--bar-border` `--chip-track` | 간트바·셀 밴드·도넛 트랙 |
| 선·바탕 | `--grid-line` `--line-soft` `--line-track` `--fill-faint` | 격자·점선·표 줄무늬 |
| 글자 | `--ink` `--ink-soft` `--bg` | 본문·부제·배경 |
| 판정 | `--heat-1~3` `--heat-1~3-ink` | 3단 히트맵 채움·글자 |
| 무채색 | `--neutral-fill` `--neutral-line` `--neutral-ink` `--neutral-head` | 기준선 열·보조 바탕 |
| 강조 | `--accent` `--accent-soft` | 병목·미통과·핵심 제안 |
| 트랙 | `--track-1~3` | 다중 트랙 연표 축 |
| 타이포 | `--font` `--w-title` `--w-strong` `--w-label` `--w-body` | **프리셋 불변** |
| 형태 | `--radius-bar` `--radius-box` `--radius-badge` `--shadow` | 모서리·그림자 |
| **제목** (v1.1) | `--font-title` `--title-align` `--title-scale` `--title-ink` `--title-track` `--title-deco` `--title-under` `--title-under-gap` | 제목 글꼴(명조 가능)·정렬·크기·자간·양옆 장식선·밑줄 |
| **캡션** (v1.1) | `--caption-align` `--caption-ink` | 캡션 정렬·색 |
| **강조 상자** (v1.1) | `--strong-fill` `--strong-ink` `--strong-ink-soft` `--strong-ring` | 헤더 띠·뿌리 상자·최종 단계를 칠할지(fill) 테두리만 둘지(ring) |
| **초점** (v1.3) | `--focus-fill` `--focus-ink` `--focus-ink-soft` `--focus-ring` | `highlight` 로 지정한 '제목이 말하는 요소' — 구조용 강조(`--strong-*`, 헤더 띠·이름표)와 분리. 기본값은 `--strong-*` 와 같다 |
| **편집** (v1.3) | `--trim-x` `--fig-display` `--caption-order` `--caption-mt` `--caption-mb` `--caption-size` `--caption-weight` `--src-size` `--src-gap` `--title-tag` `--title-tag-color` `--accent-line` `--accent-fill` `--ornament` | 그림 번호·제목을 위로(보고서 관례), 자료·주 줄, 도판식 색 막대 표식, 강조 상자 선·바탕, 뜻 없는 장식(중복 번호 뱃지) 걷기 |
| **부품** (v1.1) | `--card-fill` `--badge-shape` `--radius-pill` `--shadow-hub` `--word-break` | 카드 바탕·뱃지 원/사각·칩 둥글기·중심 상자 그림자·낱말 단위 줄바꿈 |
| **뜻 있는 색** (v2.0) | `--tone-{main,sub,go,wait,stop,mute}` + `-tint` + `-line` (18개) | board의 `tone` — 본체·보조·산출·주의·탈락·기존. 진한 값은 머리띠·이름표·화살표, `-tint`는 옅은 몸(같은 색상 명도 94.5%), `-line`은 테두리 |
| **조립 부품** (v2.0) | `--board-font` `--board-fs` `--board-line` `--board-panel` `--board-chip` `--board-radius` `--board-icon-stroke` `--board-link-w` `--board-band-label` `--board-bar-sep` `--board-step-mid` | board 글꼴(Pretendard 우선)·본문 기준 글자(22px = 그림 폭 1.5%)·선·묶음 바탕·칩 바탕·모서리·아이콘 획·화살표 굵기·띠 이름표 겹침색·막대 구분선·쉐브론 중간색 |

### 형태 토큰 쓰는 법

| 바꾸고 싶은 인상 | 토큰 |
|---|---|
| 제목을 왼쪽으로, 아래 가는 줄 | `--title-align:left; --title-deco:none; --title-under:2px solid <색>; --title-under-gap:14px` |
| 제목만 명조 | `--font-title: "AppleMyungjo", "Nanum Myeongjo", "NanumMyeongjo", "Noto Serif KR", "Batang", serif` |
| 강조 상자를 칠하지 않고 외곽선만 | `--strong-fill:#FFFFFF; --strong-ink:<주색>; --strong-ring:inset 0 0 0 2px <주색>; --strong-ink-soft:var(--ink-soft)` |
| 번호 뱃지를 사각으로 | `--badge-shape:4px` (원은 `50%`) |
| 알약 칩을 각지게 | `--radius-pill:4px` (기본 `999px` = 완전한 알약) |
| 그림 전체를 옅은 패널 위에 | `--bg:<옅은 색>` — 흰 카드(`--card-fill`)가 그 위에 떠서 층이 생긴다 |
| 한국어 낱말 중간에서 줄이 안 끊기게 | `--word-break:keep-all` |
| 그림 번호·제목을 그림 위로 (국내 보고서) | `--fig-display:flex; --caption-order:-1; --caption-mt:0; --caption-mb:14px; --caption-weight:700` |
| 도판식 짧은 색 막대 표식 | `--fig-display:flex; --title-tag:block; --title-tag-color:<강조색>` |
| 탈락·병목 상자를 요란하지 않게 | `--accent-line:solid; --accent-fill:transparent` |
| 겹치는 장식 걷기 (단계 원 번호 + 뱃지 번호 중복 등) | `--ornament:none` |

**주의 — 그림자는 `none`이 아니라 `0 0 0 transparent`로.** 템플릿이 `box-shadow: var(--strong-ring), var(--shadow)` 처럼 목록으로 합치므로, `none`이 끼면 목록 전체가 무효가 되어 테두리까지 사라진다.

**모서리는 템플릿에 박혀 있지 않다.** v1.0에는 10~20px 반경이 템플릿 곳곳에 하드코딩돼 `mono-formal`(4px)에서도 둥글게 나왔다. v1.1부터 전부 `--radius-box` 기준 상대값(`calc(var(--radius-box) ± n)`)이라 프리셋 반경을 따라간다.

### `--font`는 왜 불변인가

한글 폰트 폴백을 프리셋마다 다르게 두면, 어떤 프리셋에서만 글자가 깨지고 다른 데선 멀쩡한 상황이 생긴다. 재현도 어렵고 원인도 안 보인다. **본문 글꼴은 모든 프리셋이 같은 값을 쓴다.**

제목 글꼴(`--font-title`)만 예외로 열었다. 제목은 한 줄이라 깨지면 바로 보이고, 명조 폴백 목록 끝에 `serif`가 있어 최악에도 시스템 명조로 떨어진다.

## 15벌 (문서용 파생 3벌 포함)

같은 히트맵을 8벌로 렌더한 모습은 `examples/preview/_preset_*.png`, board 레시피는 `examples/preview/board-*.png`.

### `house` — 기본 (v2.0)

사용자가 최종본에 채택한 그림(사업 기획 흐름도·연구개발계획서 3건)에서 잰 팔레트. 남색 `#16275C` · 파랑 `#3D5BA9` · 청록 `#197D86`(산출) · 주황 `#B77718`(주의·예시) · 적 `#A84945`(탈락), 옅은 파랑 바탕, 모서리 8px, 그림자 0, Pretendard. 옛 템플릿에서도 제목 왼쪽·장식선 없음·글자 1.4배. 이미지 프롬프트는 KR-GOV DIAGRAM DISCIPLINE 절을 쓴다(`@image-discipline: kr-gov`). 근거 [benchmark-kr-2026.md](benchmark-kr-2026.md).

### `house-report` — 보고서 본문판 (v2.0)

`house`와 같은 색, 모서리 0~2px. 국책연구기관 보고서 본문 도식이 직각 12/15장이었던 관측을 따른다.

### `gov-navy` — v1.x 기본

정부·공공기관 보고서 플랫 인포그래픽. 네이비 `#12245B`, 라운드 12px, 옅은 그림자.

### `mono-formal` — 공문서

**색상(hue)이 아니라 명도 차만으로 위계를 만든다.** 흑백 프린터·팩스·복사를 거쳐도 정보가 남는다.

- 채도 0
- 3단 히트맵 `#EDEDED` / `#A8A8A8` / `#2B2B2B` — 흑백 복사 후에도 3단이 구분되는 간격
- `--accent`는 `#000000`. 흑백에서 "더 무거움"이 곧 강조다
- 그림자 없음, 라운드 4px

### `accent-plan` — 사업기획안

화면·발표 자료를 전제로 채도를 한 단계 올린다.

- 밝은 네이비 `#143A7B`
- `--accent`가 붉은 경고색이 아니라 따뜻한 주황 `#C2621B`. 기획안에서 강조는 *문제 지적*이 아니라 *핵심 제안*을 가리킨다
- 라운드 14px

### `forest-green` — 환경·농정·지역

숲색 `#1F4D3A` + 호박색 표지(▼◆ `#B7791F`). 제목 장식선을 걷고 모서리 10px. 게이트·마일스톤이 주색이 아니라 호박색이라 흐름 속 멈춤 지점이 튄다.

### `academic-serif` — 학술논문·인문사회

버건디 `#6B1E2E`. **명조 제목·왼쪽 정렬·아래 2px 줄**, 캡션도 왼쪽. **강조 상자를 칠하지 않고 외곽선만** — 먹을 덜 쓰고 학술지 도판처럼 읽힌다. 모서리 3px·그림자 없음·뱃지 사각. 강조색은 버건디와 대비되는 짙은 청색 `#1F4E79`.

### `modern-charcoal` — 민간 기획·스타트업·IR

차콜 `#22262E` + 주황 `#F26B1D`. **제목 1.1배·왼쪽·장식 없음**, 히트맵이 주황 계열(공공 파랑 계열과 확연히 갈린다), 뱃지·칩 4px로 각지게.

### `line-minimal` — 선만

슬레이트 `#2D3E50`. 채움색이 거의 흰색이고 강조 상자도 1.5px 외곽선. 칠한 면은 히트맵 3단과 뱃지 반전뿐. 제목 굵기 700. 저가 인쇄·첨부 자료용.

### `teal-lab` — 연구기관·과학기술

청록 `#0E5563`. **배경을 옅은 청회색 패널(`#F4F8F9`)로 깔고** 흰 카드를 띄운다. 모서리 16px·그림자 조금 진하게. 흰 바탕 프리셋과 가장 먼저 구별되는 지점이 바탕이다.

### `report-classic` — 흑백 복사·절제가 우선인 보고서

> v2.0 벤치마크에서 이 프리셋 산출물은 흰 바탕 93%·색 면적 1.7%로, 잘 그린 공공 도식 중앙값(60%·17%)보다 훨씬 휑했다. 컬러로 인쇄되는 보고서에는 `house-report`를 먼저 권한다.

KIEP 원고작성지침(2015)·STEPI 원고 가이드(2018)·국회예산정책처·KISTEP 보고서 실물 관측 + 영국 GSS·Tufte의 절제. 근거는 `benchmark-classic.md`.

- 그림 번호·제목 **위 가운데**, 단위 오른쪽 위, 주·자료 **아래 왼쪽**
- 오피스 계열 회색 5단(`#1A1A1A` `#595959` `#7F7F7F` `#BFBFBF` `#D9D9D9` `#F2F2F2`) + 남색 `#1F3864` + 적색 `#C00000`(한 곳)
- 구조용 강조(헤더·이름표)는 **연회색 + 1px 테두리**, 남색 면은 `highlight` 한 곳만(`--focus-*`)
- 히트맵은 명도만으로 3단 — 흑백 복사를 견딘다
- 모서리·그림자·장식선·중복 번호 0, 좌우 여백을 자르지 않아 **문서 속 그림 폭이 모두 같다**(`--trim-x:none`)

### `exhibit` — 기획·경영·컨설팅 자료

이코노미스트 도판 지침(2017)·젤라즈니 『Say It With Charts』의 **구조**만 빌렸다(특정 매체 모사는 하지 않는다).

- 맨 위 짧은 강조색 막대 하나 → 작고 흐린 그림 번호 → **결론 문장** 제목(왼쪽)
- 회색 중심 + 남색 `#12436D`(GSS 강조 남색) + 적색 `#C8102E`
- 구조용 강조는 흰 바탕 1.5px 외곽선, `highlight` 한 곳만 남색 채움

### 모든 프리셋의 `@image-style`

프리셋 머리 주석의 `@image-style:` 한 줄은 이미지 모델 경로(`gen_image.py`)가 읽는 **분위기 문장**이다. 팔레트·모서리·그림자·강조 방식은 토큰에서 자동으로 뽑고, 토큰으로 못 담는 인상만 이 줄에 영어로 적는다. 새 프리셋을 만들면 이 줄도 쓴다.

## 새 프리셋 만들기

1. `presets/gov-navy.css` 를 복사해 `presets/<이름>.css` 로 저장
2. **값만** 고친다. 토큰 이름·개수는 그대로. 색만 바꾸면 기존 프리셋과 비슷해 보이니 **형태 토큰을 최소 두 개는 다르게** 잡는다
3. 머리 주석에 설계 기준과 `@image-style:` 한 줄을 쓴다
4. 검사

```bash
bash scripts/selftest.sh                                  # 토큰 이름 집합 일치 확인
python3 scripts/render_figure.py examples/matrix-heatmap.json --preset <이름> -o /tmp/t.png
```

`matrix-heatmap` 으로 확인하는 이유는 이 템플릿이 히트맵 3단·기준선 열·범례를 한꺼번에 써서 **토큰을 가장 많이 소비**하기 때문이다. 여기서 멀쩡하면 나머지도 대체로 멀쩡하다.

5. 흑백 계열을 만들었다면 **실제로 흑백 출력해 3단이 구분되는지 확인**한다. 화면에서 구분되는 회색이 종이에서는 뭉개진다.
