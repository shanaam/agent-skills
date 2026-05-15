# Test templates

When using Path 1 (template-and-point) in Phase 1, use these as starting points. Adjust to match the project's existing conventions — if the project uses unittest classes, do that; if it uses plain pytest functions, do that. Consistency with the surrounding code matters more than picking the "best" style.

## Python (pytest) — primary

```python
"""
Tests for <module>.<feature>.

Run: pytest <path>/test_<feature>.py -v

All tests are expected to FAIL initially (Red phase).
After confirming with user, implement to satisfy them.
"""
import pytest

# from <module> import <thing>  # uncomment once the impl module exists


# ---- Happy path ----

def test_<descriptive_behavior_name>():
    """<what behavior this verifies, in one line>"""
    # Arrange
    # ...
    # Act
    # result = <thing>(...)
    # Assert
    # assert result == ...
    pytest.fail("Not implemented — replace with real test")


# ---- Edge case ----

def test_<edge_case_descriptive_name>():
    """<boundary, empty, max, off-by-one — what edge case this covers>"""
    pytest.fail("Not implemented — replace with real test")


# ---- Error case ----

def test_<invalid_input>_raises_<error_type>():
    """<what should fail and how>"""
    # with pytest.raises(<ErrorType>):
    #     <thing>(<bad input>)
    pytest.fail("Not implemented — replace with real test")


# ---- TODO: user fills these in ----

def test_TODO_replace_with_real_edge_case():
    """Placeholder — what other behavior matters here?"""
    pytest.fail("Replace with real test or delete")
```

Notes:
- `pytest.fail("Not implemented")` makes placeholders fail loudly. Better than `pass` (silently passes) or no body (also passes).
- Include 1–2 explicit `TODO` stubs at the bottom. They're an invitation for the user to add cases the template missed.
- If the project uses fixtures (`conftest.py`), reference them by name in arrange blocks instead of inline construction.
- If the project uses parametrize for input variation, use it: `@pytest.mark.parametrize("input,expected", [(1, 2), (2, 4)])`.

## Python (unittest) — when project already uses it

```python
"""Tests for <module>.<feature>. All expected to FAIL initially."""
import unittest

# from <module> import <thing>


class Test<Feature>(unittest.TestCase):

    def test_happy_path_<descriptive_name>(self):
        """<one-line behavior description>"""
        self.fail("Not implemented — replace")

    def test_edge_case_<descriptive_name>(self):
        """<edge case description>"""
        self.fail("Not implemented — replace")

    def test_invalid_input_raises_<error_type>(self):
        """<what should fail and how>"""
        # with self.assertRaises(<ErrorType>):
        #     <thing>(...)
        self.fail("Not implemented — replace")

    def test_TODO_replace_with_real_case(self):
        """Placeholder."""
        self.fail("Replace with real test or delete")


if __name__ == "__main__":
    unittest.main()
```

## JavaScript / TypeScript (jest)

```javascript
// import { feature } from '<module>';

describe('<feature>', () => {
  // ---- Happy path ----
  test('<descriptive behavior name>', () => {
    // Arrange
    // Act
    // Assert
    throw new Error('Not implemented — replace with real test');
  });

  // ---- Edge case ----
  test('<edge case description>', () => {
    throw new Error('Not implemented — replace');
  });

  // ---- Error case ----
  test('throws on invalid input', () => {
    // expect(() => feature(badInput)).toThrow(<ErrorType>);
    throw new Error('Not implemented — replace');
  });

  // ---- TODO: user fills these in ----
  test.todo('replace with real edge case');
});
```

Notes:
- `test.todo()` shows up clearly in the runner output as a pending item.
- For async code use `async () => { ... }` and `await expect(promise).rejects.toThrow(...)`.

## Go (testing)

```go
package <package>_test

import (
    "testing"
    // "<module>"
)

func TestHappyPath_<DescriptiveName>(t *testing.T) {
    t.Skip("Not implemented — replace")
    // got := Feature(...)
    // want := ...
    // if got != want {
    //     t.Errorf("got %v, want %v", got, want)
    // }
}

func TestEdgeCase_<DescriptiveName>(t *testing.T) {
    t.Skip("Not implemented — replace")
}

func TestInvalidInput_ReturnsError(t *testing.T) {
    t.Skip("Not implemented — replace")
}
```

Notes:
- `t.Skip` makes the placeholder visible in test output without being a failure. Use `t.Fail()` if you want it to be a failure during Red phase — Go convention varies.
- Table-driven tests are idiomatic in Go: `tests := []struct{ name string; in, want X }{...}` then loop with `t.Run(tt.name, ...)`.

## Rust (built-in test)

```rust
#[cfg(test)]
mod tests {
    // use crate::<module>::*;

    #[test]
    fn happy_path_<descriptive_name>() {
        unimplemented!("Replace with real test")
    }

    #[test]
    fn edge_case_<descriptive_name>() {
        unimplemented!("Replace with real test")
    }

    #[test]
    #[should_panic(expected = "<expected message>")]
    fn invalid_input_panics() {
        unimplemented!("Replace with real test")
    }
}
```

For `Result`-returning code, prefer `assert!(matches!(result, Err(MyError::...)))` over `should_panic`.

## Adapting to project conventions

Before writing any of these, check:

1. **File location.** Where do existing tests live? `tests/`, `src/__tests__/`, alongside source as `_test.go`, in `mod tests {}` blocks?
2. **Naming.** `test_foo.py` vs `foo_test.py` vs `foo.test.ts`? Match it.
3. **Fixtures and helpers.** Does the project have `conftest.py`, factory functions, `make_user()`-style builders, test utilities? Use them rather than reconstructing setup inline.
4. **Assertion style.** Plain `assert` (pytest), `expect(...).toBe(...)` (jest matcher), `self.assertEqual` (unittest), `t.Errorf` (Go)? Match existing tests.
5. **Mocking style.** `unittest.mock.patch`, `pytest-mock`, jest auto-mocks, `gomock`? Match.
6. **Async style.** `async def` + `pytest-asyncio`, `await` + jest, `tokio::test`? Match.

When in doubt, open one or two existing test files and copy their shape. The goal is for your new test file to look like it was written by the same person who wrote the others.
