---
name: test-driven-development
description: Use this skill when the user explicitly asks for TDD ("let's TDD this", "tests first", "write the tests before the code", "test-driven"). Also use proactively when the user asks to build a non-trivial feature in a repo that already has a test framework configured (pytest, jest, go test, cargo test, etc.) — but if unsure whether the feature is complex enough to benefit from TDD, ask the user before engaging. This skill enforces a human-in-the-loop TDD workflow where the user stays in control of (1) what the tests should be, (2) which design pattern to use, and (3) what to optimize. Do NOT trigger for trivial bug fixes, single-function changes from a clear spec, prototypes the user has flagged as throwaway, or repos with no test framework configured.
---

# Test-Driven Development (Human-in-the-Loop)

The standard LLM-TDD failure mode is autonomy: the model writes tests, writes code, runs tests, "fixes" failures by quietly editing the tests, and 30 minutes later the user has a passing suite that proves nothing. This skill exists to prevent that by inserting deliberate human checkpoints at the three places where ownership matters most:

1. **What the tests should be** — the user owns the spec
2. **Which design pattern to use** — the user owns the architecture, so they retain a mental model of their own codebase
3. **What to optimize** — the user owns the tradeoffs against their org's soft norms

Your job is to hold the discipline (force the test-first sequencing, refuse "just a quick implementation first") and do the mechanical work between checkpoints. Not to drive.

## When to engage

Engage when:
- The user explicitly invokes TDD by name or asks for "tests first" / "test-driven" workflow.
- The user asks to build a non-trivial feature AND the repo has a test framework configured. In this case, before engaging, confirm: *"This looks like a non-trivial feature — want to use TDD on it?"* When uncertain whether a feature is complex enough, default to asking rather than assuming.

Don't engage when:
- The user has flagged the work as a prototype, spike, or throwaway.
- The repo has no test infrastructure. Offer to set one up if interested, but don't conflate that with the TDD work itself.
- It's a trivial change (bug fix from a clear stack trace, rename, single-line edit) where TDD adds friction without adding clarity.

## Phase 0: Orient before proposing anything

Build context first. This costs ~5 tool calls and is worth it because every later phase references what you find here.

1. **Read conventions files.** `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `README.md` in repo root. Look in `docs/` for testing or style guides.
2. **Identify the test framework.** Check `pyproject.toml` (`[tool.pytest]`), `pytest.ini`, `package.json` (`"test"` script, `"jest"` config), `go.mod`, `Cargo.toml`. Locate where existing tests live.
3. **Skim 2–3 source files near where the feature will land.** Note: naming style (snake_case vs camelCase, prefix patterns), error handling style (exceptions vs result types), dependency style (DI, globals, module-level), and test style (pytest fixtures, unittest classes, plain asserts, mocking patterns).
4. **Pick the language.** Default to Python on greenfield. Match surrounding code if there's clear context (a JS webapp gets JS). If the repo mixes languages and the right choice isn't obvious, ask the user.

After orienting, summarize briefly — *"Flask app with pytest, fixtures in `conftest.py`, your conventions doc says `dataclasses` not Pydantic, existing handlers raise `AppError` rather than returning result types. I'll follow those."* — and confirm before moving on.

## Phase 1: Define the tests

Always ask the user how they want to define the tests. Frame template-and-point as the default since it's lower-friction:

> *"Two ways to handle the tests: (1) I generate a template test file with placeholder cases reflecting the feature spec, then point you to it so you can edit the assertions to match what you actually want — usually faster. Or (2) we work through them together case-by-case before writing any. Default is (1) unless you'd rather collaborate from scratch."*

### Before drafting: write the bug list first

Whichever path the user chooses, draft a bug list before drafting any tests. Enumerate 5–15 specific bugs you'd want to catch — concrete failure modes you can describe in one sentence:

- ✅ "User submits checkout with expired card → goes through anyway"
- ✅ "Empty cart total returns NaN instead of 0"
- ✅ "Override path takes 8 seconds instead of 5"
- ❌ "Validates input correctly"
- ❌ "Handles errors"
- ❌ "Covers edge cases"

If you can't write the bug list, the feature is under-specified. Ask the user what concrete failure modes they're worried about before going further.

### Audit gate: every test maps to a bug

Before showing any test to the user — template stubs in Path 1, or a proposed test in Path 2 — walk each entry and write the bug it catches in one sentence. Cite the concrete failure mode: "the BOS-strip silently undone", "the override path goes 8s instead of 5s", "expired card check skipped on retry".

If the answer is vague ("verifies the field exists", "checks the function works", "covers the schema"), the test is noise. Cut it.

**Never show the user the first draft.** Show the trimmed list — the one where every remaining test maps to a concrete bug. This is the forcing function. Without it, the natural drift is toward long lists of tests that look thorough but mostly mirror values defined elsewhere or pin implementation details.

See `references/good-tests-vs-bad-tests.md` for the specific anti-patterns the audit is designed to cut (value mirrors, framework tests, trivial guards, type tautologies, mock-call paranoia) and the patterns that produce genuinely useful tests.

### Path 1: Template-and-point (default)

Draft test stubs that target items from the bug list. Each stub:

- Maps to one or more concrete bugs from the list.
- Has a descriptive name (`test_user_can_checkout_with_valid_cart`, not `test_1`).
- Has a docstring stating which bug it catches.
- Has plausible best-guess assertions — the user will edit them, but real scaffolding helps.

Aim for 3–5 stubs covering happy path, edges, and errors. Include 1–2 explicit `# TODO: real edge case from your domain` stubs as invitations for cases the bug list missed.

**Run the audit gate on the draft before saving the file.** Cut any stub you can't justify in one sentence. Save the trimmed file at the right location, in the right framework idiom (see `references/test-templates.md`).

