# Plan: SR&ED claim drafter (portfolio piece)

Written 2026-09-28. Goal: a portfolio piece that a Canadian hiring manager
recognizes as *their* problem in ten seconds. Graduation May 2028.

**One-line pitch:** turn a startup's git history into a draft of the three
T661 project-description answers (lines 242 / 244 / 246), where every claim
cites the commit or PR it came from, and a public harness proves it.

**Differentiator (why this is not just a worse Boast/AutoDoc):** open,
local-first, and the verification harness is the product. The resume line is
the harness numbers, not "I called an LLM."

---

## Costly-action standard (read this first)

Counts as validation — someone spent time, money, or reputation:

- A founder/CTO/engineering lead runs it on their *private* repo and sends
  back specific feedback (a marked-up draft, a list of wrong citations).
- An SR&ED consultant or someone who has filed a T661 grades ≥10 drafts
  against `docs/rubric.md`.
- A draft (edited) ends up in an actual filed claim.

Null results: stars, "this is cool," signups, likes, "I'll try it later."
Warm-network feedback (friends, family, classmates) needs the higher bar: a
graded rubric, not an opinion.

---

## The five questions

### 1. Dependencies (2 = you control / 1 = priced, documented / 0 = no mechanism)

| Dependency | Score | Note |
|---|---|---|
| Git history of the target repo | 2 | Local `git log`; no API needed. |
| PR / issue text (GitHub API) | 1 | Documented, rate-limited, free tier. Optional input. |
| Generator model | 2 or 1 | Local open-weights model (2) or a hosted API (1). Keep it swappable; model IDs drift. |
| CRA form + guidance | 1 | Public, but revised; re-check each tax year. |
| **A qualified human grader** | **0** | No mechanism yet. **Milestone 1 is converting this to a 1** (see below). |

The harness's automatic checks run without the grader. The *quality* claim
does not. Until the grader is a 1, the resume line can only claim grounding
and format metrics, not "fileable" quality.

Ways to get the grader to a 1: pay an SR&ED consultant for an hour of review
(a priced mechanism); ask a founder in the Canadian startup community to grade
drafts of their own repo in exchange for the draft; find a professor or TA
who has filed SR&ED for a spin-out.

### 2. What do people do today instead?

- CTO/lead writes the narratives by hand, often a week per year, often from
  memory months after the work. *(assumed; common in consultant marketing, not measured)*
- Hire an SR&ED consultant, frequently on contingency. *(assumed)*
- AI-assisted tools already exist: Boast.ai and AutoDoc both advertise
  SR&ED documentation from GitHub/Jira. *(verified they advertise it,
  2026-09-28; shipping quality not checked)*

Switching event (portfolio framing): none needed to *hire you*. What matters
is that the harness shows something the incumbents' marketing doesn't —
grounding numbers.

### 3. Forcing functions (dated)

- **Personal:** summer-2027 internship applications run now → ~Jan 2027;
  new-grad recruiting for May 2028 grads ~Aug–Oct 2027. *(assumed typical
  cycle; check target companies)* → portfolio-ready by **mid-January 2027**
  (end of block 2).
- **Domain:** SR&ED reporting deadline is 18 months after tax-year end for
  corporations. A Dec 31, 2025 year-end files by **June 30, 2027**.
  *(verified via search, see Facts)*

### 4. Does the channel contradict the product?

Product claim: your engineering history is sensitive and stays with you.
Channel: open-source repo + write-up. No telemetry, local-first by default.
No contradiction as long as the default generator can run locally.

### 5. Single point of failure

The human grader (see 1). Absorption: incumbents already do this; that's
fine for a portfolio piece — it proves the problem is real.

---

## Facts

Verified 2026-09-28 via web search of canada.ca pages (direct fetch of
canada.ca was blocked from the build environment — open each page once to
confirm):

