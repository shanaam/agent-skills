# Research sources

Read this when the research phase starts.
It is a starting list of primary sources on AI-assisted and agentic development practice, with the date each was verified or published, so the research phase begins from reputable ground instead of a search box.
It is not a substitute for the vertical-specific research the design needs; for that, the rule is official documentation plus the engineering blogs of organisations that run the system at scale.
Dates matter: this field moves within a model generation, so prefer the newest primary source and say which date a claim rests on.

Contents:

- How to use this list
- Anthropic guidance for Claude Code and agents
- Evidence and industry reports
- Planning, specifications, and ADRs
- Testing, review, and verification
- Engineering organisations' write-ups
- Practitioner essays
- Finding sources for a vertical
- Old patterns to recognise in search results

## How to use this list

- Fetch the page; do not quote from memory.
  Several of these pages redirect or have been rewritten since first publication, and a quote from the old version misleads.
- Prefer the docs page over the blog post when both exist; the docs are maintained and the post is a snapshot.
- Vendor reports measure their own product; independent studies and the author's own posts carry more weight for a design decision.
- When two reputable sources disagree, both go into the questions file or the proposal with their dates, and the user decides.

## Anthropic guidance for Claude Code and agents

- Best practices for Claude Code (docs, maintained; the April 2025 engineering post redirects here): verification first, interview to a spec then a fresh session, adversarial review against the plan, skip the plan when the diff fits one sentence, CLAUDE.md pruning. https://code.claude.com/docs/en/best-practices
- How Claude remembers your project (docs): CLAUDE.md under 200 lines, path-scoped rules, AGENTS.md support, hooks for anything that must always happen. https://code.claude.com/docs/en/memory
- Keep Claude working toward a goal (docs, May 2026): a bounded end condition checked by a fresh evaluator, for unattended phases. https://code.claude.com/docs/en/goal
- Subagents and dynamic workflows (docs): isolated workers for verbose or parallel work; workflows for audits or a plan drafted from several angles. https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/workflows
- Effective context engineering for AI agents (Sept 2025): smallest high-signal context, just-in-time retrieval, structured note-taking, subagents returning short summaries. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Effective harnesses for long-running agents (Nov 2025): progress file, feature list that executors may only flip, one feature per session, end in a mergeable state. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Harness design for long-running application development (Mar 2026): separate the agent judging from the agent working; remove components one at a time as models improve. https://www.anthropic.com/engineering/harness-design-long-running-apps
- Prompting best practices and model-specific pages (docs): over-engineering, test-gaming, and scope blocks; fresh-context verifiers; skills written for earlier models are often too prescriptive. https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Agent Skills specification and authoring best practices: name and description limits, references one level deep, under 500 lines. https://agentskills.io/specification and https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Agentic coding and persistent returns to expertise (June 2026): humans make most planning decisions, agents most execution decisions; precision of framing predicts success. https://www.anthropic.com/research/claude-code-expertise

## Evidence and industry reports

- DORA State of AI-assisted Software Development (Sept 2025) and the AI Capabilities Model: AI amplifies what is already there; small batches, version control, and user-centric focus moderate the effect; throughput up, stability still down. https://dora.dev/research/2025/dora-report/
- DORA, Balancing AI tensions (Mar 2026): the verification tax; review burden shifts to reviewers; pair seniors on AI-generated architectural decisions. https://dora.dev/insights/balancing-ai-tensions/
- METR, early-2025 developer study (July 2025) and the Feb 2026 update: the perception gap and the context dependence are the durable findings, not the sign. https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ and https://metr.org/blog/2026-02-24-uplift-update/
- METR, many SWE-bench-passing PRs would not be merged (Mar 2026): about half of test-passing agent patches rejected by maintainers. https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/
- He et al., AI writes faster than humans can review (July 2026): review coverage falls with volume, not with authorship; govern by review wait and revert rate, not merge count. https://arxiv.org/html/2607.01904
- Fan et al., harness design for coding agents (Sept 2026): planning scaffolds help weak models and cut cost for strong ones. https://arxiv.org/html/2609.20804
- Oota et al., do agents execute the plans they declare (Sept 2026): most declared plans are not followed unless structure is enforced. https://arxiv.org/abs/2609.38108
- SWE-RPG (Aug 2026): implicit-requirement recovery is the main agent failure mode. https://arxiv.org/abs/2608.09072
- GitClear, the maintainability gap (2026): duplication and error-masking up, reuse and refactoring down; vendor data. https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- Veracode GenAI code security report (2025): a large share of generated snippets insecure in specific weakness classes regardless of model; vendor benchmark. https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/
- Storey, from technical debt to cognitive and intent debt (Mar 2026): the absence of externalised rationale as a debt class. https://arxiv.org/abs/2603.22106
- Shen and Tamkin, how AI impacts skill formation (Jan 2026): delegation patterns learn least. https://arxiv.org/html/2601.20245

