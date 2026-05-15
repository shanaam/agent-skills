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

### Path 1: Template-and-point (default)

Generate a test file at the right location, in the right framework idiom (see `references/test-templates.md`). Include:

- 3–5 test stubs covering happy path, an edge case, and an error case.
- 1–2 stubs explicitly labeled `# TODO: replace with your real edge case here`.
- Descriptive names (`test_user_can_checkout_with_valid_cart`, not `test_1`).
- A comment block on each stub describing what it should assert.
- Best-guess assertions where reasonable — the user is going to edit them, but plausible scaffolding helps.

**Then stop. Tell the user the file path and what to review. Do not proceed to implementation until they confirm.**

### Path 2: Collaborative

Ask: *"What's the first observable behavior you want to verify?"* — observable meaning checkable through the public interface, not internal state.

Propose one test for that behavior, fully written, and ask for sign-off before adding it to the file. Continue case-by-case until the user says they have enough for a vertical slice (typically 3–5 tests for one coherent behavior).

### Test quality

Whichever path: tests describe **WHAT** the system does, not **HOW**. Before writing tests, glance at `references/good-tests-vs-bad-tests.md`. Headline rules:

- Test through public interfaces.
- Names read like a spec.
- One observable behavior per test.
- Don't assert on private methods, internal data structures, or call counts (unless the call itself IS the contract — e.g., emails sent).
- Don't write tautology tests (`assert 1 + 1 == 2`).

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
- **Picking a pattern silently.** Implementing in some style without surfacing options. The user explicitly wants to retain mental model of their codebase — always offer the menu.
- **Optimizing without asking.** Even small "improvements" (renaming a variable for clarity, extracting a helper) belong in Phase 4 with consent, not Phase 3 unilaterally.
- **Rewriting tests to make them pass.** Never. The protocol is: report failure, present three options, wait.
- **Front-loading the whole feature.** Vertical slice means one observable behavior at a time. If you find yourself writing five behaviors of tests before any implementation, you've drifted into batch mode — back up.

## Reference files

- `references/good-tests-vs-bad-tests.md` — patterns and anti-patterns for test quality. Read when writing or reviewing tests.
- `references/design-pattern-menu.md` — concrete pattern options grouped by problem shape. Read at the start of Phase 2.
- `references/test-templates.md` — pytest-first templates with notes on jest, go test, cargo test. Read when generating a template in Phase 1, Path 1.
