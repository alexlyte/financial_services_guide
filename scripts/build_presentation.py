#!/usr/bin/env python3
"""Render a self-contained, client-facing HTML slide deck for GitHub Pages."""

import argparse
from collections import defaultdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from lib.loader import load_content
from lib.models import ChecklistQuestion, Pillar, Stage

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a GitHub Pages-ready HTML presentation.")
    parser.add_argument("--output", type=Path, default=ROOT / "docs" / "index.html",
                        help="HTML destination (default: docs/index.html)")
    args = parser.parse_args()

    content = ROOT / "content"
    pillars = sorted(load_content(content / "pillars", Pillar), key=lambda item: item.order)
    stages = sorted(load_content(content / "stages", Stage), key=lambda item: item.order)
    questions = load_content(content / "checklists", ChecklistQuestion)

    pillar_order = {pillar.id: pillar.order for pillar in pillars}
    pillar_names = {pillar.id: pillar.name for pillar in pillars}
    questions_by_stage = defaultdict(list)
    for question in questions:
        questions_by_stage[question.stage].append(question)
    for stage_questions in questions_by_stage.values():
        stage_questions.sort(key=lambda item: pillar_order.get(item.pillar, 99))

    environment = Environment(loader=FileSystemLoader(ROOT / "templates"), trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template("presentation.html.j2")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(template.render(
        stages=stages,
        pillars=pillars,
        pillar_names=pillar_names,
        questions_by_stage=questions_by_stage,
    ), encoding="utf-8")

    slide_count = 1 + len(stages) + len(questions)
    print(f"Generated presentation: {args.output}")
    print(f"Stages: {len(stages)} | Questions: {len(questions)} | Slides: {slide_count}")


if __name__ == "__main__":
    main()
