"""Parse a draft T661 project description written in markdown.

Expected shape:

    # Project: <title>
    ## Line 242
    Text with citations like [a1b2c3d] or [a1b2c3d, 9f8e7d6].
    ## Line 244
    ...
    ## Line 246
    ...
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

SECTIONS = ("242", "244", "246")

# CRA word limits per line, verified 2026-09-28 (see PLAN.md, Facts).
WORD_LIMITS = {"242": 350, "244": 700, "246": 350}

SECTION_HEADING = re.compile(r"^##\s*Line\s*(\d{3})\b", re.IGNORECASE)
TITLE_HEADING = re.compile(r"^#\s*Project:\s*(.+)$", re.IGNORECASE)
CITATION = re.compile(r"\[\s*([0-9a-fA-F]{7,40}(?:\s*,\s*[0-9a-fA-F]{7,40})*)\s*\]")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


@dataclass
class Sentence:
    text: str
    citations: list[str]

    @property
    def plain(self) -> str:
        return strip_citations(self.text)


@dataclass
class Section:
    line: str
    text: str = ""
    sentences: list[Sentence] = field(default_factory=list)

    @property
    def words(self) -> int:
        # Citations are removed before filing, so they don't count toward the limit.
        return len(strip_citations(self.text).split())

    @property
    def citations(self) -> list[str]:
        return [c for s in self.sentences for c in s.citations]


@dataclass
class Draft:
    title: str
    sections: dict[str, Section]


def strip_citations(text: str) -> str:
    # Take the space before a citation too, so "done [abc1234]." leaves "done." not "done ."
    return re.sub(r"\s+", " ", re.sub(r"\s*" + CITATION.pattern, "", text)).strip()


def _citations(text: str) -> list[str]:
    return [ref.strip().lower() for m in CITATION.finditer(text) for ref in m.group(1).split(",")]


def _sentences(text: str) -> list[Sentence]:
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = " ".join(line.strip().lstrip("-*").strip() for line in para.splitlines())
        for piece in SENTENCE_END.split(para):
            piece = piece.strip()
            if piece:
                out.append(Sentence(text=piece, citations=_citations(piece)))
    return out


def parse(markdown: str) -> Draft:
    title = ""
    sections: dict[str, Section] = {}
    current: Section | None = None
    lines: list[str] = []

    def flush():
        if current is not None:
            current.text = "\n".join(lines).strip()
            current.sentences = _sentences(current.text)

    for line in markdown.splitlines():
        if m := TITLE_HEADING.match(line):
            title = m.group(1).strip()
        elif m := SECTION_HEADING.match(line):
            flush()
            current = sections.setdefault(m.group(1), Section(line=m.group(1)))
            lines = []
        elif line.startswith("#"):
            flush()
            current = None
        elif current is not None:
            lines.append(line)
    flush()
    return Draft(title=title, sections=sections)
