#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_user_profile, display_my_custom_component, display_post, display_genai_advice, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    # st.title('Welcome to SDS!')

    # # An example of displaying a custom component called "my_custom_component"
    # value = st.text_input('Enter your name')
    # display_my_custom_component(value)

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

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
