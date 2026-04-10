---
name: market-commentary-aird
description: >
  Retrieve and synthesize unstructured Market Commentary from AIRD (OpenSearch-backed) sources
  via the `spgci` Python library. Use this skill whenever the user asks about commodity market
  commentary, price summaries, crude/energy/commodity reports, or any AIRD-sourced narrative
  content — even if they don't say "AIRD" or "market commentary" explicitly. Also use when the
  user wants to know what commentary templates/topics are available.
---

# Market Commentary (AIRD)

Fetch unstructured market commentary from AIRD via the `spgci` library.

---

## Step 1 — Discover available templates (when needed)

```python
import spgci as ci

templates_df = ci.MarketCommentary().list_templates()
```

**Templates DataFrame columns:**

| Column | Description |
|---|---|
| `template` | Template name to pass to the read step |
| `frequency` | Inferred cadence: daily / weekly / monthly / etc. |
| `minPublishDate` | Earliest available date (`YYYY-MM-DD`), if known |
| `maxPublishDate` | Latest available date (`YYYY-MM-DD`), if known |

> Skip this step if the user already specifies a template name.

---

## Step 2 — Read commentaries

```python
import spgci as ci

df = ci.MarketCommentary().get_market_commentaries(
    templates=["North Sea Crude Daily Summary"],
    from_date="2026-03-01",   # required, YYYY-MM-DD
    to_date="2026-03-07",     # required, YYYY-MM-DD
)
```

**Returns a `pandas.DataFrame`** — one row per commentary item.

**Key columns:**

| Column | Description |
|---|---|
| `template` | Source template |
| `publishDate` | Derived from `documentDate` |
| `headline` / `title` / `name` | Summary identifiers |
| `content` | Full commentary text — primary field for synthesis |
| `contentType` / `packageType` | Classification metadata |
| `chunk` | Chunk index (for multi-part documents) |
| `id` / `sourceId` / `sourceFilePath` | Identifiers / provenance |
| `rtpTimestamp` / `createdDate` | Timestamps |

**Truncation:** If the result set exceeds the server limit (max 120), `df.attrs["spgci_market_commentary"]` will contain:
`{ count, requestedCount, truncated, truncationReason }`

---

## Workflow by request type

### Content / information request
1. Infer `from_date` and `to_date` from the user's question.
2. If the template is unclear, call `list_templates` first and select the best match.
3. Call `get_market_commentaries` with the chosen template(s) and date range.
4. Synthesize your answer from the `content` column.

### Coverage / scope request ("what topics are available?")
1. Call `list_templates`.
2. Present results grouped by `frequency`.

---

## Rules
- `from_date` and `to_date` are **always required** for `get_market_commentaries`.
- Start with the **smallest reasonable date range**; expand only if results are insufficient.
- **Never repeat** an identical request after a truncation response — narrow the range or template instead.
- Results are entitlement-filtered server-side; missing data means the caller lacks access.