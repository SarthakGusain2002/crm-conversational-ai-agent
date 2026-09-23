"""Generic, fully synthetic CRM data used when no live tenant is configured.

None of these companies, contacts, or IDs are real. They exist so the app is
demoable out of the box without needing a live OData tenant.
"""

ACCOUNTS = [
    {"id": "1001", "name": "Prime LLC", "country": "US", "industry": "Manufacturing"},
    {"id": "1002", "name": "Nikon Corp", "country": "DE", "industry": "Electronics"},
    {"id": "1003", "name": "IronWorks", "country": "DE", "industry": "Industrial"},
    {"id": "1004", "name": "Enterasys", "country": "UK", "industry": "Networking"},
    {"id": "1005", "name": "Rude Traders", "country": "FR", "industry": "Retail"},
    {"id": "1006", "name": "Acme Corporation", "country": "US", "industry": "Logistics"},
]

OPPORTUNITIES = [
    {"id": "OPP-2001", "account_id": "1001", "name": "Prime LLC — Line upgrade", "stage": "Won", "value": 84000},
    {"id": "OPP-2002", "account_id": "1002", "name": "Nikon Corp — Sensor rollout", "stage": "Open", "value": 42000},
    {"id": "OPP-2003", "account_id": "1004", "name": "Enterasys — Network refresh", "stage": "Open", "value": 61000},
    {"id": "OPP-2004", "account_id": "1006", "name": "Acme Corporation — Fleet contract", "stage": "Open", "value": 120000},
]

LEADS = [
    {"id": "LEAD-3001", "name": "Jonas Weber", "company": "Berlin Mfg GmbH", "country": "DE", "status": "New"},
    {"id": "LEAD-3002", "name": "Priya Nair", "company": "Coastal Retail", "country": "IN", "status": "Contacted"},
]

CONTACTS = [
    {"id": "CON-4001", "account_id": "1001", "name": "Maria Alvarez", "role": "Procurement Lead"},
    {"id": "CON-4002", "account_id": "1004", "name": "Tom Richards", "role": "IT Director"},
]

SERVICE_REQUESTS = [
    {"id": "SR-5001", "account_id": "1002", "subject": "Sensor calibration issue", "priority": "High", "status": "Open"},
    {"id": "SR-5002", "account_id": "1004", "subject": "VPN connectivity drop", "priority": "High", "status": "Open"},
    {"id": "SR-5003", "account_id": "1001", "subject": "Invoice discrepancy", "priority": "Low", "status": "Closed"},
]

ENTITY_TABLES = {
    "accounts": ACCOUNTS,
    "opportunities": OPPORTUNITIES,
    "leads": LEADS,
    "contacts": CONTACTS,
    "service_requests": SERVICE_REQUESTS,
}
