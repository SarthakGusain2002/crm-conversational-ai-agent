import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crm.client import CrmClient


def test_sandbox_search_all_accounts_with_no_filter():
    client = CrmClient()
    accounts = client.search("accounts")
    assert len(accounts) >= 5
    assert not client.live_mode


def test_sandbox_search_by_country_filter():
    client = CrmClient()
    results = client.search("accounts", {"country": "DE"})
    assert all(r["country"] == "DE" for r in results)
    assert len(results) >= 2


def test_sandbox_search_by_id():
    client = CrmClient()
    results = client.search("accounts", {"id": "1001"})
    assert len(results) == 1
    assert results[0]["name"] == "Prime LLC"


def test_sandbox_search_service_requests_by_priority():
    client = CrmClient()
    results = client.search("service_requests", {"priority": "High"})
    assert len(results) == 2
    assert all(r["priority"] == "High" for r in results)


def test_unknown_entity_raises():
    client = CrmClient()
    try:
        client.search("not_a_real_entity")
        assert False, "expected ValueError"
    except ValueError:
        pass
