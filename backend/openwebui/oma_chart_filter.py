# ---------------------------------------------------------------------------
# File:        oma_chart_filter.py
# Description: OpenWebUI Function (Filter type) for inline chart rendering.
#              Upload via OpenWebUI Admin -> Functions -> New Function.
#              Set execution order AFTER oma_filter.py.
#
#              Stream behaviour (per-chunk, runs in real-time):
#                - Buffers text across chunks to catch split tags across SSE frames.
#                - Strips <!--OMA-CHART:{json}-->  tags and emits
#                  oma:chart so the OmaChartCard renders inline.
#
#              Outlet is a passthrough (stream handles everything).
#
# Author:      Vasu Chukka
# Co-author:   Claude Code
# ---------------------------------------------------------------------------
"""
OMA chart filter — renders Chart.js charts inline in chat messages.

How to install
--------------
1. OpenWebUI Admin -> Functions -> New Function
2. Paste this entire file as the function body
3. Save and set execution order AFTER the main oma_filter
4. The filter activates for all chats that use the OMA agent model.

How it works
------------
OpenWebUI JSON-parses each SSE chunk and calls Filter.stream(event=<dict>)
before the chunk content reaches the frontend. The stream filter:
  - Receives the parsed OpenAI ChatCompletionChunk dict (choices at top level)
  - Strips <!--OMA-CHART:{json}--> tags from delta.content
  - Emits oma:chart event with the parsed JSON config
  - Returns the modified dict

The Filter instance is cached by OpenWebUI for performance, so self._bufs
persists across chunks (required for multi-chunk tag buffering). Keys are
scoped by message_id to isolate concurrent conversations.
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Filter:
    """OpenWebUI Filter: extract OMA-CHART tags and emit chart events."""

    def __init__(self):
        self._bufs: dict = {}

    async def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        return body

    async def stream(
        self,
        event,
        __event_emitter__=None,
        __metadata__: Optional[dict] = None,
    ):
        try:
            if not isinstance(event, dict):
                return event

            choices = event.get("choices", [])
            if not choices:
                return event

            choice = choices[0]
            delta = choice.get("delta") or {}
            raw_content = delta.get("content", "") or ""
            finish_reason = choice.get("finish_reason")

            if not raw_content and not finish_reason:
                return event

            msg_id = (__metadata__ or {}).get("message_id", "_default")
            state = self._bufs.setdefault(msg_id, {"text": ""})

            clean_text = ""

            if raw_content:
                state["text"] += raw_content
                while True:
                    marker = "<!--OMA-CHART:"
                    open_i = state["text"].find(marker)
                    if open_i == -1:
                        if "<!--" in state["text"]:
                            cut = state["text"].rfind("<!--")
                            clean_text += state["text"][:cut]
                            state["text"] = state["text"][cut:]
                        else:
                            clean_text += state["text"]
                            state["text"] = ""
                        break
                    clean_text += state["text"][:open_i]
                    state["text"] = state["text"][open_i:]
                    close_i = state["text"].find("-->")
                    if close_i == -1:
                        break
                    tag = state["text"][:close_i + 3]
                    state["text"] = state["text"][close_i + 3:]
                    inner = tag[len(marker):-3]
                    try:
                        chart_config = json.loads(inner)
                        if __event_emitter__:
                            await __event_emitter__(
                                {"type": "oma:chart", "data": chart_config}
                            )
                        logger.info("Chart tag emitted: type=%s", chart_config.get("type", "?"))
                    except json.JSONDecodeError:
                        logger.warning("Malformed OMA-CHART JSON: %.120s", inner)

            if finish_reason:
                if state["text"]:
                    clean_text += state["text"]
                    state["text"] = ""
                self._bufs.pop(msg_id, None)

            if clean_text or raw_content:
                delta["content"] = clean_text

            return event

        except Exception as e:
            logger.exception("oma_chart_filter stream error: %s", e)
            return event

    async def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        return body