## Planning, specifications, and ADRs

- Thoughtworks Technology Radar, Vol 33 (Nov 2025) and Vol 34 (Apr 2026): context engineering and curated shared instructions at Adopt, spec-driven development at Assess with reservations, mutation testing and feedback sensors at Trial, instruction bloat and swarms at Caution. https://www.thoughtworks.com/radar
- Böckeler, understanding spec-driven development (Oct 2025): spec-first versus spec-anchored versus spec-as-source; heavy tooling as a sledgehammer. https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- Böckeler, harness engineering for coding agent users (Apr 2026): guides and sensors, computational and inferential; commit to a topology. https://martinfowler.com/articles/harness-engineering.html
- Morris, humans and agents in software engineering loops (Mar 2026): humans on the loop own the harness; artifacts are a means to an end. https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html
- Beck, Earn and Learn (Feb 2026): finish-line versus compounding game; the spec cannot carry a compounding system. https://newsletter.kentbeck.com/p/earn-and-learn
- Eisele, spec-driven development needs an exit strategy (July 2026): the change brief; after shipping, durable facts move into native artifacts and the rest goes. https://www.the-main-thread.com/p/spec-driven-development-exit-strategy
- Marmelab, the waterfall strikes back (Nov 2025): measured verbosity of spec tooling on small changes. https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back.html
- GitHub Spec Kit docs (2026): the converge step classifying gaps as missing, partial, contradicts, unrequested; match tool weight to task. https://github.github.io/spec-kit/
- Kiro specs docs (2026): requirements in EARS form so each maps to a test; bug specs record unchanged behaviour. https://kiro.dev/docs/specs/
- HumanLayer, advanced context engineering for coding agents (2025): a bad line of a plan becomes hundreds of bad lines of code; review the plan, not the diff. https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md
- Zimmermann, ten common mistakes in ADRs (Sept 2026): criteria before options, justified rejections, negative consequences, AI output checked. https://ozimmer.ch/practices/2026/09/12/ADRMistakes.html
- MADR 4.0 (Sept 2024): the reference template and status vocabulary. https://adr.github.io/madr/
- Davidson, coding agents love decision records (Oct 2026): accepted binding, proposed context, superseded history; conflict means stop and discuss; beware over-enforcement. https://www.oreilly.com/radar/coding-agents-love-decision-records/
- agents.md convention: nearest file wins, sections, boundaries. https://agents.md/
- Nigh, how to write a great agents.md (Nov 2025): commands with flags, one real snippet, three-tier boundaries, grow by iteration. https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/

## Testing, review, and verification

- ImpossibleBench (Oct 2025): how often models cheat on contradictory tests, and which mitigations work (strict prompts, an abort path, read-only tests). https://arxiv.org/html/2510.20270v1
- MutGen (2025, revised 2026): full coverage with near-zero mutation score; coverage is a weak fault-detection signal. https://arxiv.org/abs/2506.02954
- Zhao et al., misguidance effect of buggy code in generated tests (July 2026): tests written from the implementation assert its bugs; spec-first generation reduces it. https://arxiv.org/abs/2607.22883
- Böckeler, maintainability sensors for coding agents (May 2026) and TDD inside the agent loop (Aug 2026): sensors over mandated test-first; faked red steps; mutation testing. https://martinfowler.com/articles/sensors-for-coding-agents.html and https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html
- GitHub, how to review agent pull requests (May 2026): check CI and test changes first; a weakened CI is a blocker; request a plan or a split for large changes. https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/
- Demystifying evals for AI agents (Jan 2026): grade the final state, not the claims; criteria two experts would grade alike. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Verification tooling for driving an application as a user, with screenshots and profiles, is listed in [verification.md](verification.md).

