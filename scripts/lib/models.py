"""Typed representations of the playbook's atomic content files."""

from dataclasses import dataclass


@dataclass
class Pillar:
    id: str
    name: str
    order: int
    self_score_question: str
    failure_mode: str
    body: str


@dataclass
class Stage:
    id: str
    name: str
    order: int
    description: str
    likely_weak_pillars: list[str]
    opening_line: str
    quick_win: str
    body: str


@dataclass
class Objection:
    id: str
    stage: str
    pillar: str
    objection_text: str
    body: str


@dataclass
class Solution:
    id: str
    pillar: str
    category: str
    body: str
