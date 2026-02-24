#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
import streamlit as st

# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Write a good docstring here."""
    pass


def display_user_profile(profile):
    """
    Render the complete user profile page.

    Args
        profile : dict – All profile data for the user. Expected keys:
            'first_name'          : str
            'last_name'           : str
            'major'               : str
            'year'                : str  (e.g. "Junior Year")
            'university'          : str
            'email'               : str
            'about_me'            : str
            'focus_subjects'      : list[str]
            'groups_joined'       : int
            'study_hours'         : int
            'day_streak'          : int
            'weekly_availability' : list[dict] with keys 'day' and 'slots' (list[str])

    Example
        profile = {
            "first_name": "Jane", "last_name": "Doe",
            "major": "Computer Science", "year": "Junior Year",
            "university": "Stanford University", "email": "jane.doe@stanford.edu",
            "about_me": "Passionate about algorithms and AI...",
            "focus_subjects": ["Data Structures", "Machine Learning"],
            "groups_joined": 4, "study_hours": 127, "day_streak": 12,
            "weekly_availability": [
                {"day": "Mon", "slots": ["9-11 AM", "2-4 PM"]},
                {"day": "Tue", "slots": ["1-3 PM"]},
            ],
        }
        display_user_profile(profile)
    """
    if not profile:
        st.warning("No profile data available.")
        return

    # ── Header ────────────────────────────────────────────────────────────────
    initials = (profile["first_name"][0] + profile["last_name"][0]).upper()
    col_avatar, col_info, col_btns = st.columns([1, 5, 2])

    with col_avatar:
        st.markdown(f"## {initials}")

    with col_info:
        st.subheader(f"{profile['first_name']} {profile['last_name']}")
        st.caption(f"{profile['major']} · {profile['year']}")
        st.write(f"🏛 {profile['university']}   ✉ {profile['email']}")

    with col_btns:
        st.button("Edit Profile", use_container_width=True)
        st.button("Share Profile", use_container_width=True)

    st.divider()

    # ── About Me ──────────────────────────────────────────────────────────────
    st.markdown("**ABOUT ME**")
    st.write(profile["about_me"])

    st.markdown("**FOCUS SUBJECTS**")
    st.write("  ".join([f"`{s}`" for s in profile["focus_subjects"]]))

    st.divider()

    # ── Stats ─────────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    col1.metric("Groups Joined", profile["groups_joined"])
    col2.metric("Study Hours", profile["study_hours"])
    col3.metric("Day Streak", profile["day_streak"])

    st.divider()

    # ── Weekly Availability ───────────────────────────────────────────────────
    avail_col, btn_col = st.columns([4, 1])
    avail_col.markdown("**Weekly Availability**")
    btn_col.button("Update Schedule", use_container_width=True)

    cols = st.columns(len(profile["weekly_availability"]))
    for col, day_data in zip(cols, profile["weekly_availability"]):
        with col:
            st.markdown(f"**{day_data['day']}**")
            for slot in day_data["slots"]:
                st.caption(slot)


def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
