#############################################################################
# app.py
#
# Streamlit entrypoint that shows only the My Groups page.
# Run with: streamlit run app.py
#############################################################################

import streamlit as st
from modules import display_my_groups_page, sample_groups


def main():
    st.set_page_config(page_title="My Study Groups", layout="wide")
    groups = sample_groups()
    display_my_groups_page(groups, two_columns=True)


if __name__ == "__main__":
    main()
