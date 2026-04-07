# Market Commentary (AIRD) — Skill

This skill lets a client retrieve **unstructured** Market Commentary content from AIRD (OpenSearch-backed) sources.

It is intentionally modeled like a “Claude skills” workflow: **discover what’s available**, then **read the relevant items** and feed them into your LLM / downstream pipeline.

---

## Endpoints

### 1) List available Market Commentary templates

Use this when the customer asks about the *library/scope* of market commentaries, or when you need to pick the right template(s) before reading.

Preferred:

`POST /api/unstructured/marketcommentary`

Body (JSON):

```json
{}
```

Response (JSON):
- `result.templates[]`: items with:
  - `template`: the template name to use in the read step
  - `frequency`: best-effort inferred frequency (daily/weekly/monthly/etc)
  - `minPublishDate` (optional): `YYYY-MM-DD` if available
  - `maxPublishDate` (optional): `YYYY-MM-DD` if available
- `result.count`

Example:

```json
{}
```

---

### 2) Read Market Commentary content (unstructured data)

Use this when the customer wants the actual Market Commentary content.

Preferred:

`POST /api/unstructured/marketcommentary`

Body (JSON):

```json
{
  "templates": ["Template A", "Template B"],
  "fromDate": "YYYY-MM-DD",
  "toDate": "YYYY-MM-DD",
  "limit": 120
}
```

Notes:
- `limit` is optional and capped at 120.

Response (JSON):
- `result.rows[]`: tabular rows (one per commentary item)
- `result.count`: number of rows returned
- `result.requestedCount`: number of matched items before truncation
- `result.truncated`: whether the response was truncated to `limit`
- `result.truncationReason` (optional): human-readable truncation note

Row columns (current):
- `template`
- `publishDate` (derived from `documentDate`)
- `rtpTimestamp`, `createdDate`
- `id`, `sourceId`
- `headline`, `title`, `name`
- `contentType`, `packageType`
- `sourceFilePath`, `chunk`
- `content`

Important limits:
- The endpoint will **never fail** purely because too many items match.
- If the match set exceeds `limit` (max 120), the endpoint returns the **most recent/highest scoring** items up to `limit` and sets `result.truncated=true`.

Example:

```json
{
  "templates": ["North Sea Crude Daily Summary"],
  "fromDate": "2026-03-01",
  "toDate": "2026-03-07"
}
```

---

## Question Types (workflow)

### Content / information request

1. Infer `fromDate` and `toDate` from the user question (use `YYYY-MM-DD`).
2. (Optional) call the **list** endpoint to identify the best matching template(s).
3. Call the **read** endpoint with the selected template(s) and the date range.
4. Use `result.rows[]` as the context for your answer/synthesis.

### Coverage / scope of commentaries

1. Call the **list** endpoint (optionally with a `phrase` hint).
2. Present the returned templates (grouping by `frequency` if useful).

---

## Rules

- Do not repeat the **read** request with identical parameters if the response indicates too many results.
- Always include `fromDate` and `toDate` for **read**.
- Start with the smallest appropriate date range, then expand only if needed.
- Requests are entitlement-aware; results are filtered by the caller’s entitled packages.

---

## Skill Doc Endpoint

This document itself can be fetched via:

`GET /api/skills/marketcommentary`
