# 문제 해결

## 크롬을 찾을 수 없다

```
[doc-figure] 크롬을 찾을 수 없음: /Applications/Google Chrome.app/...
```

경로를 지정하거나, 크롬 없이 HTML만 만든다.

```bash
export CHROME_BIN="/path/to/chrome"
# 또는
python3 scripts/render_figure.py spec.json --html-only -o figure.html
```

리눅스에서는 `chromium`·`google-chrome-stable` 등이 흔하다. `which chromium` 으로 찾는다.

## `--verify` 가 실패한다

```
[verify] ✗ DOM 미출력 텍스트 3건:
   - 성과관리 규정 신설
```

spec에 쓴 문자열이 렌더 결과에 없다는 뜻이다. 대개 원인은 셋 중 하나다.

1. **템플릿이 그 필드를 안 읽는다** — 스키마에 없는 키를 넣었다. [스키마](../references/template-schemas.md) 확인
2. **배열 길이가 안 맞는다** — 예: `matrix-heatmap` 의 `cells` 개수가 `columns` − 1 이 아니면 초과분이 렌더되지 않는다
3. **조건부 블록이 꺼져 있다** — 상위 필드(`footer`·`legend` 등)가 없으면 하위도 안 그려진다

## 렌더는 됐는데 글자가 겹친다

**`--verify` 는 이걸 못 잡는다.** 텍스트의 *존재*만 확인하기 때문이다.

| 증상 | 손볼 곳 |
|---|---|
| `pipe-mapping` 병목 라벨이 가로로 겹침 | 블록마다 `_lane` 을 0,1,2…로 다르게 |
| `timeline-tracks` 노드 박스가 겹침 | 노드마다 `_lane` 을 다르게 |
| `timeline-tracks` 어절이 중간에 끊김 ("시행령 전부개/정") | `_w` 를 키운다. 박스는 연도 라벨과 본문이 폭을 나눠 쓴다 |
| `matrix-heatmap` 행이 오른쪽으로 밀림 | `cells` 개수 = `columns` 개수 − 1 인지 확인 |
| 전반적으로 빽빽함 | `layout` 의 폭 값을 키운다 |

## 흑백으로 출력했더니 구분이 안 된다

`gov-navy` 로 그린 그림을 흑백 프린터에 넣으면 네이비 3단이 비슷한 회색으로 뭉개진다. **`mono-formal`을 쓴다** — 명도 차만으로 위계를 만들도록 설계된 프리셋이다.

```bash
python3 scripts/render_figure.py spec.json --preset mono-formal -o out.png
```

새 흑백 프리셋을 직접 만든다면 **실제로 흑백 출력해서** 확인한다. 화면에서 구분되는 회색이 종이에서는 뭉개진다.

## 한글(.hwp)에 넣었더니 그림이 깨졌다

HTML이나 다른 문서에서 **복사–붙여넣기 하지 않는다.** 개체가 손상된다.

PNG로 저장한 뒤 한글의 `입력 → 그림`으로 넣는다. 여러 장이면 그림번호·파일경로·삽입 위치를 적은 삽입 가이드를 함께 두면 작업이 빨라진다.

## 폰트가 다르게 나온다

프리셋의 `--font` 는 `Apple SD Gothic Neo` → `NanumSquare` → `NanumGothic` → `Malgun Gothic` 순으로 폴백한다. 셋 다 없는 환경에서는 시스템 기본 산세리프로 떨어진다.

리눅스라면 나눔 계열을 설치한다.

```bash
sudo apt install fonts-nanum        # Debian/Ubuntu
```

**프리셋마다 폰트를 다르게 두지 않는다.** 어떤 프리셋에서만 글자가 깨지는 상황은 재현도 원인 추적도 어렵다.

## 여백이 안 잘린다

`pillow` 가 없으면 여백 자동 trim이 생략된다(렌더 자체는 성공한다).

```bash
pip3 install --user pillow
```

## 자체검사가 실패한다

```bash
bash scripts/selftest.sh
```

| 실패 항목 | 뜻 |
|---|---|
| ① 프리셋 토큰 불일치 | 프리셋 간 토큰 이름이 다르다. 하나에만 추가하고 나머지를 빠뜨렸을 때 |
| ② 하드코딩 색 | 템플릿에 `var(--토큰)` 아닌 색이 있다. 그 자리는 프리셋을 무시한다 |
| ③ 설치 0 경로 | HTML에 외부 요청(`src="http…"`)이 섞였다. 자기완결이 깨진다 |
| ④ 예시 스키마 | 예시가 없는 템플릿·프리셋을 가리킨다 |
| ⑤ 렌더 검증 | 위의 `--verify` 실패 항목 참고 |
