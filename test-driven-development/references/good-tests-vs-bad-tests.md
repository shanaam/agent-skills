# Good tests vs. bad tests

A test's job is to lock in observable behavior so future refactors are safe, and to catch concrete bugs before they ship. A test that does neither is noise — it has to be maintained, it churns on legitimate changes, and it gives false confidence.

This file is the reference for the audit gate in SKILL.md Phase 1. The audit asks: *"For this test, what bug would it catch?"* The patterns below describe what answers count as real bugs and which "tests" are actually noise dressed up as coverage.

## The audit question

Before any test goes in front of the user, answer in one sentence: **what concrete failure mode does this catch?**

- ✅ "The BOS strip silently undone by tokenizer change"
- ✅ "Override path takes 8s instead of 5s"
- ✅ "Expired card check skipped on retry path"
- ❌ "Verifies the field exists"
- ❌ "Checks the function works"
- ❌ "Covers the schema"

If the answer is vague, the test is noise. Cut it.

A related sanity check: *"If I rewrote the implementation tomorrow but kept the public contract, should this test still pass?"* If no, the test is coupled to implementation and is a liability.

## Anti-patterns to cut

### 1. Value mirrors

When a value is defined elsewhere (YAML config, schema default, module-level constant), don't assert it equals itself. The other file IS the source of truth; the test just churns on every legitimate tuning change.

```python
# BAD — mirrors dry_run.yaml
def test_max_steps_is_75():
    cfg = load_config("dry_run.yaml")
    assert cfg.train.max_steps == 75
```

The day someone retunes `max_steps` to 50 — a legitimate, intended change — this test breaks despite nothing being wrong. The test catches no bug; it only catches "the YAML was modified."

Distinguish from **policy pins** (below), which look similar but encode a deliberate decision worth pinning.

### 2. Framework tests

Pydantic's `Literal`/`PositiveFloat`, Hydra's overrides, OmegaConf's serialization, ORM column types, library validators — these have their own test suites. Don't reimplement them.

```python
# BAD — testing Pydantic
def test_age_must_be_positive():
    with pytest.raises(ValidationError):
        User(age=-1)  # age: PositiveInt
```

If `age: PositiveInt` is in the schema, Pydantic guarantees rejection. The test pins your trust in Pydantic — not anything about your code.

Trust the framework. Test the behavior you wrote.

### 3. Trivial guards

A method that's `if self._x is not None: self._x.foo()` doesn't need a "no-op when None" test. The guard is obvious from the code; testing it pins implementation rather than behavior.

```python
# BAD
def test_cleanup_is_noop_when_resource_is_none():
    handler = Handler()
    handler._resource = None
    handler.cleanup()  # should not raise
```

If the guard ever gets removed, the bug it would cause (`AttributeError: 'NoneType' has no 'close'`) shows up immediately in any real test that uses the handler. You don't need a dedicated test for it.

### 4. Type tautologies

```python
# BAD
def test_returns_figure():
    result = make_plot(data)
    assert isinstance(result, Figure)  # -> Figure in annotation
```

`mypy` (or any type checker) already enforces this. The test runs the function just to check what the annotation already promises. Either trust the type system or don't — but if you trust it, the test is redundant.

### 5. Mock-call paranoia

```python
# BAD — `process` is the only thing `handle` calls
def test_handle_calls_process():
    with patch.object(service, "process") as mock_p:
        service.handle(payload)
        mock_p.assert_called_once_with(payload)
```

If `process` IS the side effect that matters (it sends an email, charges a card, writes to an audit log), then asserting it was called is legitimate — the call IS the contract. But asserting on call counts/args for internal helpers means you're testing that the function does what it does. Refactoring breaks the test even though behavior is unchanged.

Rule of thumb: assert on mock calls only when the call is the observable behavior. Otherwise, assert on the result.

## Patterns that produce useful tests

### 1. Branch coverage, not line coverage

Focus on decision points: `if`/`else` arms, `try`/`except` fallbacks, early returns, edge values (0, empty, single-element, ratio-at-boundary, off-by-one).

```python
# Each branch gets a test, not each line
def test_discount_at_threshold_exactly():       # boundary
def test_discount_below_threshold():            # else arm
def test_discount_above_threshold():            # if arm
def test_discount_on_empty_cart():              # early return
def test_discount_when_coupon_expired():        # except path
```

Line coverage is satisfied by any test that touches the code. Branch coverage requires understanding the decisions the code makes.

### 2. Comprehensive happy-path beats field-by-field

One test exercising the full contract beats six tests checking one field each.

```python
# GOOD — one test, full contract
def test_checkout_produces_complete_receipt():
    receipt = checkout(user, cart_with_items)
    assert receipt.status == "completed"
    assert receipt.total == 110.00
    assert receipt.tax == 10.00
    assert receipt.items[0].sku == "WIDGET-1"
    assert receipt.timestamp is not None
```

```python
# BAD — six tests, all rebuild the same scenario
def test_receipt_has_status(): ...
def test_receipt_has_total(): ...
def test_receipt_has_tax(): ...
def test_receipt_has_items(): ...
def test_receipt_has_timestamp(): ...
def test_receipt_status_is_completed(): ...
```