**Then stop. Tell the user the file path and what to review. Do not proceed to implementation until they confirm.**

### Path 2: Collaborative

Ask: *"What's the first observable behavior you want to verify?"* — observable meaning checkable through the public interface, not internal state.

For each test you're about to propose, **first run the audit gate**: write the one-sentence bug it catches. If you can't, don't propose it — the user shouldn't see the first draft.

Propose the audited test, fully written, and ask for sign-off before adding it to the file. Continue case-by-case until the user says they have enough for a vertical slice (typically 3–5 tests for one coherent behavior).

### Test quality (reference)

The audit gate above is the primary discipline. For the specific anti-patterns the audit is designed to cut and the patterns that produce useful tests, see `references/good-tests-vs-bad-tests.md`.

### Confirm tests fail (Red)

Run the tests. They should ALL fail — the implementation doesn't exist yet. If any pass, surface this before continuing. Possible causes: tautology, partial implementation already exists, or the test framework isn't picking up the file (typo, missing decorator). A passing test pre-implementation is not a TDD success.

## Phase 2: Surface design options

Default cycle granularity: **one vertical slice** — one coherent observable behavior with its 3–5 tests. The user can request strict one-test-at-a-time or larger batches.

Before writing any implementation, present 2–3 concrete design options. Be specific — not "use a service layer", but actual patterns with their tradeoffs. See `references/design-pattern-menu.md` for the menu organized by problem shape (extension, dispatch, state, async, etc.).

Example shape:

> *"Three ways I'd consider for this:*
> *1. **Strategy + registry dict.** New payment methods register themselves; selection is a dict lookup. Cleanest extension story, slight indirection cost.*
> *2. **Polymorphic `PaymentProcessor` subclasses + factory.** Familiar OOP shape, IDE-friendly, slightly more ceremony per new method.*
> *3. **Plain `if/elif` dispatch.** Simplest, dies on the third method.*
> *Your codebase already uses (2) for the `Notifier` hierarchy and you mentioned only 1–2 methods this quarter — I'd lean (2) for consistency. Which way?"*

Always recommend one with reasoning, but make alternatives real. Reference the user's existing code where applicable. If the user says "just pick" — pick the one matching the surrounding code's style and tell them why.

## Phase 3: Implement

Write the minimum code to make the current slice's tests pass. Nothing speculative — no "while I'm in here" additions, no extra methods the tests don't exercise. Run the tests after implementing.

### When tests fail (the most important guardrail)

Stop. Do not iterate silently. Report and ask:

> *"Test `test_expired_card_blocks_checkout` failed: `AssertionError: expected CheckoutBlocked, got CheckoutSuccess`. Three options:*
> *1. **Fix the implementation** — the logic doesn't actually check expiration. I can patch this.*
> *2. **Fix the test** — if the assertion is wrong (e.g., we decided expiration shouldn't block).*
> *3. **Talk through it** — if you're not sure which side is right.*
> *What would you like?"*

This matters because the natural drift for an LLM is "just fix the test" when the implementation is hard. Surfacing the choice every time keeps the human in the loop on whether the spec or the code is wrong. Never quietly modify tests to make them pass — even small adjustments ("loosen this assertion", "skip this case for now") go through the user.

### Optimization concerns spotted during implementation

If you see something worth flagging — `O(n²)` where `O(n log n)` is easy, an obvious race condition, a redundant DB call — surface it but **do not fix it without asking**:

> *"Heads up: this loop is O(n²) over `orders`. With <100 orders it's fine; if this scales, a dict lookup makes it O(n). Want me to fix now, defer to the refactor pass, or leave it?"*

Tell the user, let them choose. Silent optimization is the same anti-pattern as silent test rewriting in a different costume.

## Phase 4: Refactor (optional, with consent)

Once the slice's tests pass, ask:

> *"Tests are green. Want to refactor before the next slice? Things I'd consider: [specific list]. Or move on to the next behavior?"*

If refactoring: change one thing at a time, keep tests green between changes, tell the user what changed. If they want to move on, move on.

## Failure modes to watch for in yourself

- **Sneaking past Phase 1.** Writing implementation before tests are confirmed. If you find yourself doing this, stop and back up.
- **Showing the first draft of tests.** The user sees the audited list, never the first draft. If you're about to surface a test you can't justify with a one-sentence bug-mapping, cut it first. Padding a test list with framework checks and type tautologies to look thorough is the failure mode this whole audit gate exists to prevent.
- **Skipping the bug list.** Drafting tests directly from your read of the feature, without first enumerating concrete failure modes, is how the audit gate gets bypassed in practice. The bug list is the spec the tests are graded against — without it, "what bug does this catch?" has no grounding.
- **Picking a pattern silently.** Implementing in some style without surfacing options. The user explicitly wants to retain mental model of their codebase — always offer the menu.
- **Optimizing without asking.** Even small "improvements" (renaming a variable for clarity, extracting a helper) belong in Phase 4 with consent, not Phase 3 unilaterally.
- **Rewriting tests to make them pass.** Never. The protocol is: report failure, present three options, wait.
- **Front-loading the whole feature.** Vertical slice means one observable behavior at a time. If you find yourself writing five behaviors of tests before any implementation, you've drifted into batch mode — back up.

## Reference files

- `references/good-tests-vs-bad-tests.md` — patterns and anti-patterns for test quality. Read when writing or reviewing tests.
- `references/design-pattern-menu.md` — concrete pattern options grouped by problem shape. Read at the start of Phase 2.
- `references/test-templates.md` — pytest-first templates with notes on jest, go test, cargo test. Read when generating a template in Phase 1, Path 1.
