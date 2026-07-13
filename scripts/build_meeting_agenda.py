#!/usr/bin/env python3
"""Generate a focused agent meeting brief from stage and self-assessment scores."""

import argparse
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from lib.loader import load_content
from lib.models import Objection, Pillar, Solution, Stage

ROOT = Path(__file__).resolve().parent.parent


def parse_scores(raw_scores: str, pillar_ids: set[str]) -> dict[str, str]:
    scores = {}
    for pair in raw_scores.split(","):
        try:
            pillar_id, score = pair.split("=", 1)
        except ValueError as exc:
            raise ValueError(f"Invalid score '{pair}'. Use pillar=red|yellow|green.") from exc
        if pillar_id not in pillar_ids:
            raise ValueError(f"Unknown pillar '{pillar_id}'.")
        if score not in {"red", "yellow", "green"}:
            raise ValueError(f"Invalid score '{score}' for {pillar_id}.")
        scores[pillar_id] = score
    missing = pillar_ids - scores.keys()
    if missing:
        raise ValueError(f"Missing score(s): {', '.join(sorted(missing))}.")
    return scores


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a financial-services meeting agenda.")
    parser.add_argument("--stage", required=True, help="Stage ID, e.g. growing-family")
    parser.add_argument("--scores", required=True, help="Comma-separated pillar=red|yellow|green scores")
    args = parser.parse_args()

    content = ROOT / "content"
    pillars = sorted(load_content(content / "pillars", Pillar), key=lambda item: item.order)
    stages = load_content(content / "stages", Stage)
    objections = load_content(content / "objections", Objection)
    solutions = load_content(content / "solutions", Solution)

    stage = next((item for item in stages if item.id == args.stage), None)
    if stage is None:
        available = ", ".join(sorted(item.id for item in stages))
        parser.error(f"Unknown stage '{args.stage}'. Available: {available}")

    try:
        scores = parse_scores(args.scores, {pillar.id for pillar in pillars})
    except ValueError as exc:
        parser.error(str(exc))

    weak_pillars = [pillar for pillar in pillars if scores[pillar.id] in {"red", "yellow"}]
    stage_objections = [item for item in objections if item.stage == stage.id]
    relevant_solutions = [item for item in solutions if item.pillar in {pillar.id for pillar in weak_pillars}]

    environment = Environment(loader=FileSystemLoader(ROOT / "templates"), trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template("meeting_agenda.md.j2")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = ROOT / "output" / f"{stage.id}-{timestamp}-agenda.md"
    output_path.write_text(template.render(stage=stage, scores=scores, weak_pillars=weak_pillars,
                                           objections=stage_objections, solutions=relevant_solutions), encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"Weak pillars: {', '.join(pillar.name for pillar in weak_pillars) or 'none'}")
    print(f"Objections: {len(stage_objections)} | Solutions: {len(relevant_solutions)}")


if __name__ == "__main__":
    main()
