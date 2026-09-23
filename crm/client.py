"""CRM data access layer.

Two modes:
- Sandbox mode (default): filters the synthetic dataset in mock_data.py.
  Needs no credentials, no network access, no cost — this is what the repo
  runs in out of the box.
- Live mode: if a tenant URL + credentials are supplied at runtime (never
  hardcoded, never committed — see .env.example), issues a real OData GET
  request against a CRM system's REST/OData service and returns the parsed
  result in the same shape as sandbox mode.

Credentials are only ever held in memory for the current session; they are
never written to disk or logged.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from crm.mock_data import ENTITY_TABLES

ENTITY_ODATA_PATHS = {
    "accounts": "AccountCollection",
    "opportunities": "OpportunityCollection",
    "leads": "LeadCollection",
    "contacts": "ContactCollection",
    "service_requests": "ServiceRequestCollection",
}


@dataclass
class CrmCredentials:
    tenant_url: str
    username: str
    password: str

    @property
    def is_configured(self) -> bool:
        return bool(self.tenant_url and self.username and self.password)


class CrmClient:
    """Looks up CRM records by entity type and simple field filters."""

    def __init__(self, credentials: CrmCredentials | None = None):
        self.credentials = credentials

    @property
    def live_mode(self) -> bool:
        return bool(self.credentials and self.credentials.is_configured)

    def search(self, entity: str, filters: dict[str, str] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        if entity not in ENTITY_TABLES:
            raise ValueError(f"Unknown entity type: {entity}")
        if self.live_mode:
            return self._search_live(entity, filters)
        return self._search_sandbox(entity, filters)

    def _search_sandbox(self, entity: str, filters: dict[str, str]) -> list[dict[str, Any]]:
        rows = ENTITY_TABLES[entity]
        if not filters:
            return list(rows)
        results = []
        for row in rows:
            if all(str(row.get(k, "")).lower().find(str(v).lower()) != -1 for k, v in filters.items()):
                results.append(row)
        return results

    def _search_live(self, entity: str, filters: dict[str, str]) -> list[dict[str, Any]]:
        assert self.credentials is not None
        path = ENTITY_ODATA_PATHS[entity]
        odata_filter = " and ".join(f"substringof('{v}',{k})" for k, v in filters.items())
        params = {"$format": "json"}
        if odata_filter:
            params["$filter"] = odata_filter
        url = f"{self.credentials.tenant_url.rstrip('/')}/{path}"
        response = requests.get(
            url,
            params=params,
            auth=(self.credentials.username, self.credentials.password),
            timeout=15,
        )
        response.raise_for_status()
        return response.json().get("d", {}).get("results", [])
