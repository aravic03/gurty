# SR&ED claim drafter

Canadian startups claim the SR&ED tax credit every year, and someone (usually
the CTO) spends days reconstructing the R&D story for Form T661 from memory.
This project drafts the three project-description answers from the git
history instead, and **every claim cites the commit it came from**.

Status: **verification harness only.** Following [PLAN.md](PLAN.md), the checks
that decide whether a draft is correct come before the generator does.

> Drafts are for a qualified person to review and edit. This tool does not
> give tax advice and never files anything.

## What's here

| Path | What |
|---|---|
| `sred/evidence.py` | Reads `git log` into evidence records; signal stats for the week-1 test |
| `sred/draft.py` | Parses a draft in markdown with `[commit]` citations |
| `sred/checks.py` | Automatic checks: CRA word limits, citation grounding, tax-year window, line-244 coverage, phrasing lints |
| `docs/rubric.md` | Human grading rubric and the primary metric (fileable-with-light-edits rate) |
| `PLAN.md` | Dependencies, facts (verified vs assumed), kill criteria, 6-week block |

## Usage

```bash
pip install -e ".[dev]"
pytest

# How much R&D story is in this history? (bots excluded)
python -m sred evidence --repo ../some-repo --since 2025-01-01 --until 2025-12-31 --list

# Check a draft against the harness; exits 1 on any error
python -m sred check draft.md --repo ../some-repo \
  --year-start 2025-01-01 --year-end 2025-12-31
```

Draft format:

```markdown
# Project: Sub-10ms vector search on commodity hardware
## Line 242
It was unknown whether ... [a1b2c3d]
## Line 244
We first tested ... [9f8e7d6, 1a2b3c4]
## Line 246
We established that ... [5e6f7a8]
```

## Checks

| Check | Level | Why |
|---|---|---|
| Missing section | error | T661 needs all three lines |
| Word limit (242: 350, 244: 700, 246: 350) | error | CRA limits; citations don't count |
| Unresolved / ambiguous citation | error | A made-up commit is a made-up claim |
| Line-244 citation outside the tax year | error | Line 244 asks for work done *in the tax year* |
| Line-244 coverage below threshold (default 70%) | error | Work performed must be evidenced sentence by sentence |
| Difficulty, business, marketing, routine-work phrasing | warning | Common reasons reviewers push back; routed to the human grader |
