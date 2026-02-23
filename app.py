#############################################################################
# app.py
#
# Entrypoint for the Streamlit app. Minimal, robust routing between Home and
# My Groups pages. Uses functions exported from modules.py (above).
#
# Recommended run: `streamlit run app.py`
#############################################################################

import streamlit as st

# Import UI helpers (modules.py includes my-groups helpers too)
from modules import (
    display_my_custom_component,
    display_post,
    display_genai_advice,
    display_activity_summary,
    display_recent_workouts,
    display_my_groups_page,
    sample_groups,
)
from data_fetcher import (
    get_user_posts,
    get_genai_advice,
    get_user_profile,
    get_user_sensor_data,
    get_user_workouts,
)

userId = "user1"


def display_home_page():
    """Home page with a simple text input and user's posts/advice/workouts."""
    st.title("Welcome to SDS!")

    # small name input and custom component placeholder
    value = st.text_input("Enter your name")
    display_my_custom_component(value)

    # Example content area — try to display posts, advice, and workouts.
    st.markdown("## Example content")

    # Show GenAI advice (safe non-fatal)
    try:
        advice = get_genai_advice(userId)
        if advice:
            display_genai_advice(advice.get("timestamp", ""), advice.get("content", ""), advice.get("image"))
    except Exception:
        st.info("No GenAI advice available (development).")

    # Show user posts (non-fatal)
    try:
        posts = get_user_posts(userId)
        profile = get_user_profile(userId)
        for p in posts:
            display_post(
                username=profile.get("full_name", "Unknown"),
                user_image=profile.get("profile_image"),
                timestamp=p.get("timestamp", ""),
                content=p.get("content", ""),
                post_image=p.get("image"),
            )
    except Exception:
        st.info("No posts available (development).")

    # Show a brief workouts summary (non-fatal)
    try:
        workouts = get_user_workouts(userId)
        display_activity_summary(workouts)
        display_recent_workouts(workouts)
    except Exception:
        st.info("No workouts available (development).")


def display_groups_page():
    """Render the My Groups page with sample/demo data (replace with real fetch when ready)."""
    groups = sample_groups()
    display_my_groups_page(groups)


def main():
    """App entrypoint: sidebar navigation and routing."""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "My Groups"])

    if page == "Home":
        display_home_page()
    elif page == "My Groups":
        display_groups_page()
    else:
        st.write("Unknown page")


if __name__ == "__main__":
    # If user runs `python app.py` directly, call main() so script doesn't crash.
    # Recommended: run with `streamlit run app.py` to launch Streamlit server.
    main()
