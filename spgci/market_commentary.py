# Copyright 2026 S&P Global Energy (previously S&P Global Commodity Insights)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Market Commentary (AIRD) helpers.

Implements the executable workflow described in `market_commentary/skills.md`:
- list templates
- get market commentaries

Returns a `pandas.DataFrame` by default.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional, Sequence, Union

import pandas as pd
from pandas import DataFrame
from requests import Response

from spgci.api_client import post_market_commentary
_MAX_LIMIT = 120


def _as_yyyy_mm_dd(value: Union[str, date, datetime]) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.date().isoformat()
    return value.isoformat()


def _result_to_df(resp: Response, *, key: str) -> DataFrame:
    j = resp.json()
    result = j.get("result")
    if not isinstance(result, dict):
        raise ValueError("Unexpected response shape: missing 'result' object")

    rows = result.get(key, [])
    if rows is None:
        rows = []

    df = pd.DataFrame(rows)

    # Carry metadata for agents/consumers.
    df.attrs["spgci_market_commentary"] = {
        "count": result.get("count"),
        "requestedCount": result.get("requestedCount"),
        "truncated": result.get("truncated"),
        "truncationReason": result.get("truncationReason"),
    }

    return df


def list_templates(
    *,
    phrase: Optional[str] = None,
    raw: bool = False,
) -> Union[DataFrame, Response]:
    """List available Market Commentary templates.

    Parameters
    ----------
    phrase : Optional[str]
        Optional hint to filter/guide template discovery (if supported server-side).
    raw : bool
        If True, return the raw `requests.Response`.

    Returns
    -------
    Union[DataFrame, Response]
        DataFrame with templates (expected columns include `template`, `frequency`, ...)
        or the raw response.
    """

    body: Dict[Any, Any] = {}
    if phrase:
        body["phrase"] = phrase

    resp = post_market_commentary(body)
    if isinstance(resp, Response) and raw:
        return resp

    df = _result_to_df(resp, key="templates")  # type: ignore[arg-type]
    return df


def get_market_commentaries(
    *,
    templates: Sequence[str],
    from_date: Union[str, date, datetime],
    to_date: Union[str, date, datetime],
    limit: int = _MAX_LIMIT,
    raw: bool = False,
) -> Union[DataFrame, Response]:
    """Read Market Commentary content (unstructured).

    Parameters
    ----------
    templates : Sequence[str]
        Template(s) to read.
    from_date, to_date : Union[str, date, datetime]
        Date range (inclusive) as `YYYY-MM-DD` string or Python date/datetime.
    limit : int
        Max items to return (capped at 120).
    raw : bool
        If True, return the raw `requests.Response`.

    Returns
    -------
    Union[DataFrame, Response]
        DataFrame with rows (expected columns include `template`, `publishDate`, `content`, ...)
        or the raw response.
    """

    if not templates:
        raise ValueError("'templates' is required")

    if limit > _MAX_LIMIT:
        raise ValueError(f"limit is capped at {_MAX_LIMIT}")

    body: Dict[Any, Any] = {
        "templates": list(templates),
        "fromDate": _as_yyyy_mm_dd(from_date),
        "toDate": _as_yyyy_mm_dd(to_date),
        "limit": int(limit),
    }

    resp = post_market_commentary(body)
    if isinstance(resp, Response) and raw:
        return resp

    df = _result_to_df(resp, key="rows")  # type: ignore[arg-type]

    for col in ("publishDate", "rtpTimestamp", "createdDate"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")  # type: ignore[assignment]

    return df


class MarketCommentary:
    """Class wrapper for the Market Commentary skill.

    This mirrors the skill doc workflow:
    - list available templates
    - get commentary rows
    """

    def list_templates(
        self,
        *,
        phrase: Optional[str] = None,
        raw: bool = False,
    ) -> Union[DataFrame, Response]:
        return list_templates(phrase=phrase, raw=raw)

    def get_market_commentaries(
        self,
        *,
        templates: Sequence[str],
        from_date: Union[str, date, datetime],
        to_date: Union[str, date, datetime],
        limit: int = _MAX_LIMIT,
        raw: bool = False,
    ) -> Union[DataFrame, Response]:
        return get_market_commentaries(
            templates=templates,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            raw=raw,
        )
