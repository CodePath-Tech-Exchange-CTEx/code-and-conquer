# modules.py
import streamlit as st
from typing import Callable, Dict, List, Optional


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
def navigation_bar(full_group_list):
    """
    Renders a simple search bar and returns a filtered list of groups.
    """
    # Simple search input
    search_query = st.text_input(
        "Search", 
        placeholder="Search by title or description...", 
        label_visibility="collapsed"
    )

    # Filtering Logic
    if not search_query:
        return full_group_list

    filtered_list = [
        group for group in full_group_list
        if search_query.lower() in group['group_title'].lower() or 
           search_query.lower() in group['description'].lower()
    ]

    return filtered_list

def study_group_card(group_title, subject, description, date, time, location, members):
    """
    Render a styled study group preview card.

    Args
    
        group_title : str
            The name of the study group.
        subject : str
            Academic subject or category label displayed at the top.
        description : str
            Short summary describing the study group.
        date : str
            Meeting date (formatted string).
        time : str
            Meeting time (formatted string).
        location : str
            Physical or virtual meeting location.
        members : str
            Current and maximum number of members (e.g., "6/12").
    """

    with st.container(border=True):
        
        # Title
        st.subheader(group_title)

        # Description
        st.write(description)

        # Date & Time
        st.write(f"**Date:** {date}")
        st.write(f"**Time:** {time}")

        # Location
        st.markdown(
            f'<div class="location">📍 {location}</div>',
            unsafe_allow_html=True
        )

        # Members
        st.write(f"👥 {members} members")

        # View Details Button
        if st.button("View Details", key=f"btn_{group_title}"):
            st.session_state.selected_group = group_title
            # st.switch_page("pages/group_page.py") 

        st.markdown('</div>', unsafe_allow_html=True)

def display_explore_page(group_list):
    """
    Render the explore page with study group cards arranged in rows.

    Args
        group_list : list of dict
            Each dictionary should have keys:
            'group_title', 'subject', 'description', 'date', 'time', 'location', 'members'
    """
    if not group_list:
        st.info("No groups found")
        return


    num_columns = 3 # Number of cards per row
    for i in range(0, len(group_list), num_columns):
        row_groups = group_list[i:i + num_columns]
        cols = st.columns(len(row_groups)) # Column for each card in this row
        for col, group in zip(cols, row_groups):
            with col:
                study_group_card(
                    group_title=group['group_title'],
                    subject=group['subject'],
                    description=group['description'],
                    date=group['date'],
                    time=group['time'],
                    location=group['location'],
                    members=group['members']
                )
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


# recommendation cards 
def create_match_card(major, title, match_pct, keywords, time, location, members):
    """A template for recommendation card."""
    with st.container():
        # Major and Match Percentage
        header_col, match_col = st.columns([2, 1])
        with header_col:
            st.caption(major.upper())
        with match_col:
            st.markdown(f"**{match_pct}% match**")
            
        # Study Group Name
        st.subheader(title)
        
        # Keywords Row
        if keywords:
            cols = st.columns(len(keywords) + 1)
            for i, word in enumerate(keywords):
                cols[i].markdown(f"`{word}`")
        
        st.write("---") 
        
        # Time, location and member details as icons
        st.markdown(f"🕒 {time}")
        st.markdown(f"📍 {location}")
        st.markdown(f"👥 {members} Members")
        
        # Action Button to join the group
        st.button("Request to Join", key=f"btn_{title.replace(' ', '_')}", use_container_width=True)
        
def display_genai_advice(matches_data):
    """Builds the full AI recommendation page."""

    # recommendation-adjust-preferences-container-streamlit
    with st.container():
        
        col1, col2 = st.columns([4, 1], vertical_alignment="center")
        
        with col1:
            # Container label 
            st.markdown("**AI-Powered Matches**")
            
            # Main heading
            st.markdown("### Curated For You")
            
            # Body description
            st.write("Based on your schedule, major and learning style to find the perfect study partners.")
            
        with col2:
            # Action button on the right side
            st.button("Adjust Preferences", use_container_width=True) 

    # top-matches-and-sort-container-streamlit 
    with st.container():
        
        header_col, sort_col = st.columns([3, 1], vertical_alignment="bottom")
        
        with header_col:
            st.markdown("### Top Matches")
            
        with sort_col:
            # creates the dropdown menu
            sort_option = st.selectbox(
                "Sort by:",
                options=["Match %", "Recently Active", "Shared Classes"],
                index=0 # Sets "Match %" as the default
            )

    cards_per_row = 2
    for i in range(0, len(matches_data), cards_per_row):
        row_groups = matches_data[i:i + cards_per_row]
        cols = st.columns(len(row_groups))
        for col, group in zip(cols, row_groups):
            with col:
                create_match_card(**group)
