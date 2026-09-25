"""Read-only ERPNext integration for JARVIS.

Talks to a Frappe/ERPNext site over its REST API:
  GET {base}/api/method/ping
  GET {base}/api/resource/<Doctype>            (list, with filters/fields)
  GET {base}/api/resource/<Doctype>/<name>     (single document)

Auth:  Authorization: token <api_key>:<api_secret>
Credentials come from the .env file:
  ERP_BASE_URL=<scheme>://<host>
  ERP_API_KEY=...
  ERP_API_SECRET=...
"""

from __future__ import annotations

import json
import os
import urllib.parse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MAX_RESULT_CHARS = 3500
DEFAULT_LIMIT     = 20
TIMEOUT_SECONDS   = 30


def erpnext_action(
    parameters: dict,
    player=None,
    session_memory=None,
) -> str:
    action   = (parameters.get("action") or "list").strip().lower()
    doctype  = (parameters.get("doctype") or "").strip()
    doc_name = (parameters.get("name") or "").strip()

    if action == "ping":
        return _request("/api/method/ping", None, player)

    if not doctype:
        msg = ("Sir, an ERPNext document type is required. "
               "Use one like Sales Order, Invoice, Lead, Quotation, Customer, or Item.")
        _log(msg, player)
        return msg

    if action == "get":
        if not doc_name:
            msg = f"Sir, I need the document name to read a specific {doctype}."
            _log(msg, player)
            return msg
        endpoint = "/api/resource/{}/{}".format(
            urllib.parse.quote(doctype), urllib.parse.quote(doc_name))
        params = None
    else:
        endpoint = "/api/resource/{}".format(urllib.parse.quote(doctype))
        params = _build_list_params(parameters)

    return _request(endpoint, params, player, doctype=doctype)


def _build_list_params(parameters: dict) -> dict | None:
    params: dict = {}

    limit = parameters.get("limit_page_length") or parameters.get("limit")
    if limit:
        try:
            params["limit_page_length"] = max(1, min(int(limit), 100))
        except (TypeError, ValueError):
            params["limit_page_length"] = DEFAULT_LIMIT
    else:
        params["limit_page_length"] = DEFAULT_LIMIT

    filters = parameters.get("filters")
    if filters:
        if isinstance(filters, str):
            try:
                filters = json.loads(filters)
            except (TypeError, ValueError):
                filters = None
        if filters:
            params["filters"] = json.dumps(filters)

    fields = parameters.get("fields")
    if fields:
        if isinstance(fields, str) and not fields.strip().startswith("["):
            fields = [f.strip() for f in fields.split(",") if f.strip()]
        elif isinstance(fields, str):
            try:
                fields = json.loads(fields)
            except (TypeError, ValueError):
                fields = None
        if fields:
            params["fields"] = json.dumps(fields)

    return params or None


def _request(endpoint: str, params: dict | None, player, doctype: str = "") -> str:
    base_url = (os.environ.get("ERP_BASE_URL") or "").strip().rstrip("/")
    api_key   = (os.environ.get("ERP_API_KEY") or "").strip()
    api_secret = (os.environ.get("ERP_API_SECRET") or "").strip()

    if not base_url:
        msg = "ERPNext is not configured yet: ERP_BASE_URL is missing from .env, sir."
        _log(msg, player)
        return msg
    if not api_key or not api_secret:
        msg = ("ERPNext does not have credentials yet: add ERP_API_KEY and "
               "ERP_API_SECRET to the .env file, sir.")
        _log(msg, player)
        return msg

    url = base_url + endpoint
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    request = Request(
        url,
        headers={
            "Authorization": f"token {api_key}:{api_secret}",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:500]
        msg = f"ERPNext returned HTTP {err.code}: {detail}"
        _log(msg, player)
        return msg
    except URLError as err:
        msg = f"Could not reach ERPNext at {base_url}: {err.reason}"
        _log(msg, player)
        return msg
    except (ValueError, TypeError) as err:
        msg = f"ERPNext returned unreadable data: {err}"
        _log(msg, player)
        return msg

    if endpoint.endswith("/ping"):
        msg = "ERPNext connection OK (pong)."
        _log(msg, player)
        return msg

    docs = payload
    if isinstance(payload, dict):
        if "data" in payload:
            docs = payload["data"]
        elif "message" in payload:
            docs = payload["message"]

    text = _format(docs, doctype, params)
    _log(text.splitlines()[0] if text else "ERPNext: empty result.", player)
    return text


def _format(docs, doctype: str, params: dict | None) -> str:
    if isinstance(docs, list):
        lines = [f"ERPNext {doctype}: {len(docs)} record(s)."]
        for index, item in enumerate(docs, start=1):
            lines.append(f"{index}. {_compact(item)}")
        text = "\n".join(lines)
    else:
        text = f"ERPNext {doctype}: {json.dumps(docs, ensure_ascii=False)}"

    if len(text) > MAX_RESULT_CHARS:
        text = text[:MAX_RESULT_CHARS] + "\n...[truncated]"
    return text


def _compact(item) -> str:
    if not isinstance(item, dict):
        return str(item)
    keys = ("name", "status", "docstatus", "customer", "company",
            "grand_total", "total", "due_date", "posting_date",
            "lead_name", "party_name", "subject", "item_name", "creation")
    parts = [f"{key}={item[key]}" for key in keys if key in item]
    if not parts:
        keys_left = list(item.keys())[:8]
        parts = [f"{k}={item[k]}" for k in keys_left]
    return ", ".join(parts)


def _log(message: str, player=None) -> None:
    print(f"[ERPNext] {message}")
    if player:
        try:
            player.write_log(f"JARVIS: {message}")
        except Exception:
            pass