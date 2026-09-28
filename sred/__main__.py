"""CLI: `python -m sred evidence ...` and `python -m sred check ...`."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from . import checks, draft, evidence


def cmd_evidence(args: argparse.Namespace) -> int:
    records = evidence.load(args.repo, args.since, args.until)
    stats = evidence.signal_stats(records)
    if args.json:
        print(json.dumps(stats, indent=2))
        return 0
    for key, value in stats.items():
        print(f"{key:>24}  {value}")
    if args.list:
        print()
        for r in records:
            if not r.is_merge:
                print(f"{r.short}  {r.date.date()}  {r.subject}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    parsed = draft.parse(Path(args.draft).read_text())
    index = evidence.EvidenceIndex(evidence.load(args.repo))
    report = checks.check(
        parsed,
        index,
        year_start=args.year_start,
        year_end=args.year_end,
        min_coverage=args.min_coverage,
    )
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"{report.title or '(untitled)'}: {'PASS' if report.passed else 'FAIL'}")
        print(f"  words     {report.metrics['words']}")
        print(f"  coverage  {report.metrics['coverage']}")
        print(f"  citations {report.metrics['citations']} "
              f"(resolved {report.metrics['citation_resolution_rate']})")
        for f in report.findings:
            print(f"  {f.level:<7} line {f.section}  {f.check}: {f.message}")
    return 0 if report.passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sred")
    sub = parser.add_subparsers(dest="command", required=True)

    ev = sub.add_parser("evidence", help="Summarize how much R&D story a git history contains.")
    ev.add_argument("--repo", default=".")
    ev.add_argument("--since")
    ev.add_argument("--until")
    ev.add_argument("--list", action="store_true", help="Also list commits.")
    ev.add_argument("--json", action="store_true")
    ev.set_defaults(func=cmd_evidence)

    ch = sub.add_parser("check", help="Check a draft against the harness.")
    ch.add_argument("draft")
    ch.add_argument("--repo", default=".")
    ch.add_argument("--year-start", type=date.fromisoformat)
    ch.add_argument("--year-end", type=date.fromisoformat)
    ch.add_argument("--min-coverage", type=float, default=checks.DEFAULT_MIN_COVERAGE)
    ch.add_argument("--json", action="store_true")
    ch.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
