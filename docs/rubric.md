# Human grading rubric

The automatic checks (`python -m sred check`) prove a draft is **grounded** and
**well-formed**. They can't prove it is **fileable**. That takes a person who
has written or reviewed T661 claims.

## Primary metric

**Fileable-with-light-edits rate:** the share of drafts a qualified grader
says they would file after less than 15 minutes of editing. This is fixed
before the generator exists, like "merged without rework" for code.

Report it with the number of drafts and graders. "7/10 drafts, 1 grader" is
honest; "70%" alone is not.

## Who counts as a qualified grader

Someone who has written, filed, or reviewed at least one T661 claim: an SR&ED
consultant, a founder or CTO who has filed, or a former CRA reviewer. Friends and
classmates don't count, however helpful they are (see PLAN.md, costly-action
standard).

## Per-draft questions

Answer each on a 1–5 scale and add one sentence explaining the score.

| # | Question | 1 | 5 |
|---|---|---|---|
| 1 | **Uncertainty (line 242):** does it say what was technologically unknown at the start, and why standard practice couldn't resolve it? | Describes difficulty or business goals | A reviewer would accept it as stated |
| 2 | **Systematic investigation (line 244):** does it show hypotheses, tests, results, and changes of direction in order? | A list of features built | A clear experiment log |
| 3 | **Advancement (line 246):** does it state what new knowledge was gained, including negative results? | Restates the product | Specific knowledge that didn't exist before |
| 4 | **Faithfulness:** open 5 random citations. Does each commit actually support its sentence? | Most don't | All do |
| 5 | **Selection:** did it choose the right work, leaving routine engineering out? | Mostly routine work | The work you'd have picked |

Final question: **would you file this after less than 15 minutes of edits?** Yes / No.

## Recording results

Put one JSON line per draft in `results/grades.jsonl`:

```json
{"draft": "drafts/repo-x-2025.md", "grader": "g1", "scores": [4, 3, 4, 5, 3], "fileable": true, "notes": "..."}
```
