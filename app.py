#############################################################################
# app.py
#
# Entrypoint for the app. Adds a simple page switcher so you can view the
# existing Home page and the "My Groups" page created in modules_mygroups.py.
#
#############################################################################

import streamlit as st

# existing modules (keep these if you still use them elsewhere)
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

# my-groups focused module (adjust name/path if you used a different filename)
# This file should contain display_my_groups_page and sample_groups as provided earlier.
from modules_mygroups import display_my_groups_page, sample_groups

# example user id used by other data fetchers
userId = 'user1'


def display_home_page():
    """Displays the home page of the app (original content)."""
    st.title('Welcome to SDS!')

    # An example of displaying a custom component called "my_custom_component"
    value = st.text_input('Enter your name')
    display_my_custom_component(value)

    # Example: show a few placeholder widgets that used to live on the page
    st.markdown("## Example content")
    # Pull and show the user's posts (if you want to keep; safe no-op if fetcher returns data)
    try:
        posts = get_user_posts(userId)
        for p in posts:
            display_post(
                username=get_user_profile(userId).get('full_name', 'Unknown'),
                user_image=get_user_profile(userId).get('profile_image'),
                timestamp=p.get('timestamp', ''),
                content=p.get('content', ''),
                post_image=p.get('image')
            )
    except Exception:
        # Don't crash the page if data fetchers are not ready — just skip.
        st.info("No posts available (development mode).")


def display_groups_page():
    """Displays the My Groups page using sample/demo data by default."""
    # You can replace sample_groups() with a real data fetcher when available.
    groups = sample_groups()
    display_my_groups_page(groups)


def main():
    """App entrypoint: shows a sidebar page selector and routes to the selected page."""
    # Simple sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "My Groups"])

    if page == "Home":
        display_home_page()
    elif page == "My Groups":
        display_groups_page()
    else:
        st.write("Unknown page")


if __name__ == '__main__':
    main()
