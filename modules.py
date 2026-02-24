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

def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass


def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass