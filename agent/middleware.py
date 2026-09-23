"""Natural language <-> CRM middleware.

Dual-model pattern, same idea as the other repos in this portfolio:
- Claude Haiku handles intent parsing and simple result formatting — fast,
  cheap, used for the majority of turns.
- Claude Sonnet is only used when a turn needs deeper reasoning (summarizing
  a large/ambiguous result set, or synthesizing an insight across records)
  rather than just listing rows back to the user.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

from anthropic import Anthropic

HAIKU_MODEL = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-5"

ENTITIES = ["accounts", "opportunities", "leads", "contacts", "service_requests"]

INTENT_SYSTEM_PROMPT = f"""You translate a natural-language CRM request into a structured search.
Valid entity types: {", ".join(ENTITIES)}.
Respond with ONLY a JSON object, no other text, in this exact shape:
{{"entity": "<one of the valid entity types, or null if unclear>",
  "filters": {{"<field>": "<value>", ...}},
  "needs_clarification": <true|false>,
  "clarifying_question": "<a short question to ask the user, or null>"}}
Set needs_clarification to true if the entity type is ambiguous, or if a
search term doesn't clearly map to a specific record. Keep filters minimal —
only include a field if the user's message clearly implies it (e.g. a
country, an account name fragment, a priority level, a status).
"""

FORMAT_SYSTEM_PROMPT = """You are a CRM assistant. Given raw CRM records (as JSON) and the user's
original question, write a short, natural-language, conversational answer.
Reference specific record names/IDs where useful. If the list is empty, say
so plainly and suggest the user rephrase or broaden the search. Do not
invent any data not present in the records provided.
"""


@dataclass
class Intent:
    entity: str | None
    filters: dict[str, str]
    needs_clarification: bool
    clarifying_question: str | None


def _client() -> Anthropic:
    return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def parse_intent(user_message: str) -> Intent:
    response = _client().messages.create(
        model=HAIKU_MODEL,
        max_tokens=200,
        system=INTENT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    text = next((b.text for b in response.content if b.type == "text"), "{}")
    data = json.loads(text)
    return Intent(
        entity=data.get("entity"),
        filters=data.get("filters") or {},
        needs_clarification=bool(data.get("needs_clarification")),
        clarifying_question=data.get("clarifying_question"),
    )


def format_response(user_message: str, records: list[dict], complex_reasoning: bool = False) -> str:
    model = SONNET_MODEL if complex_reasoning or len(records) > 5 else HAIKU_MODEL
    response = _client().messages.create(
        model=model,
        max_tokens=400,
        system=FORMAT_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"User's question: {user_message}\n\nRecords (JSON):\n{json.dumps(records, indent=2)}",
            }
        ],
    )
    return next((b.text for b in response.content if b.type == "text"), "")