## Engineering organisations' write-ups

- OpenAI, harness engineering (Feb 2026; primary page often blocks fetches, so triangulate): docs as the system of record, mechanical architecture checks, exec plans with progress logs, doc garbage collection. https://openai.com/index/harness-engineering/
- Stripe, Minions (Feb 2026): one-shot agents on isolated devboxes, rules scoped by subdirectory, feedback shifted left. https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents
- Shopify, Under the River (May 2026): agents work in the open; the session is what must survive. https://shopify.engineering/under-the-river
- Ramp, why we built our own background agent (Jan 2026): sandbox per session, PRs under the requesting human's identity. https://builders.ramp.com/post/why-we-built-our-background-agent
- Cursor, towards self-driving codebases (Feb 2026): planners that do not code, workers that return one hand-off, premature-completion failures. https://cursor.com/blog/self-driving-codebases
- Anthropic, building a C compiler with parallel Claudes (Feb 2026): tests of low quality make the agent solve the wrong problem; progress files; cheating observed. https://www.anthropic.com/engineering/building-c-compiler
- Pragmatic Engineer, how building software is changing at Anthropic (July 2026) and inside OpenAI's agentic software factory (Sept 2026): PR gates with a failing test on the unpatched build; risk-tiered review. https://newsletter.pragmaticengineer.com/

## Practitioner essays

- Willison, agentic engineering patterns (2026 guide) and the parallel coding agent lifestyle (Oct 2025): review capacity is the bottleneck; prototypes prove technology choices; confirm the red step. https://simonwillison.net/guides/agentic-engineering-patterns/
- Osmani, my LLM coding workflow going into 2026 (Dec 2025) and interview-me skill (2026): spec then stepwise plan; hypothesis with confidence; a guess attached to each question; explicit out of scope. https://addyo.substack.com/p/my-llm-coding-workflow-going-into
- Beck, augmented coding (June 2025) and party of one for code review (Dec 2025): derailment signs; review asks whether the code does what was asked and stays understandable. https://newsletter.kentbeck.com/
- Hashimoto, my AI adoption journey (Feb 2026) and non-trivial vibing (Oct 2025): each rules-file line earned by a bad behaviour; give the agent a way to verify its work; plan in a saved spec file. https://mitchellh.com/writing/my-ai-adoption-journey
- Ronacher, agentic coding recommendations (June 2025), things that didn't work (July 2025), and 2026 essays: logging the agent can read, CLIs over MCP, most pre-written prompts go unused, defensive code from looped agents. https://lucumr.pocoo.org/
- Vincent, how I'm using coding agents (Oct 2025): one question per message, plans written for an engineer with no context, architect and implementer sessions. https://blog.fsck.com/2025/10/05/how-im-using-coding-agents-in-september-2025/
- Fowler fragments (Jan and Apr 2026): learning during implementation changes the spec; verified used to mean read by you; better review surfaces, not better prompts. https://martinfowler.com/fragments/

## Finding sources for a vertical

The named vertical decides where to look; these are the reliable places, in order:

- The official documentation and changelog of every tool the decision touches, read at the current version.
- The engineering blogs of organisations that run the system at the user's scale or larger, filtered to posts from the last two years.
- Conference talks and papers for anything contested, read directly rather than through a summary.
- The repository itself: the rules files, ADRs, workflows, and the task runner's recipes outrank any external source on what the user's system does today.

Skip aggregator listicles, content farms, and forum answers without a primary link.

## Old patterns to recognise in search results

- The April 2025 Claude Code best-practices blog post and its think-harder keyword ladder; the docs page replaced it and only `ultrathink` remains a keyword.
- Ultraplan, removed in 2026; plan mode is local.
- Custom slash commands as a separate feature; they are skills now.
- "Write a comprehensive CLAUDE.md describing the codebase"; long context files reduce adherence.
- "Always do TDD with the agent"; contested since mid-2026, with outcome sensors preferred.
- "AI makes experienced developers slower" as a general fact; the 2025 result is marked historical by its authors.
