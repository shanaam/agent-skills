# ADR practice

Read this at the ADR review gate, at every end-of-phase ADR check, and before drafting any ADR or addendum.

## Why ADRs carry more weight now

Agents read the repository's documents as their long-term memory.
An ADR that records a rejected alternative stops a later session from re-proposing it, and an ADR that records a constraint stops a plan from quietly violating it.
That makes the decision log part of the codebase's safety net, not an afterthought.
Rationale that lives only in a conversation is a debt the next reader pays, human or agent, and the ADR is where it is repaid.

## Finding the existing set

- Look under `docs/adr/`, `docs/decisions/`, `architecture/decisions/`, and search the repo for `ADR-` and `adr`.
- Read the index first when one exists; it tells you the numbering scheme, the families, and any historical id mapping.
- Read the ADRs most likely to constrain the plan in full, not by title, and record the findings inline under the gate checkbox.
- Status decides weight: an accepted ADR is binding, a proposed one is context the plan names as unaccepted, and a superseded one is history.
- When the task and an accepted ADR conflict, stop and raise it with the user as a choice between changing the task and amending the ADR; do not layer a workaround that keeps both technically true.
  An agent that keeps an obsolete abstraction because an old ADR called it mandatory, and adds another layer to stay compatible, has over-enforced the record, and the record exists to be questioned when it no longer fits.

## Writing one

- Use the repo's own template when it has one; otherwise use the minimal shape below.
- Status starts at Proposed; only the author moves it to Accepted, and only after reading it.
- Assign the number at write time, after re-reading the index, because a number chosen at planning time collides with ADRs written in the meantime by other sessions or branches.
- Check for duplicate numbers across the family while there; collisions happen when branches land out of order, and a collision found is a finding for the author, not something to fix silently.
- Never reuse a number, even for a superseded or absorbed ADR.
- Name the qualities the decision serves and the criteria the options were judged against before naming the options, so the rationale is not reverse-engineered from the winner.
- Record at least two options; a record with one option is not a decision.
- Record rejected alternatives and the reason for each; that is the part a future reader cannot reconstruct.
- Record the negative consequences as well as the positive; a record with none is incomplete, and only the non-obvious consequences are worth the reader's time.
- Add a "Revisit if" section naming the signals that should reopen the decision.
- Keep implementation detail out; a record of a single implementation-level design is not a decision record.
- The record carries no agent attribution; it reads as the team's decision, in the author's voice, or with no author at all when the repo's template has no such field.
- An agent-drafted record or addendum is a suggestion until the user has read every line and changed what does not match their reasoning; the agent queues it under Awaiting the author with the draft's location, never moves its status, and treats a rationale it inferred from the code rather than from the conversation as the part most likely to be wrong.
- Keep it free of any reference to the implementation plan or its phases.

## Amending one

- When a new decision partially changes an accepted ADR, add a dated addendum at the end of the amended ADR rather than rewriting its body silently, and link the amending ADR if one exists.
- When a decision evolves without deserving its own ADR, the dated addendum alone is enough.
- An addendum is still a decision: draft it with the plan, queue it for the author's approval, and leave the status line alone.

## Minimal template (fallback when the repo has none)

```markdown
# ADR-XXXX: [Title]

**Status:** Proposed
**Date:** YYYY-MM-DD
**Amends:** [optional, the accepted ADR this partially modifies]
**Builds on:** [optional, the ADR this extends without changing]

## Context

What situation or requirement prompted this decision.

## Decision

What was decided.

## Rationale

Why this was chosen, and each alternative that was rejected with the reason.

## Consequences

What becomes easier or harder as a result.

## Revisit if

The signals that should reopen this decision.
```
