import streamlit as st

PAGES = ["Explore Groups", "My Groups", "User Profile", "AI Recommendations", "Account Settings", "Create Groups"]

def normalize_page(raw_value: str) -> str:
    if not raw_value:
        return "Explore Groups"

    value = str(raw_value).strip().lower()
    for page in PAGES:
        if value == page.lower():
            return page
    return "Explore Groups"


def sync_query_params() -> None:
    st.query_params["page"] = st.session_state.page