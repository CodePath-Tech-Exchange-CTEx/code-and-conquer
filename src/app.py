#############################################################################
# app.py
#
# Entrypoint for the StudySync app.
#############################################################################

import streamlit as st
from auth_flow import render_auth_flow
from backend.data_fetcher import get_my_groups, get_user_profile, get_final_recommendations, get_nearby_groups

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from pages.modules import (
    apply_styles,
    render_top_nav,
    display_user_profile,
    navigation_bar,
    display_explore_page,
    display_my_groups_page,
    display_genai_advice,
    display_account_settings_page
)

PAGES = ["Explore Groups", "My Groups", "User Profile", "AI Recommendations", "Account Settings"]


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
    st.query_params["authenticated"] = "true"
    if st.session_state.get("current_user_id"):
        st.query_params["uid"] = st.session_state["current_user_id"]


def display_app_page() -> None:
    # ── Authentication gate ───────────────────────────────────────────────────
    # Must be inside this function so set_page_config has already run
    # and st.query_params is fully accessible.
    # Nav links include ?authenticated=true so this persists across pages.
    if st.query_params.get("authenticated") == "true":
        st.session_state["authenticated"] = True
        if "uid" in st.query_params:
            st.session_state["current_user_id"] = st.query_params["uid"]

    if not st.session_state.get("authenticated", False):
        render_auth_flow()
        st.stop()

    if "page" not in st.session_state:
        st.session_state.page = "Explore Groups"

    query_page = normalize_page(st.query_params.get("page", st.session_state.page))
    st.session_state.page = query_page

    apply_styles()
    render_top_nav(selected_page=st.session_state.page)

    # -------------------------------------------------------------------------
    # MY GROUPS MODULE: BigQuery-backed data loading
    # Current test user: user-uuid-1
    # -------------------------------------------------------------------------
    current_user_id = st.session_state.get("current_user_id", "user-uuid-1")

    try:
        my_groups = get_my_groups(current_user_id)
    except Exception as exc:
        st.error(f"Unable to load My Groups: {exc}")
        my_groups = []

    # -------------------------------------------------------------------------
    # USER PROFILE MODULE: BigQuery-backed data loading
    # -------------------------------------------------------------------------
    try:
        profile = get_user_profile(current_user_id)
    except Exception as exc:
        st.error(f"Unable to load User Profile: {exc}")
        profile = None

    sync_query_params()

    # -------------------------------------------------------------------------
    # PAGE ROUTING
    # -------------------------------------------------------------------------
    page = st.session_state.page
    u_id = st.session_state.get("user_id")
    u_interests = st.session_state.get("about_me", "Computer Science")

    try:
        default_lon = -67.1452
        default_lat = 18.2110
        nearby_groups = get_nearby_groups(
            user_id=current_user_id,
            search="",
            filter=[],
            lon=default_lon,
            lat=default_lat
        )
    except Exception as exc:
        st.error(f"Unable to load Nearby Groups: {exc}")
        nearby_groups = []

    if page == "Explore Groups":
        filtered_list = navigation_bar(nearby_groups, current_user_id)
        display_explore_page(filtered_list)
    elif page == "My Groups":
        display_my_groups_page(my_groups)
    elif page == "User Profile":
        display_user_profile(profile)
    elif page == "AI Recommendations":
        display_genai_advice(user_id=u_id, user_interests=u_interests)
    elif page == "Account Settings":
        display_account_settings_page(u_id)


if __name__ == "__main__":
    display_app_page()