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


def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass


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

    