| Fact | Source |
|---|---|
| T661 line 242 (uncertainties) 350 words, 244 (work performed in the tax year) 700 words, 246 (advancements) 350 words | [How to write your project description for Form T661](https://www.canada.ca/en/revenue-agency/services/scientific-research-experimental-development-tax-incentive-program/sred-claim/group-projects/project-description-t661.html) |
| Answers should be technical, in the language of those who did the work | same |
| Corporations: 18 months from end of tax year to file | [SR&ED Filing Requirements Policy](https://www.canada.ca/en/revenue-agency/services/scientific-research-experimental-development-tax-incentive-program/filing-requirements-policy.html) |
| 2021 guidelines replaced the "five questions" with "how" and "why" requirements | [Guidelines on the eligibility of work](https://www.canada.ca/en/revenue-agency/services/scientific-research-experimental-development-tax-incentive-program/sred-policies-guidelines/guidelines-eligibility-work-sred-tax-incentives.html) |
| Pre-claim approval process live since April 1, 2026; for eligible businesses under $25M gross income; determination within 8 weeks; uses existing documentation | [CRA tax tip, 2026](https://www.canada.ca/en/revenue-agency/news/newsroom/tax-tips/tax-tips-2026/innovate-confidence-cra-sred-tax-incentive-program-pre-claim-approval-process.html) |
| Budget 2025: enhanced 35% credit expenditure limit $3M → $6M for tax years beginning on/after Dec 16, 2024 | [MNP](https://www.mnp.ca/en/insights/directory/significant-enhancement-announced-sr-ed-program), [PwC Canada](https://www.pwc.com/ca/en/services/tax/publications/tax-insights/sred-changes-2025.html) — secondary sources; confirm legislation passed |

Assumed (with how to check):

- Commit histories contain enough signal to reconstruct uncertainty and
  experimentation. **Check: week-1 disproof test below.** Load-bearing.
- "Difficulty ≠ uncertainty" phrasing lints catch real reviewer objections.
  Check: grader feedback on the first 10 drafts.

**What changed in the last six months:** CRA's pre-claim approval process
(April 2026) asks for planning documentation *before* work starts. That's a
new, dated reason for small companies to write SR&ED-shaped text earlier —
a possible second mode for the tool.

---

## Sequencing

1. **Cheapest disproof (week 1).** Pick 3 public repos from startups with
   plausibly R&D-heavy work. Run `python -m sred evidence` on a 12-month
   window. By hand, try to write line 242 + 244 using *only* commits (then
   commits + PRs). Record where the evidence ran out.
2. **Harness (weeks 1–2).** Done first, in `sred/checks.py`: word limits,
   citation grounding, citation coverage, tax-year window, phrasing lints.
   Human rubric in `docs/rubric.md`.
3. **Thin slice (weeks 3–4).** Generator: evidence → clusters of related
   work → draft markdown with citations. One repo, end to end, ugly.
4. **Public artifact (weeks 5–6).** Write-up + harness numbers on 3 repos +
   grader results if the grader exists yet.
5. **Product polish.** Only after the gate.

## Block 1: Sep 29 – Nov 9, 2026 (part-time)

Numbers are starting placeholders; adjust once, in week 2, then freeze.

| # | Kill criterion (checked at the date) | Earlier tripwire |
|---|---|---|
| K1 | Week 1: for none of 3 repos can a human write a credible line 242 from commits + PRs → the "from git history" premise is dead; pivot inputs to design docs/tickets or kill. | First repo's commits are >70% one-line messages with no body. |
| K2 | Week 4: generated drafts have <90% of citations resolving to real evidence, or <70% of line-244 sentences cited. | First generated draft has any fabricated commit ID. |
| K3 | Week 6: no qualified grader has graded any drafts → downgrade the claim to "grounding + format only" and spend block 2 on converting the grader to a 1. | No reply from the first 3 people asked within 2 weeks. |
| K4 | Week 6: grader rates <30% of drafts "fileable with <15 min of edits". | First 3 graded drafts all "rewrite from scratch." |

## Weaknesses: staging vs kill

| Weakness | Type |
|---|---|
| Incumbents exist (Boast, AutoDoc) | Staging — differentiate on openness + harness |
| No labelled ground truth for "is this SR&ED?" | Staging — rubric + grader |
| Tax-filing output could be treated as advice | Staging — drafts only, always human-reviewed, say so in README |
| Real users' repos are confidential | Staging — local-first, no telemetry |
| Commit history doesn't contain the uncertainty story at all | **Kill fact** for the git-only premise → K1 |

## Checklist

```
[x] Every dependency scored 2 / 1 / 0 — core loop has one 0 (grader); milestone 1 converts it
[x] Current alternative named
[x] Forcing-function dates written down, inside 18 months
[x] Channel doesn't contradict the product's claim
[x] Single point of failure named
[x] Costly-action standard defined before outreach starts
[x] Load-bearing facts marked verified or assumed
[ ] Cheapest disproof test run (week 1)
[x] Verification harness specced before the generator
[x] Kill criteria + earlier tripwires written
[x] Weaknesses labelled staging vs kill
[x] Runs solo, on ~$100/month, through multi-week gaps
```

## Log

- **2026-09-28:** Harness built (13 tests passing). Smoke test on
  Shopify/toxiproxy for 2024: 31 commits, of which 17 were from bots. The 14
  human commits had 36% with a body and a 0% experiment-word share. That's
  pure maintenance, with no R&D story in it. It's a useful negative control,
  and a warning for K1: choose week-1 repos where R&D plausibly happened. Bots
  are now excluded from the stats; before that fix they inflated the
  experiment share to 55% through Dependabot's "compare" links.
