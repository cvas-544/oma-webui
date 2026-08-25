# ---------------------------------------------------------------------------
# File:        create_langfuse_widgets.py
# Description: Create Langfuse dashboard widgets for all 5 Invertix feedback
#              signals via the Langfuse tRPC API.
#              Run: python3 scripts/create_langfuse_widgets.py --cookie <token>
# Author:      Vasu Chukka
# Co-author:   Claude Code
# ---------------------------------------------------------------------------
"""Create Langfuse dashboard widgets for Invertix feedback signals and failure tags.

Langfuse dashboard widgets use an internal tRPC API (not the public REST API).
Auth requires your browser session cookie: open cloud.langfuse.com, open
DevTools → Application → Cookies → copy the value of 'next-auth.session-token'.

Usage:
  python3 scripts/create_langfuse_widgets.py --cookie <token>               # feedback widgets (5)
  python3 scripts/create_langfuse_widgets.py --cookie <token> --failure-tags # failure_tag widgets (4)
  python3 scripts/create_langfuse_widgets.py --cookie <token> --all          # all 9 widgets
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from typing import Any

# ------------------------------------------------------------------ config ---

# Defaults — override via --project-id and --host CLI flags
DEFAULT_PROJECT_ID = "cmrn1h4nf0167ad0enuqskgoj"
DEFAULT_LANGFUSE_HOST = "https://cloud.langfuse.com"

# ----------------------------------------------------------------- widgets ---

WIDGETS: list[dict[str, Any]] = [
    {
        "name": "Thumbs Up",
        "description": "Number of explicit positive ratings (user_feedback = +1)",
        "view": "scores-numeric",
        "metrics": [{"measure": "value", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "user_feedback"},
            {"column": "value", "type": "number", "operator": ">=", "value": 1},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Thumbs Down",
        "description": "Number of explicit negative ratings (user_feedback = -1)",
        "view": "scores-numeric",
        "metrics": [{"measure": "value", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "user_feedback"},
            {"column": "value", "type": "number", "operator": "<=", "value": -1},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Copy to Clipboard",
        "description": "Times users copied a response — strong positive signal",
        "view": "scores-numeric",
        "metrics": [{"measure": "value", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "copy_to_clipboard"},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Download Artifact",
        "description": "PDF / Excel / chart downloads — user acted on the output",
        "view": "scores-numeric",
        "metrics": [{"measure": "value", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "download_artifact"},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Regenerate",
        "description": "Regeneration clicks — implicit dissatisfaction signal",
        "view": "scores-numeric",
        "metrics": [{"measure": "value", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "regenerate"},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Positive Feedback",
        "description": "Emoji ratings ≥ 3 (😊 😄) from the feedback popup — user was satisfied",
        "view": "scores-numeric",
        "metrics": [{"measure": "value", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "user_feedback_detail"},
            {"column": "value", "type": "number", "operator": ">=", "value": 3},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Negative Feedback",
        "description": "Emoji ratings ≤ 2 (😞 😐) from the feedback popup — user was dissatisfied",
        "view": "scores-numeric",
        "metrics": [{"measure": "value", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "user_feedback_detail"},
            {"column": "value", "type": "number", "operator": "<=", "value": 2},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
]

# Pie chart — feedback category distribution (Wrong Data, Not Helpful, etc.)
FEEDBACK_CATEGORIES_PIE: dict[str, Any] = {
    "name": "Feedback Category Breakdown",
    "description": "Distribution of thumbs-down category pills (Wrong Data, Not Helpful, etc.)",
    "view": "scores-categorical",
    "metrics": [{"measure": "count", "agg": "count"}],
    "dimensions": [{"field": "stringValue"}],
    "filters": [
        {"column": "name", "type": "string", "operator": "=", "value": "feedback_categories"},
    ],
    "chartType": "PIE",
    "chartConfig": {"type": "PIE"},
}

# Pie chart — positive vs negative feedback split from user_feedback (±1)
FEEDBACK_SENTIMENT_PIE: dict[str, Any] = {
    "name": "Feedback Sentiment",
    "description": "Positive vs Negative feedback split (user_feedback +1 / -1)",
    "view": "scores-numeric",
    "metrics": [{"measure": "value", "agg": "count"}],
    "dimensions": [{"field": "value"}],
    "filters": [
        {"column": "name", "type": "string", "operator": "=", "value": "user_feedback"},
    ],
    "chartType": "PIE",
    "chartConfig": {"type": "PIE"},
}

# Categorical failure-tag widgets — one per label (retrieval/route/prompt/infra).
# Uses scores-categorical view and stringValue column filter.
FAILURE_TAG_HISTOGRAM: dict[str, Any] = {
    "name": "Failure Tag Distribution",
    "description": "Count of bad traces per failure category (retrieval / route / prompt / infra)",
    "view": "scores-categorical",
    "metrics": [{"measure": "count", "agg": "count"}],
    "dimensions": [{"field": "stringValue"}],
    "filters": [
        {"column": "name", "type": "string", "operator": "=", "value": "failure_tag"},
    ],
    "chartType": "VERTICAL_BAR",
    "chartConfig": {"type": "VERTICAL_BAR"},
}

FAILURE_TAG_WIDGETS: list[dict[str, Any]] = [
    {
        "name": "Failure: Retrieval",
        "description": "Traces where agent used the right tool but pulled wrong data (bad filter, wrong plant/date)",
        "view": "scores-categorical",
        "metrics": [{"measure": "count", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "failure_tag"},
            {"column": "stringValue", "type": "string", "operator": "=", "value": "retrieval"},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Failure: Route",
        "description": "Traces where agent chose wrong tool, wrong order, or looped without progress",
        "view": "scores-categorical",
        "metrics": [{"measure": "count", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "failure_tag"},
            {"column": "stringValue", "type": "string", "operator": "=", "value": "route"},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Failure: Prompt",
        "description": "Traces where agent misunderstood intent, refused a valid request, or gave wrong format",
        "view": "scores-categorical",
        "metrics": [{"measure": "count", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "failure_tag"},
            {"column": "stringValue", "type": "string", "operator": "=", "value": "prompt"},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
    {
        "name": "Failure: Infra",
        "description": "Traces that failed due to sandbox crash, DB connection error, timeout, or missing lib",
        "view": "scores-categorical",
        "metrics": [{"measure": "count", "agg": "count"}],
        "dimensions": [],
        "filters": [
            {"column": "name", "type": "string", "operator": "=", "value": "failure_tag"},
            {"column": "stringValue", "type": "string", "operator": "=", "value": "infra"},
        ],
        "chartType": "NUMBER",
        "chartConfig": {"type": "NUMBER"},
    },
]

# ------------------------------------------------------------------ tRPC ----

def trpc_call(procedure: str, payload: dict, session_token: str, host: str) -> dict:
    """Call a Langfuse tRPC mutation with browser session token.

    cloud.langfuse.com (EU region) uses the cookie name:
      __Secure-next-auth.session-token.EU
    """
    url = f"{host}/api/trpc/{procedure}?batch=1"
    body = json.dumps({"0": {"json": payload}}).encode()
    # Try both EU and US region cookie names (cloud.langfuse.com = EU)
    cookie_str = (
        f"__Secure-next-auth.session-token.EU={session_token}; "
        f"__Secure-next-auth.session-token={session_token}"
    )
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Cookie": cookie_str,
            "Origin": host,
            "Referer": f"{host}/",
            "x-trpc-source": "nextjs-react",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise Exception(f"HTTP {e.code}: {body[:500]}")


def create_widget(widget_def: dict, session_token: str, project_id: str, host: str) -> str | None:
    payload = {
        "projectId": project_id,
        **widget_def,
    }
    try:
        resp = trpc_call("dashboardWidgets.create", payload, session_token, host)
        # tRPC batch response: [{"result": {"data": {"json": ...}}}]
        result = resp[0]["result"]["data"]["json"]
        widget_id = result.get("widget", {}).get("id") or result.get("id")
        print(f"  ✓  Created '{widget_def['name']}' → id={widget_id}")
        return widget_id
    except Exception as exc:
        print(f"  ✗  Failed '{widget_def['name']}': {exc}")
        return None


# --------------------------------------------------------------- main -------

def main() -> None:
    parser = argparse.ArgumentParser(description="Create Langfuse dashboard widgets")
    parser.add_argument("--cookie", required=True,
                        help="next-auth.session-token cookie value from your Langfuse login")
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID,
                        help=f"Langfuse project ID (default: {DEFAULT_PROJECT_ID})")
    parser.add_argument("--host", default=DEFAULT_LANGFUSE_HOST,
                        help=f"Langfuse host URL (default: {DEFAULT_LANGFUSE_HOST})")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--failure-tags", action="store_true",
                       help="Create only the 4 failure_tag count widgets")
    group.add_argument("--histogram", action="store_true",
                       help="Create 1 bar-chart widget showing all failure tags in one view")
    group.add_argument("--all", action="store_true",
                       help="Create all widgets (7 feedback + 4 failure_tag + 1 histogram + 1 pie)")
    group.add_argument("--sentiment-pie", action="store_true",
                       help="Create the Feedback Sentiment pie chart widget only")
    group.add_argument("--categories-pie", action="store_true",
                       help="Create the Feedback Category Breakdown pie chart widget only")
    args = parser.parse_args()

    if args.failure_tags:
        to_create = FAILURE_TAG_WIDGETS
    elif args.histogram:
        to_create = [FAILURE_TAG_HISTOGRAM]
    elif args.sentiment_pie:
        to_create = [FEEDBACK_SENTIMENT_PIE]
    elif args.categories_pie:
        to_create = [FEEDBACK_CATEGORIES_PIE]
    elif args.all:
        to_create = WIDGETS + FAILURE_TAG_WIDGETS + [
            FAILURE_TAG_HISTOGRAM, FEEDBACK_SENTIMENT_PIE, FEEDBACK_CATEGORIES_PIE
        ]
    else:
        to_create = WIDGETS

    print(f"Creating {len(to_create)} widgets in project {args.project_id} @ {args.host}…\n")
    widget_ids = []
    for w in to_create:
        wid = create_widget(w, args.cookie, args.project_id, args.host)
        if wid:
            widget_ids.append(wid)

    print(f"\nDone. {len(widget_ids)}/{len(to_create)} widgets created.")
    if widget_ids:
        print("\nWidget IDs (drag these into your Langfuse dashboard):")
        for wid in widget_ids:
            print(f"  {wid}")


if __name__ == "__main__":
    main()
