---
name: cortex
description: Explore alternatives with thinking lenses when the user explicitly asks for cortex quick or full cortex, faces an important decision, or brings a problem that has resisted two attempts.
---

# Cortex

Start with a clear problem, its essential outcome, known facts and actual constraints.
Keep confidential material, credentials and unnecessary personal data out of every brief.
An idea is a proposal to test; it never authorizes spending, sending, publishing or changing a system.

## Choose the mode

- **Quick:** read [quick.md](quick.md). Preserve the direct answer, then run three to five lenses in one fresh agent that has not seen the draft. Present up to three useful alternatives after the direct answer.
- **Full:** read [full.md](full.md). Run all 24 core lenses and any relevant additional lenses, one isolated agent per lens. Cultivate every idea and deliver the complete page before selection.

In Full, a separate baseline agent writes the competent, obvious answer first.
Each lens agent sees only the problem brief and its own file from `lenses/`.
Transformative lenses also receive the independent baseline, as specified in full.md.
Agents must not see other lenses' outputs. Do not rank, merge away or discard ideas during generation.
If separate agents are unavailable, say **“not independently generated”** and describe the actual fallback; never claim a Full independent run.

## Every idea has a shape

- **Title · lens:** name the move and the lens that produced it.
- **Before / After:** show what changes relative to the competent baseline.
- **Kept intact:** list the essential outcome dimensions preserved.
- **New operation it enables:** required for a representation change; name an operation previously unavailable. Renaming or weakening the goal does not count.
- **Cheapest test:** give the smallest observation that distinguishes the proposed mechanism from the baseline.
- **Drop it if:** state an observable stopping condition.

Develop the mechanism, dependencies, available means and breaking point before judging it.
For analogies, include the origin field, transferred relationship and where the mapping breaks.
Separate facts, hypotheses and missing evidence. Check decision-changing external claims against primary evidence when tools permit; otherwise mark them unverified.

## Selection comes before stress

Show the complete Full page, including premises, conditional routes, originals and variants.
Stress-test only the ideas the user selects, or those you select under explicit delegation.
Read the relevant files in `checks/`; report strongest objection, cost, uncertainty and next test.
Do not infer a selection from silence or simulate the user's preferences.

## Optional tools and path resolution

All script paths below are relative to the directory containing this `SKILL.md`,
not the host's current working directory. Resolve the installed skill directory
first, then invoke the script by its absolute path (quote paths containing spaces):

```sh
python3 "<absolute-skill-directory>/scripts/check.py"
python3 "<absolute-skill-directory>/scripts/page.py" "<run.json-path>" --out "<run.html-path>"
```

`check.py` checks the editable files. `page.py` renders the complete run without
calling a model. Resolve input and output paths separately; relative run paths
are interpreted from the caller's working directory, not the skill directory.
