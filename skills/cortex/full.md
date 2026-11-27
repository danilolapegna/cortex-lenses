# Full · generate, cultivate, choose, test

1. Freeze a neutral problem brief: the user's words, essential outcome, constraints, resources, known facts and verified failed attempts. Separate assumptions and unknowns from facts. Remove confidential material.
2. Ask one separate agent for the competent, obvious answer to that brief. It sees no lenses. Preserve its answer as the baseline.
3. Read the frontmatter in `lenses/`. Run every file with `core: true`, plus relevant additional lenses. Give each its own isolated agent with only the brief and that lens file. Do not share other outputs. The transformative lenses `challenge-assumptions`, `mutation-checklist`, `subtraction` and `the-common-barrier` also receive the baseline. The common-barrier agent receives the verified failed attempts too.
4. Generate without ranking or discarding. Each agent returns idea cards in the SKILL.md shape, or an explicit no-idea result with the attempted transformation. No novelty quota ends the search early. If separate agents are unavailable, label the output “not independently generated”; report the missing isolation rather than claiming a Full independent run.
5. Inspect primary evidence for decision-changing claims in the problem and any newly explored domain. Keep claim, URL, access date and limits with the idea; unavailable evidence stays unverified. Do not invent precedents or measured results.
6. Cultivate every mechanism family before judging: explain causal interaction, decisive dependency, obtainable means, breaking point and first test. A grouping may link related ideas but must preserve every original, condition and variant. Keep explicit premises and uncomfortable routes in separate sections.
7. Deliver all ideas on one page, in a stable order unrelated to merit. Use the JSON shape below and optionally scripts/page.py. Retain every lens result, including no-idea results. A requested shortlist may also appear in chat, but never replaces the complete page.
8. Wait for the user's selection. Only explicit selection or delegated choice starts stress testing. Strengthen the selected idea before attacking it; use the relevant files in checks/, including the strongest objection, rival response, fragile assumption and reversibility where applicable.
9. Compare outcome, fully loaded human effort, agent work, spending, time to first signal and effects on others separately. State unknowns. Verify rights, privacy, permissions and potential harm before any proposed action. Finish with a bounded test, owner, evidence trigger and stopping rule. Selection grants no permission to execute.

## Run JSON

UTF-8 JSON object. Strings below are required and nonempty unless stated otherwise.
No fields are truncated by the renderer. Use plain text, never raw HTML.

- `title`, `problem`, `baseline`: strings.
- `independence`: string describing what contexts actually ran and any isolation gap.
- `lens_results`: one object per executed lens: `lens` (file stem), `status` (`ideas` or `none`), `note` (what was tried or any limitation).
- `ideas`: every original card, with unique `id`, `title`, `lens`, `section` (`ideas`, `premises` or `conditional`), `before`, `after`, `kept_intact`, `mechanism`, `dependency`, `means`, `breaking_point`, `cheapest_test`, `drop_it_if`.
- `new_operation`: required on representation-change cards; omit on other cards.
- Optional card fields: `variants` (list of strings), `evidence` (list of strings recording inspected claims, links, dates and limits), `analogy` (origin field, transferred relationship and breaking point as a string).
- Optional `selected`: list of idea IDs explicitly selected by the user or under delegation; default empty. `selection_note` (string) records who selected and why. A nonempty selection requires this note.
- Optional `stress_tests`: list of objects, each with `idea_id` from `selected`, `checks` (nonempty list of check file stems), `finding`, `cost`, `next_test`, `owner`, `stop_if` (nonempty strings). Empty until selection.

Every idea must point to a lens result marked `ideas`; a `none` result has no cards.
The renderer checks internal completeness; only the host can establish that every required
lens was actually run independently. Never use a JSON example as proof of an independent run.

From the repository root:

```sh
python3 skills/cortex/scripts/page.py examples/full-run.json --out examples/full-run.html
```

The included example is a synthetic rendering fixture, not a measured outcome.
The renderer writes a standalone, offline HTML page with the baseline, every card,
variants, lens coverage and any selected stress tests. It does not run agents or send data.
