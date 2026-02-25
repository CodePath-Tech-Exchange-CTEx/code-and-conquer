import streamlit as st
from modules import display_user_profile, navigation_bar, display_explore_page
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to:",
        ["Explore Groups", "User Profile", "Recent Groups", "AI Recommendations"]
    )

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

    mock_study_groups = [
        {"group_title": "Calc II Cram Session", "subject": "Math", "description": "Preparing for midterm", "date": "Oct 12", "time": "4PM", "location": "Library Room 3", "members": "4/6"},
        {"group_title": "Bio 101 Lab Prep", "subject": "Science", "description": "Reviewing cell structures", "date": "Oct 13", "time": "2PM", "location": "Science Hall", "members": "2/4"},
        {"group_title": "Art History Chat", "subject": "Arts", "description": "Renaissance era discussion", "date": "Oct 15", "time": "11AM", "location": "Cafe Blue", "members": "8/10"},
        {"group_title": "Python Basics", "subject": "CS", "description": "Looping and logic", "date": "Oct 16", "time": "6PM", "location": "Zoom", "members": "12/20"},
    ]
    if page == "Explore Groups":
        # Run the page
        filtered_list = navigation_bar(mock_study_groups)
        display_explore_page(filtered_list)

    # elif page == "User Profile":
    #     display_user_profile(profile)
    
    else: 
        st.title("Study Group Finder")


# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
