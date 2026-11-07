---
name: essay-summarizer
description: Produce a structured summary of an essay, blog post, academic paper, X/Twitter thread, or uploaded PDF article/report — covering author background, thesis, supporting evidence, the strongest counterargument, and references for further reading. Use this skill whenever the user's message is primarily a link or a PDF attachment of long-form written content (bare link/file, or paired with a trivial framing note like "thoughts?", "summarize", "tldr", "wdyt"). Common sources include Substack, Medium, personal blogs, arXiv/bioRxiv, X.com threads, and uploaded PDFs of academic papers, whitepapers, or technical reports. Do not trigger when the message includes a substantive question, request, or commentary alongside the link or file — those are normal conversation, not summary requests.
---

# Essay Summarizer

Turn a link or an uploaded PDF into a structured brief that lets the reader understand the piece *and think critically about it* in under a minute. The format is opinionated on purpose: it surfaces source credibility (Author), the actual claim (Thesis), how well it's argued (Supporting Evidence), what the piece is missing or getting wrong (Counter Argument), and where to dig further (References). A generic summary doesn't do this — it just compresses.

## When to use this skill

Trigger when the user's message is *primarily a link or an uploaded PDF* of long-form written content. The link or file can be paired with a trivial framing note that just signals "do your thing":

- "thoughts?", "wdyt", "thoughts on this?"
- "summarize", "summarize this", "tldr", "tl;dr"
- "what's this about?", "interesting?"

A bare PDF upload with no message at all also counts as a trigger — if the user attaches an article-shaped PDF and says nothing, treat it the same as a bare link.

Do **not** trigger when the message includes a substantive question, a specific kind of analysis request, or commentary that frames the conversation differently. Also do not trigger for PDFs that aren't long-form written content (resumes, contracts, forms, slide decks, datasheets, receipts) — those are clearly not articles even if uploaded silently. When in doubt, ask a one-line clarifier rather than defaulting to the full summary format.

### Triggering examples

| Message | Trigger? | Why |
| --- | --- | --- |
| `https://example.substack.com/p/post` | Yes | Bare link |
| `https://arxiv.org/abs/2401.01234 thoughts?` | Yes | Trivial framing note |
| `tldr: https://example.com/post` | Yes | Trivial framing note |
| `https://x.com/user/status/123` | Yes | X thread, treated as essay |
| *(PDF of an arXiv paper attached, no message)* | Yes | Bare PDF upload of an article |
| *(PDF of a whitepaper attached)* + `tldr` | Yes | PDF + trivial framing note |
| *(PDF of a technical report attached)* + `thoughts?` | Yes | PDF + trivial framing note |
| `https://example.com/post — does the author's argument about X hold up given the new MIT study?` | No | Substantive question; engage with it directly |
| `I disagree with this https://example.com/post — am I missing something?` | No | User wants conversation, not a summary |
| `Help me write a response to this: https://example.com/post` | No | Writing task |
| *(PDF attached)* + `extract the references section as a list` | No | Specific extraction task, not a summary |
| *(PDF resume attached)* + `thoughts?` | No | Not an article/report — fall back to normal review |

### Supported sources

Essays and blog posts (Substack, Medium, personal sites), academic papers (arXiv, bioRxiv, journals, lab pages), X/Twitter threads, and uploaded PDFs of articles, academic papers, whitepapers, or technical reports. **Not** intended for YouTube videos, podcasts, short news articles, or non-article PDFs (resumes, contracts, slide decks) — those are better handled conversationally or with a different skill.

## Output format

Use this exact structure, in this order, with bold inline labels rather than H1/H2 headings — it keeps the brief scannable:

> **Author:** ~1–2 sentences. Name, current role, and the expertise relevant to *this specific piece*. If the author is well-known in the field, that's enough; otherwise search the web (and LinkedIn or their personal site) for credentials, current affiliation, and prior work in the area.
>
> **Thesis:** ~2–3 sentences. The actual claim the essay is making — not a topic description ("this essay is about AI safety") but a position ("the author argues that X, because Y"). If the essay carries multiple connected claims, capture the spine.
>
> **Supporting Evidence:**
> - Roughly 3–6 bullets. Each one is a piece of rationale, evidence, data point, or argument the author leans on.
> - Be specific. Include numbers, study names, examples, or short quotes where they make the bullet sharper.
>
> **Counter Argument:** ~1–2 sentences. The strongest counter to the thesis — not a strawman. This requires its own research step (see workflow below). Frame it as "Critics argue…" or "The strongest pushback is…", and name a specific tradeoff or empirical claim, not just "some people disagree."
>
> **References:**
> - Roughly 3–6 bullets. Working URL + one-line description of what each adds.
> - Mix of: sources the author cites that are worth following up on, other relevant work by the same author, related pieces from other authors, and sources backing the counterargument.