The six-test version triples maintenance cost and tests no additional bug.

### 3. Parametrize related cases

Present/absent, yes/no, three-cell truth tables → one parametrized test.

```python
@pytest.mark.parametrize("status,coupon_valid,expected_discount", [
    ("active",  True,  10.00),
    ("active",  False,  0.00),
    ("expired", True,   0.00),
    ("expired", False,  0.00),
])
def test_discount_combinations(status, coupon_valid, expected_discount):
    user = make_user(status=status)
    coupon = make_coupon(valid=coupon_valid)
    assert calculate_discount(user, coupon) == expected_discount
```

Each row is a bug-mapping. The parametrize structure makes the truth table visible at a glance.

### 4. Policy pins vs. value mirrors

A value that encodes a **deliberate decision** — a dev/prod split, a cost-control choice, a security invariant — is worth pinning because flipping it is a policy regression, not a tuning change. This looks like a value mirror but isn't.

```python
# GOOD — policy pin, documented
def test_production_uses_real_storage_not_mock():
    """Policy: prod must never use InMemoryStore (data loss risk).

    Catches: someone setting STORAGE_BACKEND=memory in prod config.
    """
    cfg = load_config(env="production")
    assert cfg.storage.backend != "memory"
```

```python
# BAD — value mirror, same shape but no policy
def test_storage_backend_is_postgres():
    cfg = load_config(env="production")
    assert cfg.storage.backend == "postgres"
```

The difference: the first catches "we accidentally lost durability"; the second breaks the day someone legitimately migrates to a different database. Always document the policy in the test docstring — if you can't articulate one, it's a value mirror, not a policy pin.

## Other useful patterns (still good, less critical)

### Tests named like specs

A reader scanning test names should learn what the system does:

- `test_expired_card_blocks_checkout` ✅
- `test_empty_cart_returns_zero_total` ✅
- `test_checkout_2` ❌
- `test_validate_internal_state` ❌

### Concrete expected values, not derived ones

```python
# GOOD
def test_calculate_total_includes_8_percent_tax():
    items = [item(price=100.00)]
    assert calculate_total(items) == 108.00  # the spec, hardcoded
```

If the expected value is derived from the same logic as the implementation, the test has the same bug as the code.

### Arrange-Act-Assert

```python
def test_discount_applies_to_subtotal():
    # Arrange
    cart = make_cart_with([item("widget", 100.00)])
    coupon = Coupon(percent_off=10)
    # Act
    total = apply_coupon(cart, coupon).total
    # Assert
    assert total == 90.00
```

Visual structure makes failure messages clearer and tests scannable.

### Mock external boundaries only

Mock network, time, randomness, third-party APIs, the filesystem when needed. Don't mock your own code — it makes tests fragile and stops them catching integration bugs. If you find yourself writing five `mock.patch` decorators on one test, the function under test is doing too much, or you're really just testing the mocks.

## Backfilling vs. TDD-first: a different failure mode

When tests are written AFTER the code exists, there's a gravitational pull toward *"verify the code works as written."* Those tests pin implementation, not behavior. The author reads the code, asks "what does this do?", and writes tests confirming it. Future refactors break the tests even when behavior is identical.

**Antidote: write the bug list FIRST.** Before drafting any tests, enumerate 5–15 specific bugs you'd want to catch. If possible, cite recent commits where similar bugs were introduced — they're the most honest evidence of what fails in this codebase.

Then design tests for those bugs. Anything in the draft that doesn't map to a listed bug is suspect — it's probably an artifact of reading the code rather than reading the spec.

This is exactly the audit gate from SKILL.md Phase 1, but it matters even more on backfill because the gravitational pull is stronger. If you're being asked to add tests to existing code: do the bug list first, before opening any source file.

## Quick checklist before sign-off

Before confirming a test set is ready (Phase 1 → Phase 2 transition):

- [ ] You have a bug list. Every test in the set maps to one or more listed bugs.
- [ ] No value mirrors. Every constant-comparison is either a policy pin (with documented policy) or it's been cut.
- [ ] No framework tests. You're not re-testing Pydantic / Hydra / your ORM.
- [ ] No trivial guards. Obvious `if x is not None:` checks aren't being pinned.
- [ ] No type tautologies. `isinstance` checks against the annotated return type are gone.
- [ ] No mock-call paranoia. Call-count assertions only where the call IS the contract.
- [ ] Each test asserts on observable behavior, not internal state.
- [ ] All tests fail when run (Red). If any pass pre-implementation, investigate before moving on.

## When a test passes on the first run (pre-implementation)

Suspect it. Possible causes:

- **Tautology.** The assertion is trivially true.
- **Framework test.** You're testing the library, which already works.
- **Type tautology.** mypy or the language enforces the assertion.
- **Value mirror.** Both sides come from the same source — comparing X to X.
- **Already implemented.** The behavior exists somewhere else in the code.
- **Test framework didn't run it.** Typo, wrong file, missing decorator.

A passing test pre-implementation is not a TDD success. Surface it to the user.
