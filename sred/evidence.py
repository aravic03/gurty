"""Turn a git repository's history into evidence records a draft can cite."""

from __future__ import annotations

import re
import statistics
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"
LOG_FORMAT = RECORD_SEP + FIELD_SEP.join(["%H", "%P", "%an", "%aI", "%s", "%b"]) + FIELD_SEP

# Heuristic only: words that suggest experimentation rather than routine work.
# Used for the week-1 "is the signal in the history?" test, never for eligibility.
EXPERIMENT_WORDS = re.compile(
    r"\b(experiment\w*|benchmark\w*|prototype\w*|spike|investigat\w*|attempt\w*|"
    r"hypothes\w*|ablation|evaluat\w*|compar\w*|tried|trying|approach|latency|"
    r"throughput|accuracy|regression)\b",
    re.IGNORECASE,
)

# Dependency bots write long bodies full of "compare" links; they'd swamp the stats.
BOT_AUTHORS = re.compile(r"\[bot\]|^(dependabot|renovate|github-actions)\b", re.IGNORECASE)


@dataclass
class Evidence:
    sha: str
    parents: list[str]
    author: str
    date: datetime
    subject: str
    body: str
    files: list[str] = field(default_factory=list)
    insertions: int = 0
    deletions: int = 0

    @property
    def short(self) -> str:
        return self.sha[:7]

    @property
    def is_merge(self) -> bool:
        return len(self.parents) > 1

    @property
    def is_revert(self) -> bool:
        return self.subject.lower().startswith("revert")

    @property
    def is_bot(self) -> bool:
        return bool(BOT_AUTHORS.search(self.author))

    @property
    def text(self) -> str:
        return f"{self.subject}\n{self.body}".strip()


def _parse_numstat(block: str) -> tuple[list[str], int, int]:
    files, ins, dels = [], 0, 0
    for line in block.strip().splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, removed, path = parts
        files.append(path)
        # Binary files report "-" for both counts.
        ins += int(added) if added.isdigit() else 0
        dels += int(removed) if removed.isdigit() else 0
    return files, ins, dels


def parse_log(raw: str) -> list[Evidence]:
    records = []
    for chunk in raw.split(RECORD_SEP):
        if not chunk.strip():
            continue
        sha, parents, author, date, subject, body, numstat = chunk.split(FIELD_SEP, 6)
        files, ins, dels = _parse_numstat(numstat)
        records.append(
            Evidence(
                sha=sha,
                parents=parents.split(),
                author=author,
                date=datetime.fromisoformat(date),
                subject=subject.strip(),
                body=body.strip(),
                files=files,
                insertions=ins,
                deletions=dels,
            )
        )
    return records


def load(repo: str | Path, since: str | None = None, until: str | None = None) -> list[Evidence]:
    cmd = ["git", "-C", str(repo), "log", "--numstat", f"--pretty=format:{LOG_FORMAT}"]
    if since:
        cmd.append(f"--since={since}")
    if until:
        cmd.append(f"--until={until}")
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    return parse_log(out)


class EvidenceIndex:
    """Resolves citation ids (any unique sha prefix of 7+ chars) to evidence."""

    def __init__(self, records: list[Evidence]):
        self.records = records

    def resolve(self, ref: str) -> list[Evidence]:
        ref = ref.lower()
        return [r for r in self.records if r.sha.startswith(ref)]


def signal_stats(records: list[Evidence]) -> dict:
    """How much story is in this history? Numbers for the week-1 disproof test."""
    non_merge = [r for r in records if not r.is_merge]
    commits = [r for r in non_merge if not r.is_bot]
    n = len(commits)
    if n == 0:
        return {"commits": 0, "bot_commits": len(non_merge)}
    return {
        "commits": n,
        "bot_commits": len(non_merge) - n,
        "merges": len(records) - len(non_merge),
        "authors": len({r.author for r in commits}),
        "with_body": round(sum(bool(r.body) for r in commits) / n, 3),
        "median_subject_words": statistics.median(len(r.subject.split()) for r in commits),
        "median_body_words": statistics.median(len(r.body.split()) for r in commits),
        "reverts": sum(r.is_revert for r in commits),
        "experiment_word_share": round(
            sum(bool(EXPERIMENT_WORDS.search(r.text)) for r in commits) / n, 3
        ),
        "first": min(r.date for r in commits).date().isoformat(),
        "last": max(r.date for r in commits).date().isoformat(),
    }
