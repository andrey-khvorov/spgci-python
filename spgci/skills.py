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

"""Runtime helpers to retrieve skill documentation.

This is intended for agent runtimes (ClaudeCode, etc.) that want to:
1) fetch the skill Markdown
2) follow the steps by calling executable wrappers (e.g., `spgci.market_commentary`)

Skill docs are fetched from the server:
- GET /api/skills/{name}
"""

from __future__ import annotations

from typing import Any, Dict, Union

from requests import Response

from spgci.api_client import get_data


def get_skill_doc(name: str, *, raw: bool = False) -> Union[str, Response]:
    """Fetch the skill documentation for a given skill name.

    Parameters
    ----------
    name : str
        Skill name, e.g. `marketcommentary`.
    raw : bool
        If True, return the raw `requests.Response`.

    Returns
    -------
    Union[str, Response]
        Markdown string or raw response.
    """

    if not name or not name.strip():
        raise ValueError("'name' is required")

    path = f"api/skills/{name.strip()}"
    resp = get_data(path=path, params={}, raw=True)
    if raw:
        return resp

    content_type = (resp.headers.get("content-type") or "").lower()

    # Some deployments may respond with JSON that wraps Markdown.
    if "application/json" in content_type:
        try:
            payload: Dict[str, Any] = resp.json()
            if isinstance(payload.get("markdown"), str):
                return payload["markdown"]
            if isinstance(payload.get("content"), str):
                return payload["content"]
        except Exception:
            pass

    return resp.text


def get_marketcommentary_skill_doc(*, raw: bool = False) -> Union[str, Response]:
    return get_skill_doc("marketcommentary", raw=raw)
