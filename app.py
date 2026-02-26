# app.py
import streamlit as st
from modules import (
    display_user_profile,
    navigation_bar,
    display_explore_page,
    display_genai_advice,
    display_my_groups_page,
)

PAGES = ["Explore Groups", "My Groups", "User Profile", "AI Recommendations"]


def display_app_page():
    st.set_page_config(page_title="StudySync", page_icon="📚", layout="wide")

    # Initialize page in session_state
    if "page" not in st.session_state:
        st.session_state.page = "Explore Groups"

    st.sidebar.title("Navigation")

    # Make the current page determine the radio index
    current = st.session_state.page if st.session_state.page in PAGES else PAGES[0]

    # Do NOT give the radio a key; use its return value
    choice = st.sidebar.radio(
        "Go to:",
        PAGES,
        index=PAGES.index(current),
    )

    # If the user changed the sidebar, update our page
    if choice != st.session_state.page:
        st.session_state.page = choice

    # ---- Mock data ----
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
        "university": "Stanford University",
        "email": "jane.doe@stanford.edu",
        "about_me": "Passionate about algorithms and AI...",
        "focus_subjects": ["Data Structures", "Machine Learning"],
        "groups_joined": 4,
        "study_hours": 127,
        "day_streak": 12,
        "weekly_availability": [
            {"day": "Mon", "slots": ["9-11 AM", "2-4 PM"]},
            {"day": "Tue", "slots": ["1-3 PM"]},
        ],
    }

    mock_study_groups = [
        {
            "group_title": "Calc II Cram Session",
            "subject": "Math",
            "description": "Preparing for midterm",
            "date": "Oct 12",
            "time": "4PM",
            "location": "Library Room 3",
            "members": "4/6",
        },
        {
            "group_title": "Bio 101 Lab Prep",
            "subject": "Science",
            "description": "Reviewing cell structures",
            "date": "Oct 13",
            "time": "2PM",
            "location": "Science Hall",
            "members": "2/4",
        },
        {
            "group_title": "Art History Chat",
            "subject": "Arts",
            "description": "Renaissance era discussion",
            "date": "Oct 15",
            "time": "11AM",
            "location": "Cafe Blue",
            "members": "8/10",
        },
        {
            "group_title": "Python Basics",
            "subject": "CS",
            "description": "Looping and logic",
            "date": "Oct 16",
            "time": "6PM",
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

    # ---- Routing ----
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
    else:
        st.title("Study Group Finder")


if __name__ == "__main__":
    display_app_page()