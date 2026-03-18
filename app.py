#############################################################################
# app.py
#
# Entrypoint for the StudySync app.
# Theme handling is delegated to Streamlit's built-in light/dark support
# through .streamlit/config.toml.
#############################################################################

import streamlit as st

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from modules import (
    apply_styles,
    render_top_nav,
    display_user_profile,
    navigation_bar,
    display_explore_page,
    display_genai_advice,
    display_my_groups_page,
)

PAGES = ["Explore Groups", "My Groups", "User Profile", "AI Recommendations"]


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


def display_app_page() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "Explore Groups"

    query_page = normalize_page(st.query_params.get("page", st.session_state.page))
    st.session_state.page = query_page

    apply_styles()

    render_top_nav(selected_page=st.session_state.page)

    matches_data = [
        {
            "major": "Computer Science",
            "title": "GenAI & Systems Design",
            "match_pct": 98,
            "keywords": ["Algorithms", "Python", "GenAI"],
            "time": "Tuesdays 5:00 PM",
            "location": "Fisk Library",
            "members": "3/5",
        },
        {
            "major": "Computer Science",
            "title": "iOS Dev Hackers",
            "match_pct": 92,
            "keywords": ["Swift", "Hackathons", "App Dev"],
            "time": "Fridays 3:00 PM",
            "location": "Nashville Tech Hub",
            "members": "4/6",
        },
        {
            "major": "Computer Science",
            "title": "Technical Interview Prep",
            "match_pct": 85,
            "keywords": ["Data Structures", "Mock Interviews"],
            "time": "Wednesdays 6:00 PM",
            "location": "Remote / Discord",
            "members": "2/4",
        },
    ]

    profile = {
        "first_name": "Jane",
        "last_name": "Doe",
        "major": "Computer Science",
        "year": "Junior Year",
        "institution": "Stanford University",
        "email": "jane.doe@stanford.edu",
        "about_me": "Passionate about algorithms, AI, and building products that make learning more collaborative.",
        "focus_subjects": ["Data Structures", "Machine Learning"],
        "groups_joined": 4,
        "study_hours": 127,
        "day_streak": 12,
        "weekly_availability": [
            {"day": "Mon", "slots": ["9–11 AM", "2–4 PM"]},
            {"day": "Tue", "slots": ["1–3 PM"]},
            {"day": "Wed", "slots": ["6–8 PM"]},
        ],
    }

    mock_study_groups = [
        {
            "group_title": "Calc II Cram Session",
            "subject": "Math",
            "description": "Preparing for the midterm with problem-solving drills and quick review sheets.",
            "date": "Oct 12",
            "time": "4:00 PM",
            "location": "Library Room 3",
            "members": "4/6",
        },
        {
            "group_title": "Bio 101 Lab Prep",
            "subject": "Science",
            "description": "Reviewing cell structures, lab notes, and quiz questions before Friday.",
            "date": "Oct 13",
            "time": "2:00 PM",
            "location": "Science Hall",
            "members": "2/4",
        },
        {
            "group_title": "Art History Chat",
            "subject": "Arts",
            "description": "A discussion-based session focused on Renaissance themes and major works.",
            "date": "Oct 15",
            "time": "11:00 AM",
            "location": "Cafe Blue",
            "members": "8/10",
        },
        {
            "group_title": "Python Basics",
            "subject": "CS",
            "description": "Looping, conditionals, and debugging practice for beginners.",
            "date": "Oct 16",
            "time": "6:00 PM",
            "location": "Zoom",
            "members": "12/20",
        },
    ]

    my_groups = [
        {
            "title": "Advanced Chemistry",
            "icon": "🧪",
            "days": "Tue & Wed",
            "mode": "In person",
            "location": "Science Hall",
            "members": "4/6",
        },
        {
            "title": "Astronomy",
            "icon": "🔭",
            "days": "Mon & Wed",
            "mode": "Online",
            "location": "Zoom",
            "members": "5/8",
        },
        {
            "title": "Biology",
            "icon": "🧬",
            "days": "Saturday",
            "mode": "In person",
            "location": "Fisk Library",
            "members": "3/6",
        },
    ]

    sync_query_params()

    page = st.session_state.page

    if page == "Explore Groups":
        filtered_list = navigation_bar(mock_study_groups)
        display_explore_page(filtered_list)
    elif page == "My Groups":
        display_my_groups_page(my_groups)
    elif page == "User Profile":
        display_user_profile(profile)
    elif page == "AI Recommendations":
        display_genai_advice(matches_data)


if __name__ == "__main__":
    display_app_page()