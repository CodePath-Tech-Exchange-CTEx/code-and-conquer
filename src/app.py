#############################################################################
# app.py
#
# Entrypoint for the StudySync app.
#############################################################################

import streamlit as st
from backend.data_fetcher import get_my_groups, get_user_profile, get_final_recommendations, get_explore_page_groups
from pages.explore import display_explore_page
from pages.my_groups import display_my_groups_page
from backend.page_loader import sync_query_params, normalize_page

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from components import navigation_bar

from pages.modules import (
    apply_styles,
    render_top_nav,
    display_user_profile,
    display_genai_advice, 
    display_account_settings_page
)


def display_app_page() -> None:
    apply_styles()
    if "page" not in st.session_state:
        st.session_state.page = "Explore Groups"

    query_page = normalize_page(st.query_params.get("page", st.session_state.page))
    st.session_state.page = query_page

    render_top_nav(selected_page=st.session_state.page)

    # -------------------------------------------------------------------------
    # MY GROUPS MODULE: BigQuery-backed data loading
    #
    # This section fetches real "My Groups" data from BigQuery for the
    # My Groups page only.
    #
    #
    # Current test user:
    #   user-uuid-1
    # -------------------------------------------------------------------------
    current_user_id = "user-uuid-1"

    try:
        my_groups = get_my_groups(current_user_id)
    except Exception as exc:
        st.error(f"Unable to load My Groups: {exc}")
        my_groups = []

    # -------------------------------------------------------------------------
    # USER PROFILE MODULE: BigQuery-backed data loading
    #
    # Fetches real profile data from the Users and GroupMemberships tables.
    # -------------------------------------------------------------------------
    try:
        profile = get_user_profile(current_user_id)
    except Exception as exc:
        st.error(f"Unable to load User Profile: {exc}")
        profile = None

    sync_query_params()


    # -------------------------------------------------------------------------
    # PAGE ROUTING
    #
    # My contribution:
    #   - "My Groups" page uses BigQuery data through get_my_groups()
    #
    # Teammates' sections:
    #   - "Explore Groups"
    #   - "User Profile"
    #   - "AI Recommendations"
    # -------------------------------------------------------------------------
    page = st.session_state.page
    u_id = st.session_state.get("user_id")
    u_interests = st.session_state.get("about_me", "Computer Science")

    # --- The Fixed Fetch for Nearby Groups ---
    try:
        # Set up default values for the map (e.g., UPRM coordinates)
        default_lon = -67.1452 
        default_lat = 18.2110
        
        # If your app has search bars later, you can replace these empty values!
        current_search = ""
        current_filter = [] 

        # Call the function with all 5 required arguments
        nearby_groups = get_explore_page_groups(
            user_id=current_user_id, 
            search=current_search, 
            filter=current_filter, 
            lon=default_lon, 
            lat=default_lat
        )
    except Exception as exc:
        st.error(f"Unable to load Nearby Groups: {exc}")
        nearby_groups = []

    if page == "Explore Groups":
        filtered_list = navigation_bar(nearby_groups, current_user_id)
        display_explore_page(current_user_id,filtered_list)
    elif page == "My Groups":
        display_my_groups_page(my_groups, current_user_id=current_user_id)
    elif page == "User Profile":
        display_user_profile(profile)
    elif page == "AI Recommendations":
        display_genai_advice(user_id=u_id, user_interests=u_interests)
    elif page == "Account Settings":
        display_account_settings_page(u_id)




if __name__ == "__main__":
    display_app_page()