The counts above are rough guidelines, not targets — let the material set the size. A simple piece doesn't need six evidence bullets; a dense one might warrant seven. Two short sentences usually read better than one long one stuffed with three claims. The whole output should still be readable in under a minute, with tight sentences and no filler.

### When the material is thin

If a section genuinely lacks substance — the author has no findable public footprint, the essay asserts a thesis but doesn't really argue for it, the topic is uncontroversial enough that there's no honest counterargument — say so directly rather than padding. A one-line "External signal on this author is thin; the newsletter launched recently and there's no clear LinkedIn match" is more useful than two sentences of vague filler. The reader should be able to tell the difference between "I researched this and here's what's there" and "I researched this and there's not much to find."

## Workflow

### 1. Get the content

**Uploaded PDF.** Read the file directly from `/mnt/user-data/uploads/`. If a `pdf-reading` skill is available, consult it for the right reading strategy — text-heavy papers can be extracted with `pdfplumber` or `pypdf`, scanned reports may need OCR, and slide-style PDFs may need page rasterization. Pull the title, author(s), affiliations, and abstract from the first one or two pages — these populate the Author and Thesis sections more reliably than guessing from the filename. If the PDF has a DOI or arXiv ID, note it for the References section.

**Linked content.** For most URLs, use `web_fetch` directly. For arXiv, fetch the abstract page (`/abs/`) rather than the PDF unless deeper detail is needed.

**X / Twitter is a special case.** Direct `web_fetch` on `x.com` and `twitter.com` URLs is blocked by robots.txt and will always fail — don't waste a turn on it. Go straight to `web_search` for the post (e.g., `web_search` with the author handle, status ID, or distinctive phrases from the thread). The search results return the full thread content reliably, and you can synthesize from them without a separate fetch.

A small note on `web_fetch`: it only accepts URLs that the user provided directly or that appeared in earlier search/fetch results. You can't construct a URL (e.g., a thread-reader or archive URL) and fetch it in the blind — find it via search first, then fetch from the result.

If the page is paywalled, gated, or returns minimal content, walk this fallback chain:

1. Web search the article title — there's often a syndicated or republished copy, a substantive third-party summary, or a cached version that comes back as a search hit you can then fetch
2. Search for the URL on the Wayback Machine (`web.archive.org`) or archive.today; fetch any result that comes back
3. If everything fails, write the summary from what's available (snippets, abstract, opening paragraphs) and clearly note in the reply that limited access constrained the result

### 2. Research the author

One or two web searches is usually enough: `[author name] [topic of essay]` or `[author name] [their employer/publication]`. Look for current role, prior work in the area, credentials, and any biases that affect how the reader should weight the piece. If a single sentence captures it, stop there — don't pad. If the author has limited public presence (newer writer, common name with no clear match, pseudonymous), name that fact in the Author line rather than inventing context.

### 3. Research the counter argument

This is the section that takes the most thought, and the one that's most valuable to the reader. The goal is *intellectual honesty*, not contrarianism. Search for:

- Direct critiques of the essay or the author's broader position
- Empirical evidence that complicates the thesis
- Mainstream or competing positions in the same debate
- Known tradeoffs the author has set aside or downplayed

If the thesis is uncontroversial or empirical and well-supported, say so explicitly — "the strongest pushback is methodological rather than substantive: [specific concern]" — rather than fabricating opposition.

### 4. Compose the summary

Write the brief in the exact format above. Read it back as if you were the user: would the bullets actually help them decide whether to read the full piece, and whether to trust it? If a bullet is just rephrasing the thesis, cut it.

## On quotes

Direct quotes can sharpen a bullet, but use them sparingly:

- Keep any quote under 15 words
- Use at most one quote from any single source
- Default to paraphrase — in a brief like this, paraphrase is almost always better than a quote

## On citations

Cite sources in every section, not just the research-heavy ones. Each Supporting Evidence bullet should carry a citation back to the fetched essay — readers may want to verify a specific claim, and a citation makes the verification one click instead of a re-read of the whole piece. Author and Counter Argument lines cite the web searches they came from. The References section is itself a list of links and doesn't need additional inline citations.

In short: if a sentence makes a factual claim, it should be traceable to a source.

## A note on author voice vs. your voice

The summary is *yours*, not the author's. State the thesis as "The author argues…" rather than slipping into the author's first person. The Counter Argument section in particular should make it clear the critique is research you did, not the essay's own self-criticism — readers should be able to tell the difference between what the piece claims and what others say about it.
