#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_user_profile
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    # st.title('Welcome to SDS!')

    # # An example of displaying a custom component called "my_custom_component"
    # value = st.text_input('Enter your name')
    # display_my_custom_component(value)

    matches_data = [
    {
        "major": "Computer Science",
        "title": "GenAI & Systems Design",
        "match_pct": 98,
        "keywords": ["Algorithms", "Python", "GenAI"],
        "time": "Tuesdays 5:00 PM",
        "location": "Fisk Library",
        "members": "3/5"
    },
    {
        "major": "Computer Science",
        "title": "iOS Dev Hackers",
        "match_pct": 92,
        "keywords": ["Swift", "Hackathons", "App Dev"],
        "time": "Fridays 3:00 PM",
        "location": "Nashville Tech Hub",
        "members": "4/6"
    },
    {
        "major": "Computer Science",
        "title": "Technical Interview Prep",
        "match_pct": 85,
        "keywords": ["Data Structures", "Mock Interviews"],
        "time": "Wednesdays 6:00 PM",
        "location": "Remote / Discord",
        "members": "2/4"
    }
]

    st.write("DEBUG: Before calling display_genai_advice")
    display_genai_advice(matches_data)
    st.write("DEBUG: After calling display_genai_advice")

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()