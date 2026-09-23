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
from dataclasses import dataclass, field

import streamlit as st
from dotenv import load_dotenv

from agent.export import to_excel_bytes, to_pdf_bytes, to_word_bytes
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


@dataclass
class AgentReply:
    answer: str
    records: list[dict] = field(default_factory=list)


def _handle_message(user_message: str) -> AgentReply:
    intent = parse_intent(user_message)
    if intent.needs_clarification or not intent.entity:
        question = intent.clarifying_question or "Could you clarify which records you're looking for?"
        return AgentReply(answer=question)

    client = _get_client()
    records = client.search(intent.entity, intent.filters)
    answer = format_response(user_message, records)
    return AgentReply(answer=answer, records=records)


def _render_export_buttons(records: list[dict]) -> None:
    if not records:
        return
    st.dataframe(records, use_container_width=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("Download Excel", to_excel_bytes(records), "crm_results.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col2:
        st.download_button("Download Word", to_word_bytes(records), "crm_results.docx",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with col3:
        st.download_button("Download PDF", to_pdf_bytes(records), "crm_results.pdf", "application/pdf")


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
                reply = _handle_message(user_message)
            st.markdown(reply.answer)
            _render_export_buttons(reply.records)
        st.session_state["messages"].append({"role": "assistant", "content": reply.answer})


if __name__ == "__main__":
    main()
