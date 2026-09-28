"""Deterministic checks on a draft. Errors fail the draft; warnings go to the human grader.

These checks decide what "correct" means *before* any generator exists. They can
prove a draft is grounded and well-formed. They cannot prove it is fileable —
that needs the human rubric in docs/rubric.md.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import date

from .draft import SECTIONS, WORD_LIMITS, Draft
from .evidence import EvidenceIndex

DEFAULT_MIN_COVERAGE = 0.7

# Phrasing that reviewers commonly push back on. Heuristic warnings, not rules.
PHRASE_LINTS = {
    "difficulty-not-uncertainty": (
        r"\b(difficult|challenging|complex|hard to|not sure (if|whether)|weren'?t sure)\b",
        "Describes difficulty, not a technological uncertainty. Say what was unknown "
        "and why existing knowledge couldn't resolve it.",
    ),
    "business-uncertainty": (
        r"\b(market|customers?|revenue|sales|pricing|business case)\b",
        "Business or market uncertainty is not technological uncertainty.",
    ),
    "marketing-language": (
        r"\b(cutting[- ]edge|state[- ]of[- ]the[- ]art|revolutionary|world[- ]class|"
        r"best[- ]in[- ]class|game[- ]chang\w*|innovative)\b",
        "Marketing language. Replace with the specific technical claim.",
    ),
    "routine-work": (
        r"\b(bug ?fix\w*|refactor\w*|upgrad\w*|migrat\w*|bump\w*|UI tweaks?)\b",
        "May read as routine engineering. Tie it to the uncertainty it tested, or cut it.",
    ),
}


@dataclass
class Finding:
    level: str  # "error" | "warning"
    check: str
    section: str
    message: str


@dataclass
class Report:
    title: str
    findings: list[Finding]
    metrics: dict

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "passed": self.passed,
            "metrics": self.metrics,
            "findings": [asdict(f) for f in self.findings],
        }


def check(
    draft: Draft,
    index: EvidenceIndex,
    year_start: date | None = None,
    year_end: date | None = None,
    min_coverage: float = DEFAULT_MIN_COVERAGE,
) -> Report:
    findings: list[Finding] = []
    metrics: dict = {"words": {}, "coverage": {}}
    cited = resolved = 0

    for line in SECTIONS:
        section = draft.sections.get(line)
        if section is None or not section.text:
            findings.append(Finding("error", "missing-section", line, f"Line {line} is missing or empty."))
            continue

        # Word limit.
        metrics["words"][line] = section.words
        if section.words > WORD_LIMITS[line]:
            findings.append(
                Finding(
                    "error",
                    "word-limit",
                    line,
                    f"{section.words} words; CRA limit for line {line} is {WORD_LIMITS[line]}.",
                )
            )

        # Grounding: every citation must resolve to exactly one commit.
        for ref in section.citations:
            cited += 1
            matches = index.resolve(ref)
            if not matches:
                findings.append(Finding("error", "unresolved-citation", line, f"[{ref}] matches no commit."))
                continue
            if len(matches) > 1:
                findings.append(
                    Finding("error", "ambiguous-citation", line, f"[{ref}] matches {len(matches)} commits.")
                )
                continue
            resolved += 1
            # Line 244 asks for work performed *in the tax year*.
            if line == "244" and year_start and year_end:
                day = matches[0].date.date()
                if not (year_start <= day <= year_end):
                    findings.append(
                        Finding(
                            "error",
                            "outside-tax-year",
                            line,
                            f"[{ref}] is dated {day}, outside {year_start}..{year_end}.",
                        )
                    )

        # Coverage: share of sentences backed by at least one citation.
        n = len(section.sentences)
        coverage = sum(bool(s.citations) for s in section.sentences) / n if n else 0.0
        metrics["coverage"][line] = round(coverage, 3)

        for name, (pattern, advice) in PHRASE_LINTS.items():
            for s in section.sentences:
                if m := re.search(pattern, s.plain, re.IGNORECASE):
                    findings.append(Finding("warning", name, line, f'"{m.group(0)}": {advice}'))

    # Work performed is the section that must be evidenced line by line.
    if "244" in metrics["coverage"] and metrics["coverage"]["244"] < min_coverage:
        findings.append(
            Finding(
                "error",
                "low-coverage",
                "244",
                f"{metrics['coverage']['244']:.0%} of line-244 sentences cite evidence; "
                f"minimum is {min_coverage:.0%}.",
            )
        )

    metrics["citations"] = cited
    metrics["citation_resolution_rate"] = round(resolved / cited, 3) if cited else None
    return Report(title=draft.title, findings=findings, metrics=metrics)
