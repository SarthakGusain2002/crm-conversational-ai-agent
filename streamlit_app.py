"""Conversational AI agent for a CRM system (SAP Cloud for Customer-style
OData backend), built as a Claude-powered chat UI over natural language.

Run:
    streamlit run streamlit_app.py

By default this runs against a fully synthetic sandbox dataset — no tenant
or credentials required. To point it at a real CRM OData tenant instead,
enter a tenant URL, username, and password in the sidebar (session-only,
never written to disk).
"""
import os

import streamlit as st
from dotenv import load_dotenv

from agent.middleware import format_response, parse_intent
from crm.client import CrmClient, CrmCredentials

load_dotenv()

st.set_page_config(page_title="CRM Conversational AI Agent", page_icon="💬", layout="wide")

SUGGESTED_PROMPTS = [
    "Show open opportunities",
    "Search accounts from Germany",
    "High priority tickets",
    "Show me account 1001",
    "Which leads are new",
]


def _get_client() -> CrmClient:
    tenant_url = st.session_state.get("tenant_url") or os.environ.get("CRM_TENANT_URL", "")
    username = st.session_state.get("username") or os.environ.get("CRM_USERNAME", "")
    password = st.session_state.get("password") or os.environ.get("CRM_PASSWORD", "")
    creds = CrmCredentials(tenant_url, username, password) if tenant_url else None
    return CrmClient(creds)


def _render_sidebar() -> None:
    with st.sidebar:
        st.header("Connection")
        st.session_state["tenant_url"] = st.text_input("Tenant URL", value=st.session_state.get("tenant_url", ""))
        st.session_state["username"] = st.text_input("Username", value=st.session_state.get("username", ""))
        st.session_state["password"] = st.text_input("Password", type="password", value=st.session_state.get("password", ""))
        if _get_client().live_mode:
            st.success("Connected to live tenant")
        else:
            st.info("Sandbox mode — using simulated CRM data. No tenant required.")

        st.divider()
        st.header("Try asking")
        for prompt in SUGGESTED_PROMPTS:
            if st.button(prompt, use_container_width=True):
                st.session_state["pending_prompt"] = prompt


def _handle_message(user_message: str) -> str:
    intent = parse_intent(user_message)
    if intent.needs_clarification or not intent.entity:
        return intent.clarifying_question or "Could you clarify which records you're looking for?"

    client = _get_client()
    records = client.search(intent.entity, intent.filters)
    return format_response(user_message, records)


def main() -> None:
    st.title("💬 CRM Conversational AI Agent")
    st.caption("Ask in plain English — the agent searches accounts, opportunities, leads, contacts, and service requests.")

    _render_sidebar()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    pending = st.session_state.pop("pending_prompt", None)
    user_message = pending or st.chat_input("Ask about accounts, opportunities, leads, contacts, or service requests...")

    if user_message:
        st.session_state["messages"].append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)

        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                answer = _handle_message(user_message)
            st.markdown(answer)
        st.session_state["messages"].append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
