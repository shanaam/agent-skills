# Good tests vs. bad tests

A test's job is to lock in observable behavior so future refactors are safe. A test that breaks every time the internals change isn't doing that job — it's just noise that has to be maintained forever.

## The core question

Before writing any test, ask: *"If I completely rewrote the implementation tomorrow but kept the public interface, should this test still pass?"*

- Yes → good test.
- No → it's coupled to implementation. It's a liability.

## Good test patterns

### 1. Test through public interfaces

```python
# GOOD
def test_user_can_checkout_with_valid_cart():
    user = make_user()
    cart = make_cart_with([item("widget", 10.00)])

    receipt = checkout(user, cart)

    assert receipt.total == 10.00
    assert receipt.status == "completed"
```

The test calls `checkout()` (a public function) and checks the resulting `receipt`. Says nothing about HOW checkout works internally. This test survives any internal refactor.

### 2. Names that read like a spec

A reader scanning your test names should learn what the system does:

- `test_expired_card_blocks_checkout` ✅
- `test_empty_cart_returns_zero_total` ✅
- `test_checkout_2` ❌ (says nothing)
- `test_validate_internal_state` ❌ (about internals, not behavior)

### 3. One observable behavior per test

Each test asserts one outcome. If you find yourself writing `# Step 1: ... # Step 2: ...` with separate assertions on different things, that's probably 2–3 tests.

### 4. Arrange-Act-Assert (or Given-When-Then)

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

Visual structure makes the test readable and the failure message clearer.

### 5. Concrete expected values, not derived ones

```python
# GOOD
def test_calculate_total_includes_8_percent_tax():
    items = [item(price=100.00)]
    assert calculate_total(items) == 108.00  # the spec, hardcoded
```

The expected value is the spec. If the implementation has a bug, the test catches it.

## Bad test patterns

### 1. Testing private methods or internal state

```python
# BAD
def test_checkout_calls_internal_validation():
    order = Order(...)
    order.checkout()
    assert order._validation_was_called == True
```

Refactor the internals — remove `_validation_was_called` — and the test breaks even though behavior is identical.

### 2. Asserting on call counts (unless the call IS the contract)

```python
# BAD — the test breaks if you cache, batch, or memoize
def test_db_called_three_times(mock_db):
    process_orders([o1, o2, o3])
    assert mock_db.call_count == 3
```

```python
# GOOD — when "did we send the email" IS the spec
def test_confirmation_email_sent_on_checkout(mock_mailer):
    checkout(user, cart)
    assert mock_mailer.sent_count == 1
    assert mock_mailer.last_recipient == user.email
```

The distinction: are you asserting on a side effect that's part of the contract (email sent, audit log written), or on internal call patterns that are implementation details?

### 3. Tautology tests

```python
# BAD
def test_addition():
    assert 1 + 1 == 2  # testing Python, not your code
```

If a test passes regardless of what you do to your code, it isn't testing your code.

### 4. Tests that mirror the implementation

```python
# Implementation
def calculate_total(items):
    subtotal = sum(item.price for item in items)
    tax = subtotal * 0.08
    return subtotal + tax

# BAD — same logic, different syntax
def test_calculate_total():
    items = [...]
    expected = sum(i.price for i in items) + sum(i.price for i in items) * 0.08
    assert calculate_total(items) == expected
```

If the implementation has a bug, the test has the same bug. Use concrete expected values (see Good Pattern 5).

### 5. Over-mocking

Mock external boundaries (network, time, randomness, third-party APIs, the filesystem when relevant). Don't mock your own code unless there's no alternative — over-mocking makes tests fragile and stops them from catching integration bugs.

If you find yourself writing five `mock.patch` decorators on a single test, that's a signal: the function under test is doing too much, or the mocks have replaced so much of the system that you're really just testing the mocks.

## When a test passes on the first run

If a test passes immediately when you run it before writing any implementation, suspect it. Possible causes:

- **Tautology.** The assertion is trivially true (testing the language or framework).
- **Already implemented.** The behavior exists somewhere else in the code.
- **Test framework didn't run it.** Typo in the test name, wrong file location, missing decorator.

Surface this to the user. A passing test pre-implementation is not a TDD success — it's a signal something is off.

## Quick checklist before sign-off

Before confirming a test set is ready (Phase 1 → Phase 2 transition):

- [ ] Each test has a name that reads like a spec.
- [ ] Each test asserts on observable behavior, not internal state.
- [ ] No call-count assertions unless the calls are the contract.
- [ ] Expected values are concrete, not derived.
- [ ] Mocks cover external boundaries only (or: they cover internal collaborators and the user agreed that was needed here).
- [ ] All tests fail when run (Red). If any pass, investigate before moving on.
