# SupportFlow RAG Evaluation Report

## Status

Initial local evaluation completed with the bundled benchmark dataset.

Local check environment:

- LLM provider: `mock`
- Corpus source: bundled `sample_docs/`
- Indexed documents during local check: 42
- Evaluation cases: 40
- Command path: FastAPI `POST /api/evaluation/run`

## Dataset Summary

| Category | Count | Purpose |
| --- | ---: | --- |
| Simple lookup | 10 | Tests direct retrieval of one or two obvious sources. |
| Multi-document | 10 | Tests synthesis across manuals, rules, runbooks, templates, and release notes. |
| API/error named entities | 8 | Tests exact handling of endpoints, webhook events, and error codes. |
| Unanswerable | 7 | Tests refusal behavior for missing facts, secrets, unsupported metrics, and unrelated asks. |
| Vague/paraphrased | 5 | Tests semantic retrieval when the question does not reuse source wording. |
| Total | 40 | Portfolio-scale benchmark for local RAG evaluation. |

## Metrics to Report

| Metric | Definition | Target |
| --- | --- | ---: |
| Recall@3 | At least one expected source appears in top 3 retrieved sources. | 0.85+ |
| Recall@5 | At least one expected source appears in top 5 retrieved sources. | 0.95+ |
| MRR | Mean reciprocal rank of first expected source. | 0.70+ |
| Cited-answer rate | Generated answer includes at least one cited source when answerable. | 0.95+ |
| Expected-keyword match rate | Answer includes expected operational terms. | 0.80+ |
| Unanswerable accuracy | Missing-information cases are refused or qualified correctly. | 0.85+ |

`nDCG` and automated faithfulness scoring are useful extensions, but they are not required for the first portfolio evaluation.

## Initial Local Results

| Metric | Result | Notes |
| --- | ---: | --- |
| Recall@3 | 0.608 | Deterministic local retrieval baseline. |
| Recall@5 | 0.654 | Needs tuning before being presented as final quality. |
| MRR | 0.653 | First relevant source is often near the top but not consistently first. |
| Citation rate | 1.000 | Mock answer path cites retrieved context when available. |
| Unanswerable accuracy | 0.825 | Close to target; threshold and prompt rules need tuning. |
| Expected-keyword match rate | 0.688 | Useful signal for improving chunking and keyword boosts. |

These numbers are intentionally treated as a baseline, not as final claims. The portfolio should show both the measurement and the improvement backlog.

## Planned Evaluation Flow

1. Index the full `sample_docs/` corpus.
2. Run every case from `evaluation/qa_dataset.json`.
3. Store retrieved sources, rank, answer, citations, latency, and provider.
4. Calculate retrieval metrics first.
5. Calculate answer-quality checks from citations and expected keywords.
6. Review failures manually and record improvement actions.

## Expected Strengths

- Exact API codes such as `AUTH_401`, `RATE_429`, and `WEBHOOK_SIG_INVALID` should perform well when keyword retrieval is enabled.
- Simple queue, role, and SLA lookup questions should retrieve directly from manuals and operations rules.
- Multi-document cases should demonstrate the value of citations because answers often require a manual plus a runbook or template.

## Expected Risks

- Vague questions may retrieve adjacent but incomplete documents if semantic search dominates exact metadata.
- CSV rows may be chunked too coarsely unless row-level text is generated during ingestion.
- JSON documents may need field flattening so nested FAQ answers and webhook event names are searchable.
- Unanswerable questions require prompt and threshold controls; retrieval alone will often find a nearby but insufficient source.

## Failure Review Template

For every failed case, capture:

- Case ID
- Failure type: retrieval, answer, citation, keyword, or unanswerable
- Expected sources
- Retrieved sources
- Missing keyword or unsupported claim
- Root cause
- Proposed fix

## Initial Improvement Backlog

- Add exact-match boosts for uppercase error codes and endpoint-like paths.
- Normalize CSV rows into one chunk per row for FAQ and error-reference files.
- Add category metadata filters to the admin evaluation screen.
- Add explicit refusal examples to the answer prompt.
- Show the source rank and score next to each citation in the UI.
