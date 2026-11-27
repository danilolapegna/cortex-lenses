# Quick · a cold second look

Use this when there is already a direct answer worth checking. It adds one agent call;
it does not run the Full search.

1. Preserve the complete direct answer. Use a separately produced baseline if one already exists; otherwise the direct-answer agent supplies the baseline and a different agent runs the cold round.
2. Prepare a neutral brief: objective, essential invariants, verified facts, constraints and resources. Omit the draft, favored solution and hints about its framing.
3. Choose three to five files from `lenses/` for distinct missing moves. Favor a premise challenge, a transfer, subtraction, a reversal or a representation change as the problem warrants.
4. Give the brief and those files to one fresh agent. It applies each lens separately without evaluating earlier ideas. Return at most six cards in the shape in SKILL.md; a lens may yield none.
5. Only after generation, compare the cards with the preserved answer. Deliver the complete direct answer first, then up to three alternatives that materially change what to do, with cheapest test and stopping condition. A worse alternative never displaces the answer. It is fine to return no useful alternative.
6. Keep the remaining cards available in the conversation. Stress-test only a selected idea, using the relevant files in `checks/`.

Do not give the cold agent the draft, even later during generation. Baseline-dependent
lenses such as `the-common-barrier.md` need a different brief: use an already independent
baseline, or choose another lens to preserve Quick's one-extra-call and cold-context limits.

If the host cannot create a fresh context, finish the direct answer and label the
same-context alternatives **“not independently generated; not a cold round.”**
Do not silently expand Quick into dozens of calls. An idea authorizes no action.
