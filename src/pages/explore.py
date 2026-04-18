from html import escape
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from backend.data_fetcher import get_nearby_groups
from components import _project_root, _go_to_page, navigation_bar, study_group_card


import streamlit as st

def display_explore_page(group_list: List[Dict]) -> None:
    if not group_list:
        st.info("No groups found.")
        return

    cards_per_row = 4

    for i in range(0, len(group_list), cards_per_row):
        row_groups = group_list[i : i + cards_per_row]
        cols = st.columns(cards_per_row)

        for idx, col in enumerate(cols):
            with col:
                if idx < len(row_groups):
                    group = row_groups[idx]
                    study_group_card(
                        group_id=str(group.get("id", "")),
                        group_title=str(group.get("title", "")),
                        subject=str(group.get("subject", "")),
                        description=str(group.get("description", "")),
                        date=str(group.get("schedule", "")[0]["day_of_week"]),
                        time=str(group.get("schedule", "")[0]["start_time"]),
                        location=str(group.get("location_text", "")),
                        capacity=str(group.get("capacity", "")),
                    )
                else:
                    st.empty()