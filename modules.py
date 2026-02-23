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


def display_post(group_title, subject, description, date, time, location, members):
    """Write a good docstring here."""
    pass


def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass


def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
