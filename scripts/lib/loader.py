"""Load markdown content with YAML frontmatter into typed models."""

from dataclasses import fields
from pathlib import Path
from typing import TypeVar

import frontmatter

T = TypeVar("T")


def load_content(content_dir: Path, model: type[T]) -> list[T]:
    """Load every .md file in a flat content directory as ``model`` instances."""
    items: list[T] = []
    for path in sorted(content_dir.glob("*.md")):
        post = frontmatter.load(path)
        data = {field.name: post.metadata[field.name] for field in fields(model) if field.name != "body"}
        data["body"] = post.content.strip()
        items.append(model(**data))
    return items
