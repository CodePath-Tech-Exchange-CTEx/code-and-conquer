import streamlit as st
from modules import render_my_groups_page
from data_fetcher import (
    get_user_posts,
    get_genai_advice,
    get_user_profile,
    get_user_sensor_data,
    get_user_workouts,
)

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    # simple input (keeps the text input you had)
    value = st.text_input('Enter your name')

    # -------------------------
    # My Groups UI (minimal)
    # -------------------------
    def open_chat(group):
        st.info(f"Would open chat for: {group['name']}")

    def browse_groups():
        st.info("Would navigate to group recommendations / browse screen")

    # sample groups data (replace with real fetches if you want)
    groups = [
        {"name": "Advanced Chemistry", "icon": "🧪", "days": "Tue & Wed", "mode": "In person", "members": "4/6 Members"},
        {"name": "Astronomy", "icon": "🔭", "days": "Mon & Wed", "mode": "Online", "members": "5/8 Members"},
        {"name": "Biology", "icon": "🌿", "days": "Saturday", "mode": "In person", "members": "—"},
    ]

    # render the My-Groups area from modules.py
    render_my_groups_page(groups, on_chat=open_chat, on_join=browse_groups, columns=2)


# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
