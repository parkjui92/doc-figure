# doc-figure

**A Claude Code skill that renders diagrams for proposals, official documents, and business plans — with Korean text that never breaks. No API key, no install.**

[한국어 README](README.md) · [MIT License](LICENSE)

---

## Why

Ask an image model for an org chart in a Korean document and you get:

- Hangul labels rendered as **shapes that merely look like Hangul** — malformed jamo, characters that don't exist
- "48억원" coming back as "4B억윈"
- Four divisions requested, three or five delivered
- Table rows and columns that don't line up

Ask for a fix and **something else breaks.** This is structural to diffusion models — no amount of prompting gets past it.

doc-figure inverts the approach: **text, numbers, and alignment are drawn by code.** Strings from the spec land in the DOM verbatim, which makes broken glyphs *structurally impossible* rather than merely unlikely.

This matters most for Korean and other non-Latin scripts, where image models degrade far worse than they do in English.

## 30-second start — nothing to install

```bash
git clone https://github.com/parkjui92/doc-figure.git
```

In Claude Code:

> Using the `doc-figure/` folder, draw an org chart. Lead is the Policy Planning Office; three divisions — Analysis, Reform, Performance; attach an advisory committee.

You get a single self-contained HTML file. Open it in a browser, print to PDF or screenshot, drop it in your document.

With Chrome and Python you can render PNGs directly:

```bash
cd doc-figure
python3 scripts/render_figure.py examples/org-chart.json -o figure_01.png --verify
```

```
[doc-figure] ✓ figure_01.png  (2932x937)  template=org-chart  preset=gov-navy
[verify] ✓ all 20 spec strings present in DOM (zero broken glyphs)
```

## Intent first, shape second

A diagram's shape is itself a claim: a cycle says "there is feedback", a pyramid says "there is hierarchy", a Venn says "these overlap". doc-figure picks the **form** before the color: (1) write the one sentence the reader must take away, (2) classify the relationship (cycle, filtering, overlap, positioning, hierarchy, containment, causes, delta, transition, hand-offs, goal decomposition…), (3) propose 2–3 candidates that show *different* things, (4) `scripts/figure_pack.py` renders each candidate and writes its image-model prompt, bundled in one self-contained `index.html` card page (add `--gpt` for GPT Image renders with OCR checks). See [form-catalog.md](references/form-catalog.md) (Korean).

**14 relationship forms** (`templates/forms.html`): `cycle` `funnel` `venn` `quadrant` `pyramid` `concentric` `hub` `fishbone` `staircase` `before-after` `waterfall` (sum is cross-checked; axis auto-truncated) `iceberg` `swimlane` `logic-tree` — plus the 11 templates below, 25 forms in all.

## 11 templates

| Template | Use |
|---|---|
| `timeline-gantt` | Gantt schedule with gates, milestones, donut KPI |
| `timeline-tracks` | Multi-track chronology (e.g. legislation vs. programs) |
| `flow-process` | Step-by-step process with review gates |
| `decision-flow` | Screening gates with rejection branches and criteria |
| `org-chart` | Governance tree with advisory attachment |
| `structure-block` | Layered system diagram |
| `layer-stack` | Two-tier stack with a bidirectional divider |
| `concept-argument` | Central claim with flanking supporting evidence |
| `comparison-matrix` | Header-and-rows comparison table |
| `matrix-heatmap` | Three-level judgment heatmap against a baseline column |
| `pipe-mapping` | Lane–segment bottleneck mapping with countermeasures |

