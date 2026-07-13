#!/usr/bin/env python3
"""Render a self-contained HTML slide deck for GitHub Pages or any web server."""

import argparse
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from build_meeting_agenda import parse_scores
from lib.loader import load_content
from lib.models import Objection, Pillar, Solution, Stage

ROOT = Path(__file__).resolve().parent.parent


def chunks(items: list[Solution], size: int) -> list[list[Solution]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a GitHub Pages-ready HTML presentation.")
    parser.add_argument("--stage", required=True, help="Stage ID, e.g. building")
    parser.add_argument("--scores", required=True, help="Comma-separated pillar=red|yellow|green scores")
    parser.add_argument("--output", type=Path, default=ROOT / "docs" / "index.html",
                        help="HTML destination (default: docs/index.html)")
    args = parser.parse_args()

    content = ROOT / "content"
    pillars = sorted(load_content(content / "pillars", Pillar), key=lambda item: item.order)
    stages = load_content(content / "stages", Stage)
    objections = load_content(content / "objections", Objection)
    solutions = load_content(content / "solutions", Solution)
    stage = next((item for item in stages if item.id == args.stage), None)

    if stage is None:
        parser.error(f"Unknown stage '{args.stage}'. Available: {', '.join(sorted(item.id for item in stages))}")
    try:
        scores = parse_scores(args.scores, {pillar.id for pillar in pillars})
    except ValueError as exc:
        parser.error(str(exc))

    weak_pillars = [pillar for pillar in pillars if scores[pillar.id] in {"red", "yellow"}]
    stage_objections = [item for item in objections if item.stage == stage.id]
    relevant_solutions = [item for item in solutions if item.pillar in {pillar.id for pillar in weak_pillars}]

    environment = Environment(loader=FileSystemLoader(ROOT / "templates"), trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template("presentation.html.j2")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(template.render(
        stage=stage,
        scores=scores,
        weak_pillars=weak_pillars,
        objections=stage_objections,
        solution_groups=chunks(relevant_solutions, 4),
    ), encoding="utf-8")

    print(f"Generated presentation: {args.output}")
    print(f"Slides: {3 + len(weak_pillars) + bool(stage_objections) + len(chunks(relevant_solutions, 4))}")
    print(f"Weak pillars: {', '.join(pillar.name for pillar in weak_pillars) or 'none'}")


if __name__ == "__main__":
    main()
