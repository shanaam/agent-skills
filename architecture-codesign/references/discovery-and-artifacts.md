# Discovery question bank and artifact catalogue

Read this when opening discovery (to pick and adapt the first batch) and again when listing artifacts at the end.
Nothing here is a script to recite; pick the themes the request makes live and drop the rest.

## Discovery themes

Aim for 6 to 12 questions in the first batch, grouped under theme headers, numbered so the user can answer holistically and skip what does not apply.
Close every batch with "Anything important I haven't asked about?".

### Goals and users

- What is this for, and who uses it (an internal team, end users, both, other agents)?
- What does success look like in six months, and in two years?
- What is the one thing it must do well even if everything else is mediocre?

### Constraints

- Languages, frameworks, or platforms fixed by the team, and which are open?
- Existing infrastructure (cloud, on-prem, hybrid, a particular account or region)?
- Compliance, privacy, or security requirements, including internal policy?
- Budget envelope, and whether that is money, people, or calendar?
- Team size, and experience with the candidate technologies?

### Workload shape

- Throughput, latency, data volume, and how peaky the load is?
- For ML: training, serving, or both; online or batch; model size; inference pattern (sync, async, streaming)?
- For data systems: arrival pattern, retention, who reads it back and how often?

### Existing system context

- What is in place today, and what is painful about it?
- What is replaceable, and what must the new work integrate with unchanged?
- Which decisions are already recorded (ADRs, design docs, rules files) and still binding?

### Tradeoff tolerance

- Which of speed to prototype, correctness, cost, operability, and flexibility wins when they conflict?
- Rank them; the order matters more than the individual answers.
- What is the user explicitly willing to give up?

### Time horizon

- Throwaway prototype, an internal tool for one team, or a foundation meant to last years?
- Is this a finish-line deliverable or compounding platform work; the second needs as much investment in futures (tidying, tests, docs) as in features.
- This single answer dominates most structural choices, so pin it down early.

### Execution context

- Who executes the plan: the user, agent sessions, or both, and are several sessions likely to run at once?
- Which steps need the author's hands (credentials, hardware, a second machine, production writes)?
- What counts as done: tests green, a manual check, a demo, a sign-off?

## Extra probes by system type

### ML systems

- Which lifecycle stages matter: train, evaluate, serve, retrain, monitor?
- Data and feature versioning and lineage requirements?
- Failure modes that matter (drift, latency, hallucination, bias) and how each is detected?
- Compute mix (GPU/CPU) and the training-time horizon (minutes, hours, days)?
- Where do evaluation sets come from, and who owns their quality?

### Device-facing and real-time systems

- Which clocks exist (device, host, wall) and which one is authoritative for each stream?
- What happens on link loss, reorder, or backpressure, and how is loss made visible rather than concealed?
- Which parts live in firmware, which on the host, and what is the cost of moving the boundary later?
- How is the device stood in for during development (emulator, replay, synthetic), and what does the stand-in not reproduce?

### Platform and repository work

- One repository or several, and which cross-dependencies are allowed?
- Which checks gate a merge today (hooks, CI lanes, labels), and which are advisory?
- What is the task runner, and does every recurring workflow already have a recipe?

## Artifact catalogue

List artifacts at the end of every session, each with a filename, a one-line purpose, and three to five bullets of expected contents.
Offer to draft; do not auto-generate, because many are short-lived or unwanted and the user should pick.
Surface the implementation plan separately from the documentation set, because it is the artifact most likely to be accepted on first offer.

Examples by domain, to adapt to what discovery surfaced:

- **Repository, CI, and testing:** the implementation plan, `docs/repo-structure.md`, `docs/testing-philosophy.md` (test types, what is skipped and why), `docs/ci-pipeline.md`, `CONTRIBUTING.md`, an ADR template, a PR template, branch-protection notes.
- **Service architecture:** a service catalogue, one ADR per major decision, runbooks, on-call playbook stubs, an SLO and SLI document.
- **ML platforms:** a model lifecycle policy, a data and feature versioning policy, monitoring SLOs, train/eval/serve interface contracts, a retraining cadence document, model registry conventions.
- **Device-facing systems:** a wire-protocol document, a clock-domain and alignment note, a stand-in (emulator or replay) guide with its known gaps, a manual QC walkthrough.
- **Cross-cutting:** a decision log with the ADR template, a platform overview README, a glossary of internal terms, and the rules file for agents (AGENTS.md with a CLAUDE.md pointer) when the repo lacks one.
