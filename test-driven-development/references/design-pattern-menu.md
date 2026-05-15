# Design pattern menu

Use this as a checklist when entering Phase 2. Pick the 2–3 most relevant patterns for the user's problem shape and present them with concrete tradeoffs. Always recommend one with reasoning grounded in the user's codebase, but make the alternatives real (not strawmen).

The point is not to pick the "fanciest" pattern. It's to give the user a real choice between options that fit their problem and their existing code, and to keep them in the driver's seat on architectural decisions.

## How to present options

Three rules of thumb:

1. **Reference the codebase.** *"Your `Notifier` already does X — using the same shape here means new contributors only learn one pattern."*
2. **Be specific about cost.** Not "more complex" but *"adds an extra file per variant and one indirection per call."*
3. **Recommend, but invite override.** *"I'd lean (2). Want to go that way, or did you want to push back?"*

If options are genuinely close — say so. *"Honestly these are within noise of each other for your case. (1) is what your existing code uses. Pick that unless you've got a reason."*

---

## By problem shape

### Adding new variants over time (open-closed)

| Pattern | When it fits | Cost |
|---|---|---|
| **Plain `if/elif` dispatch** | 1–2 variants, no plans to grow | Dies on the 3rd variant; rewriting later is a hassle |
| **Strategy + registry dict** | Variants register themselves; great when extensions live in plugins or modules loaded at startup | Extra indirection; harder for IDE jump-to-definition |
| **Polymorphic subclasses + factory** | Strong type discipline, IDE-friendly navigation, familiar OOP | More files, more ceremony per variant |
| **Tagged union / discriminated dataclass** | Variants are mostly data with one switch on type | Behavior gets fragmented if logic grows beyond the switch |

### Dispatch (which thing handles which input)

| Pattern | When it fits |
|---|---|
| **Simple dict / mapping** | Static set of handlers, clean key→callable, no order dependency |
| **Chain of responsibility** | Order matters, handlers may pass on to the next, default fallback |
| **Visitor** | One operation across many node types (AST walking, document traversal) |
| **Match / switch (Python 3.10+, Rust, Go)** | Shape is structural and you want exhaustiveness checking |

### State management

| Pattern | When it fits |
|---|---|
| **Pure functions + explicit state passing** | Easiest to test, easiest to reason about, no hidden mutation |
| **Class with state** | Long-lived object with coherent lifecycle (connection, session, document) |
| **Module-level state** | Singletons (config, logger). Beware: hard to test, easy to leak between tests |
| **Context object passed through calls** | Many functions need same handful of values; alternative to threading them as args |

### Async / concurrency

| Pattern | When it fits |
|---|---|
| **Sync, top to bottom** | Default. Don't reach for async unless you actually need it |
| **`async`/`await`** | I/O-bound, many concurrent operations (HTTP fan-out, DB pools) |
| **Background worker / queue** | Decouple slow work from request path; durability matters |
| **Multiprocessing** | CPU-bound (Python especially — the GIL makes threading useless for compute) |
| **Threading** | CPU-bound in non-GIL languages, or I/O-bound where async is overkill |

### Configuration & dependency injection

| Pattern | When it fits |
|---|---|
| **Constructor injection** | Dependencies explicit, tests substitute easily, type-checkable |
| **Default arg with override** | Single dependency, simple cases (`def fn(client=DEFAULT_CLIENT)`) |
| **Module-level singleton** | Truly global resource (logger, app config). Keep these few |
| **DI container / framework** | Large codebase with deep dependency trees. Usually overkill — try without first |

### Error handling

| Pattern | When it fits |
|---|---|
| **Exceptions** | Default in Python; for genuinely exceptional cases (not control flow) |
| **Result types (`Ok`/`Err`, `Either`)** | Domain errors callers should always handle. Common in Rust, Go, modern TS |
| **Sentinel returns (`None`, `-1`, `""`)** | Almost never. Easy for callers to forget to check |
| **Custom error hierarchy** | When callers need to distinguish error types and catch selectively |

### Data shape and validation

| Pattern | When it fits |
|---|---|
| **Plain `dict` / record** | Internal, throwaway, when shape is unstable |
| **`dataclass` / `NamedTuple` / `struct`** | Internal, stable shape, no validation needed |
| **Pydantic / attrs / pydantic-like with validators** | External boundary (API, file parsing); validation is the point |
| **Protocol / interface** | Define structural type without prescribing implementation |

### Persistence access

| Pattern | When it fits |
|---|---|
| **Direct ORM/SQL in handler** | Small app, single team, no plans for multiple data sources |
| **Repository pattern** | Want to swap storage (test in-memory, prod Postgres), or multiple call sites need the same query |
| **CQRS (read/write split)** | Reads and writes have very different shapes or scaling needs |
| **Active Record** | ORM convention (Django, Rails); the model object knows how to save itself |

---

## Example: how a Phase 2 prompt looks

> *"For the payment processor, three real options:*
>
> *1. **`if/elif` dispatch.** One function, branches on `method_type`. Cost: when you add Stripe webhooks next quarter you're back here editing this function.*
>
> *2. **Strategy + registry dict.** Each method is a class implementing `PaymentMethod`; `METHODS = {"card": CardMethod(), "bank": BankMethod()}`. Adding a method is one new file plus a registry entry. Cost: one extra indirection at the call site.*
>
> *3. **Subclass + factory.** `class CardMethod(PaymentProcessor)`, factory function maps strings to classes. Familiar OOP. Cost: marginally more ceremony than (2).*
>
> *Your `Notifier` hierarchy uses pattern (3), so going that way keeps consistency. But (2) is cleaner if you'll have plugins. Which way?"*

That's the shape: concrete, grounded in their code, recommendation with reasoning, real alternatives, decision back to the user.
