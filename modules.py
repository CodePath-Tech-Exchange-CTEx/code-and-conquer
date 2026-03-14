# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
import streamlit as st
from typing import Callable, Dict, List, Optional

# CSS style for modules
st.markdown("""
<style>
.study-card {
    border-radius: 18px;
    padding: 20px;
    background-color: #1e1e1e;
    border: 1px solid #333;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.subject-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    background-color: #2d2d2d;
    font-size: 0.8rem;
    margin-bottom: 8px;
}
.location {
    color: #ff4b4b;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True) # Written by Chat GPT


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


    num_columns = 2 # Number of cards per row
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

def _my_groups_styles() -> None:
    st.markdown(
        """
        <style>
          .ss-topbar {
            display:flex;
            align-items:center;
            justify-content:space-between;
            padding: 8px 6px 4px 6px;
          }
          .ss-brand {
            font-weight: 800;
            font-size: 20px;
            letter-spacing: .2px;
          }
          .ss-subtitle {
            color: rgba(255,255,255,0.65);
            font-size: 13px;
            margin-top: -6px;
          }
          .mg-card-icon {
            width: 54px;
            height: 54px;
            border-radius: 14px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size: 28px;
            background: rgba(255,255,255,0.08);
            margin-bottom: 8px;
          }
          .mg-muted {
            color: rgba(255,255,255,0.7);
          }
          .mg-title {
            font-weight: 750;
            margin-top: 6px;
            font-size: 16px;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _top_pills_nav() -> None:
    """
    Top nav pills like your mockup.
    These buttons only set st.session_state.page (they DO NOT touch widget-owned keys).
    """
    left, b1, b2, b3 = st.columns([4, 1.2, 1.6, 1.8], vertical_alignment="center")

    with left:
        st.markdown(
            """
            <div class="ss-topbar">
              <div>
                <div class="ss-brand">StudySync</div>
                <div class="ss-subtitle">My groups</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b1:
        if st.button("Profile", key="pill_profile", use_container_width=True):
            st.session_state.page = "User Profile"
    with b2:
        if st.button("My Group", key="pill_mygroup", use_container_width=True):
            st.session_state.page = "My Groups"
    with b3:
        if st.button("Recommend", key="pill_reco", use_container_width=True):
            st.session_state.page = "AI Recommendations"


def display_my_groups_page(my_groups: List[Dict]) -> None:
    """
    Modern 'My Study Group' page.

    my_groups items expected keys:
      - title (str)
      - icon (str)
      - days (str)
      - mode (str)
      - location (str)
      - members (str)
    """
    _my_groups_styles()
    _top_pills_nav()

    st.markdown("## My Study Group")
    st.write("")

    cards_per_row = 2
    join_card_rendered = False

    # append a join card placeholder at the end
    items = list(my_groups) + ["__JOIN_CARD__"]

    for i in range(0, len(items), cards_per_row):
        row_items = items[i : i + cards_per_row]
        cols = st.columns(len(row_items))

        for col, item in zip(cols, row_items):
            with col:
                if item == "__JOIN_CARD__":
                    if join_card_rendered:
                        continue
                    join_card_rendered = True

                    # Join card
                    with st.container(border=True):
                        st.markdown(
                            '<div class="mg-card-icon">＋</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown("### Join Another")
                        st.markdown("### Group")
                        st.markdown(
                            '<div class="mg-muted">Find new study partners</div>',
                            unsafe_allow_html=True,
                        )

                        # NEW: Add New Course button (safe)
                        if st.button("Add New Course", key="mg_add_course", use_container_width=True):
                            # only set page (do not touch widget-owned keys)
                            st.session_state.page = "Explore Groups"

                        # Keep Discover Groups too
                        if st.button("Discover Groups", key="mg_discover", use_container_width=True):
                            st.session_state.page = "Explore Groups"

                else:
                    g = item
                    with st.container(border=True):
                        st.markdown(
                            f'<div class="mg-card-icon">{g["icon"]}</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"🗓 **{g['days']}**")
                        st.markdown(f"📍 **{g['mode']}**")
                        st.markdown(f"👥 **{g['members']} Members**")
                        st.button(
                            "Group Chat",
                            key=f"mg_chat_{g['title']}",
                            use_container_width=True,
                        )

                        # Render the title inside the card so it doesn't float
                        st.markdown(f'<div class="mg-title">{g["title"]}</div>', unsafe_allow_html=True)