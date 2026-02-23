#############################################################################
# app.py
#
# Entrypoint for the app with resilient imports so missing helpers won't crash
# the whole app during development.
#
#############################################################################

import streamlit as st

# Try to import UI helper functions from modules.py, but provide safe fallbacks
# if the names aren't present (prevents ImportError during early development).
try:
    from modules import (
        display_my_custom_component,
        display_post,
        display_genai_advice,
        display_activity_summary,
        display_recent_workouts,
    )
except Exception as e:
    # Log the import problem for debugging and provide simple fallbacks.
    st.warning(f"Warning: some UI helpers couldn't be imported from modules.py: {e}")

    # Minimal fallback implementations so the app remains runnable.
    def display_my_custom_component(value):
        """Fallback simple display for missing custom component."""
        st.write(f"(custom component) Hello, {value}")

    def display_post(username, user_image, timestamp, content, post_image):
        """Fallback: render a simple post."""
        st.markdown(f"**{username}** · _{timestamp}_")
        st.write(content)
        if post_image:
            st.image(post_image)

    def display_genai_advice(timestamp, content, image):
        """Fallback GenAI advice card."""
        st.subheader("GenAI Advice")
        st.markdown(f"_{timestamp}_")
        st.write(content)
        if image:
            st.image(image)

    def display_activity_summary(workouts_list):
        """Fallback minimal activity summary."""
        st.subheader("Activity Summary")
        if not workouts_list:
            st.info("No workouts.")
            return
        st.write(f"Workouts: {len(workouts_list)}")

    def display_recent_workouts(workouts_list):
        """Fallback recent workouts list."""
        st.subheader("Recent Workouts")
        for w in workouts_list or []:
            st.write(w)

# Import the data fetchers as before
from data_fetcher import (
    get_user_posts,
    get_genai_advice,
    get_user_profile,
    get_user_sensor_data,
    get_user_workouts,
)

# Import the My Groups module (adjust name if you saved it differently)
# If your groups module is integrated into modules.py, change this to `from modules import display_my_groups_page, sample_groups`
try:
    from modules_mygroups import display_my_groups_page, sample_groups
except Exception as e:
    st.warning(f"Warning: couldn't import modules_mygroups: {e}")

    # If modules_mygroups is missing, provide minimal fallbacks to keep the UI working
    def sample_groups():
        return []

    def display_my_groups_page(groups):
        st.info("My Groups page not available (modules_mygroups import failed).")

# example user id used by other data fetchers
userId = "user1"


def display_home_page():
    """Displays the home page of the app (original content)."""
    st.title("Welcome to SDS!")

    # An example of displaying a custom component called "my_custom_component"
    value = st.text_input("Enter your name")
    display_my_custom_component(value)

    # Example: attempt to show the user's posts (non-fatal if fetching fails)
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
        # do not crash the page; just show info
        st.info("User posts unavailable.")


def display_groups_page():
    """Displays the My Groups page using sample/demo data by default."""
    groups = sample_groups()
    display_my_groups_page(groups)


def main():
    """App entrypoint: shows a sidebar page selector and routes to the selected page."""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "My Groups"])

    if page == "Home":
        display_home_page()
    elif page == "My Groups":
        display_groups_page()
    else:
        st.write("Unknown page")


if __name__ == "__main__":
    main()