Rendered previews are in the [Korean README](README.md#템플릿-11종). Every spec lives in [`examples/`](examples/) — copy and edit.

## 8 presets — shape, not just color

Since v1.1 a preset changes more than color: **title style (centered/left, serif option, side rules, underline), emphasis boxes (filled vs. outlined), corner radius, badge shape (circle/square), background panel**. The same spec reads very differently. Previews are in the [Korean README](README.md#프리셋-8벌--색이-아니라-생김새가-바뀐다).

| Preset | For | Look |
|---|---|---|
| `gov-navy` | proposals, research reports | navy, centered title with rules, filled emphasis |
| `mono-formal` | official documents | zero saturation — hierarchy from luminance alone, survives B/W print and fax |
| `accent-plan` | business plans | brighter navy, warm orange accent |
| `forest-green` | environment, agriculture, regional policy | forest green with amber markers |
| `academic-serif` | journal articles | burgundy, **serif left-aligned title with underline, outlined emphasis**, square corners |
| `modern-charcoal` | startup / IR decks | charcoal + vivid orange, large left title, orange heatmap |
| `line-minimal` | cheap printing, attachments | outlines only, almost no fills |
| `teal-lab` | research institutes, data | teal, **white cards on a light panel**, 16px radius |

```bash
python3 scripts/render_figure.py examples/matrix-heatmap.json --preset academic-serif -o out.png
```

## Freeform diagrams

Cycles, funnels, Venns, pyramids — shapes where **the shape is the meaning** — are not forced into the nearest template. The `freeform` template takes HTML or inline SVG and provides token-bound component classes (`ff-*`, SVG `s-*`/`t-*`). `--verify` rejects any `#hex`/`rgb()` in the body so the figure still follows the preset. Examples: `freeform-cycle.json`, `freeform-funnel.json`.

## Image-model path (optional) — the same spec through GPT Image

With an OpenAI key, `scripts/gen_image.py` **designs a structured prompt** from the same spec and preset — layout rules per template, the content as an outline, palette/radius/shadow/emphasis pulled from preset tokens, and an exhaustive list of the only strings allowed in the image — then calls the newest GPT Image model (auto-selected from the API model list, precision variant first; pin with `FIGURE_IMAGE_MODEL`).

```bash
python3 scripts/gen_image.py examples/org-chart.json --preset academic-serif --dry-run        # prompt only, no key
python3 scripts/gen_image.py examples/timeline-gantt.json --preset teal-lab --from-render      # code render as reference
python3 scripts/gen_image.py examples/timeline-gantt.json --fix out.png --instruction "..."   # fix one spot
```

Labels are checked by OCR right after generation (macOS Vision, falling back to tesseract). **Still read every label yourself** — the model is usually right, not structurally unable to be wrong. In September 2026 tests, `gpt-image-2.5-sunburst` got all 121 Korean labels across four figures right, 25–33 s each. The code renderer remains the default.

## Install as a skill

```bash
git clone https://github.com/parkjui92/doc-figure.git ~/.claude/skills/doc-figure
```

Hand it a whole document and it **proposes where figures belong before drawing anything** — you approve, then it renders.

## Verification

```bash
bash scripts/selftest.sh
```

Checks preset token parity (57 tokens × 8 presets), hardcoded colors (hex and rgba) that would escape the preset system, the zero-install HTML path, example schema validity, renders all 13 examples with text verification, freeform color discipline, and designs image-model prompts for every example (no API calls).

> **A `--verify` pass does not mean the figure looks right.** It confirms every string exists in the DOM; it cannot see labels overlapping each other or spilling off-canvas. Always look at the output. (This happened during development, which is why `pipe-mapping` gained per-label lane offsets.)

## Requirements

| Path | Needs |
|---|---|
| Default (HTML) | **Nothing.** A browser. |
| Precise (PNG) | Chrome + Python 3. `pillow` optionally trims whitespace. |
| External APIs | **None** for the default, precise and freeform paths. The image-model path alone needs an OpenAI key. |

Set `CHROME_BIN` if Chrome lives somewhere unusual.

## Not in scope

- **Typesetting body tables** — your word processor does that. This renders diagram images.
- **Photographic illustration** — the image-model path stays within diagrams and infographics.
- **General charting** — use matplotlib for scatter plots and regressions.

## License

MIT.
