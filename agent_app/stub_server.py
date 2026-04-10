from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


class Handler(BaseHTTPRequestHandler):
    server_version = "spgci-stub/0.1"

    def _require_auth(self) -> bool:
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "missing_bearer_token"}).encode("utf-8")
            )
            return False
        return True

    def _send_json(self, payload: dict, *, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if not self._require_auth():
            return

        if self.path != "/api/unstructured/marketcommentary":
            self._send_json({"error": "not_found", "path": self.path}, status=404)
            return

        body = _read_json(self)

        # If no templates/fromDate/toDate provided, treat as "list templates".
        if not body or (
            "templates" not in body and "fromDate" not in body and "toDate" not in body
        ):
            self._send_json(
                {
                    "result": {
                        "templates": [
                            {
                                "template": "North Sea Crude Daily Summary",
                                "frequency": "daily",
                                "minPublishDate": "2026-01-01",
                                "maxPublishDate": "2026-03-07",
                            }
                        ],
                        "count": 1,
                    }
                }
            )
            return

        templates = body.get("templates") or []
        template = templates[0] if templates else "Unknown Template"
        from_date = body.get("fromDate")
        to_date = body.get("toDate")
        limit = int(body.get("limit") or 120)

        rows = [
            {
                "template": template,
                "publishDate": from_date,
                "rtpTimestamp": None,
                "createdDate": None,
                "id": "stub-1",
                "sourceId": "stub",
                "headline": f"Stub headline for {template}",
                "title": f"Stub title for {template}",
                "name": template,
                "contentType": "text/plain",
                "packageType": "stub",
                "sourceFilePath": None,
                "chunk": None,
                "content": f"Stub content for {template} from {from_date} to {to_date}.",
            }
        ]

        self._send_json(
            {
                "result": {
                    "rows": rows[:limit],
                    "count": len(rows[:limit]),
                    "requestedCount": len(rows),
                    "truncated": len(rows) > limit,
                    "truncationReason": "stub" if len(rows) > limit else None,
                }
            }
        )

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        # Keep stub output quiet by default.
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Local stub server for agent_app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4010)
    args = parser.parse_args()

    httpd = HTTPServer((args.host, args.port), Handler)
    print(f"Stub server listening on http://{args.host}:{args.port}")
    print("Implements: POST /api/unstructured/marketcommentary")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
