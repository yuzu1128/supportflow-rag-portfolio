# SupportFlow RAG Operations Guide

## Scope

This guide covers local demo operations for the SupportFlow RAG portfolio and the operational expectations a reviewer should see during a walkthrough. It does not define a production on-call process for real customers.

## Local Operating Model

The demo should run with Docker Compose and expose:

- FastAPI backend
- React/Vite frontend
- Chroma vector store
- SQLite metadata and query log database
- Optional OpenRouter provider
- Optional Ollama local provider

The local environment should be labeled as Local Demo or Development in the UI. It should not imply production service status.

## Corpus Management

Source documents live in `sample_docs/` and are grouped by category:

- `01_user_manual`
- `02_faq`
- `03_incident_response`
- `04_api_specs`
- `05_release_notes`
- `06_test_specs`
- `07_support_templates`
- `08_operations_rules`

Ingestion should preserve source path, source ID, file type, category, and title where available.

## Reindex Procedure

1. Confirm the document corpus is available.
2. Run ingestion from the admin UI or backend ingestion endpoint.
3. Review document counts by category and file type.
4. Confirm chunk count and failed document count.
5. Run a small retrieval smoke test:
   - `AUTH_401`
   - `message.created`
   - `fallback queue`
   - `not helpful article suggestion`
6. Run the QA dataset evaluation.

## Evaluation Procedure

Use `evaluation/qa_dataset.json` as the benchmark source. The evaluation runner should measure:

- Recall@3
- Recall@5
- MRR
- Unanswerable-question accuracy
- Cited-answer rate
- Expected-keyword match rate

Every failed case should save:

- Question ID
- Question text
- Expected sources
- Retrieved sources
- Expected keywords
- Missing keywords
- Generated answer
- Failure reason

## Answer Review Rules

An answer is acceptable when it:

- Uses retrieved SupportFlow sources.
- Provides source citations.
- Contains the expected operational fact.
- Avoids unsupported claims.
- Says the documents do not state the answer when evidence is missing.

An answer is unacceptable when it:

- Invents secret values, named people, customer domains, or metrics.
- Omits sources.
- Uses unrelated documents as evidence.
- Gives a confident answer for an unanswerable question.

## Logs

The system should log:

- Timestamp
- Question
- Retrieval mode
- Provider type
- Retrieved source paths
- Scores
- Latency
- Answer status
- Citation count
- Error message when applicable

Logs should not store raw API keys, webhook secrets, or customer credentials.

## Incident Handling for the Demo

Common demo failures and expected response:

| Symptom | Likely Cause | Action |
| --- | --- | --- |
| No sources returned | Index missing or ingestion failed | Reindex and inspect document count. |
| API error-code questions fail | Keyword retrieval not active | Check exact-match path for CSV/JSON chunks. |
| Answers have no citations | Prompt or response parser issue | Inspect answer generation contract. |
| Unanswerable questions hallucinate | Evidence threshold too low | Raise minimum source confidence or add refusal rule. |
| Slow answers | LLM provider latency | Switch to local model or reduce context size. |

## Release Checklist

- Sample corpus has 30 to 50 documents.
- QA dataset has 30 to 50 cases.
- Evaluation report is updated after the latest run.
- UI shows local/demo environment status.
- Static presentation page opens without generated screenshots.
- README links to design, AWS architecture, operations, evaluation report, and presentation.

## Caveats

The sample PDF and DOCX sources are text placeholders, not binary documents. This is intentional for a lightweight portfolio repository. A production system would use validated parsers and malware scanning before indexing binary uploads.
