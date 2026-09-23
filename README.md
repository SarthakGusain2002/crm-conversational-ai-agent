# CRM Conversational AI Agent

A conversational AI agent that lets you search a CRM system in plain English
instead of clicking through menus and filters — and export whatever it finds
straight to Excel, Word, or PDF. Originally built as a personal hackathon
project exploring how far natural language could replace manual CRM
navigation, then rebuilt here as a clean, standalone, credential-free demo.

## Why this exists

Sales and service teams spend a lot of time navigating CRM screens to find
customer information, opportunities, leads, and tickets — learning filter
options, remembering field names, clicking through multiple views just to
answer a simple question. This project explores replacing that with a chat
interface: ask "show me open opportunities" or "high priority tickets from
Germany" and get an answer back immediately, in natural language.

## How it works

```
 user types in plain English
        │
        ▼
┌───────────────────┐        ┌─────────────────────┐
│  Streamlit chat UI  │──────▶│  Intent parsing       │  Claude Haiku
│  (streamlit_app.py) │        │  (agent/middleware.py)│  → {entity, filters,
└───────────────────┘        └──────────┬───────────┘     needs_clarification}
        ▲                                │
        │                                ▼
        │                     ┌─────────────────────┐
        │                     │  CRM client           │  sandbox mode (mock data)
        │                     │  (crm/client.py)      │  or live OData mode
        │                     └──────────┬───────────┘
        │                                │
        │                                ▼
        │                     ┌─────────────────────┐
        └─────────────────────│  Response formatting  │  Claude Haiku or Sonnet
                               │  (agent/middleware.py)│  (Sonnet for larger/
                               └─────────────────────┘   more complex results)
```

1. **Intent parsing** — Claude Haiku turns a natural-language message into a
   structured search: which entity type (accounts, opportunities, leads,
   contacts, service requests), which filters, and whether the request is
   too ambiguous to search yet. If it's ambiguous, the agent asks a
   clarifying question instead of guessing — e.g. searching for "CTS" might
   return several partial matches and the agent will ask you to confirm
   which one you meant, rather than picking one at random.
2. **CRM lookup** — `crm/client.py` searches either a fully synthetic
   sandbox dataset (default, no setup required) or, if you provide a tenant
   URL and credentials in the sidebar, a real CRM OData service, using the
   exact same interface either way.
3. **Response formatting** — Claude formats the raw records into a natural
   answer. Simple lookups use Haiku; larger or more ambiguous result sets
   use Sonnet, since that needs more reasoning to summarize well. This is
   the same dual-model, cost-conscious pattern used across this portfolio.
4. **Export** — every result set is also shown as a table in the UI, with
   one-click export to Excel, Word, or PDF (`agent/export.py`), so a result
   can be shared as a report rather than only read in the chat window.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
streamlit run streamlit_app.py
```

By default the app runs in **sandbox mode** against a small synthetic
dataset (generic company names, no real data) — no CRM tenant or
credentials needed to try it. To connect to a real CRM OData tenant instead,
enter a tenant URL, username, and password in the sidebar at runtime.
Credentials are held only in the Streamlit session for that run — never
written to disk, logged, or committed.

## Data & security notes

- All CRM data shipped in this repo (`crm/mock_data.py`) is fully synthetic —
  generic company/contact names invented for this demo, not real customers.
- No tenant URL or credentials are hardcoded anywhere in the code. Any real
  values you use locally belong in `.env` (gitignored) or are entered
  directly in the running app's sidebar.
- The OData integration in `crm/client.py` uses the tenant's existing
  authentication (basic auth over HTTPS) rather than any custom auth
  scheme — the agent never bypasses the CRM system's own access control.

## Tests

```bash
pip install pytest
pytest tests/
```

Tests cover the deterministic sandbox search logic in `crm/client.py` only —
no API key required, keeping test runs free and fast (the same
cost-conscious testing approach used elsewhere in this portfolio).

## Tech stack

Python, Streamlit, `anthropic` SDK (Claude Haiku + Sonnet, dual-model),
`requests` for OData calls, `python-dotenv` for local config, `pandas` +
`openpyxl` (Excel export), `python-docx` (Word export), `reportlab` (PDF
export), `pytest`.
