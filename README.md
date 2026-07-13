# WFG financial-services playbook

This is a small, file-based content system for turning a family's life stage and self-assessment scores into a focused agent meeting brief. Atomic markdown files hold the source content; YAML frontmatter makes them queryable; Jinja2 renders the same source material into different formats over time.

## Structure

- `content/pillars/` — the five financial pillars and their self-assessment prompts.
- `content/stages/` — life-stage context, conversation openers, likely weak areas, and quick wins.
- `content/objections/` — stage- and pillar-tagged objections with reframes.
- `content/solutions/` — category-level solution guidance, tagged by pillar.
- `templates/` — render targets for a meeting agenda and training stage card.
- `scripts/` — the generator and small loading/model helpers.
- `output/` — generated files (ignored by Git).
- `docs/` — the generated HTML presentation location for GitHub Pages.

## Setup and run

```bash
cd wfg-playbook
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_meeting_agenda.py \
  --stage growing-family \
  --scores protection=red,liquidity=yellow,accumulation=yellow,retirement-income=green,longevity-legacy=green
```

The generator writes `output/{stage}-{timestamp}-agenda.md` and prints the weak pillars plus counts of included objections and solution categories.

## Render a presentation for GitHub Pages

The presentation renderer creates a self-contained HTML deck: no presentation platform, external JavaScript, or CDN is required. It supports arrow keys, on-page controls, responsive viewing, and printing to PDF.

```bash
python scripts/build_presentation.py \
  --stage building \
  --scores protection=yellow,liquidity=yellow,accumulation=yellow,retirement-income=green,longevity-legacy=green
```

By default this writes `docs/index.html`. Commit and push that generated file, then in GitHub open **Settings → Pages**, select **Deploy from a branch**, choose `main`, and select the `/docs` folder. GitHub will publish the deck at the repository's Pages URL. Use `--output path/to/deck.html` to generate a separate local HTML file instead.

## Adding content

Add one Markdown file per item to the relevant `content/` directory. Keep the frontmatter fields consistent with existing examples and put editable prose in the body. The loader turns frontmatter and body into simple Python dataclasses, so the script can filter by stage and pillar without a database.

`templates/stage_card.md.j2` is a second render target for onboarding or training. Render it with the same loaded content, selecting a stage's `likely_weak_pillars`, all stage objections, and matching solutions. New formats such as slides or a client one-pager can use the same loaded content and a new template.

## Design intent

This is deliberately not a static document. Content remains small, reviewable, and easy for non-engineers to refine file by file. As the playbook matures, the source files can serve multiple render targets while preserving a single, queryable content base.
