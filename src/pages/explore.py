from pathlib import Path
from typing import Dict, List, Optional
from backend.data_fetcher import get_explore_page_groups, get_final_recommendations, get_user_identity_data
from components import study_group_card

import streamlit as st


def display_explore_page(user_id: str, group_list: List[Dict]) -> None:
    if not group_list:
        st.info("No groups found.")
        return

    print(group_list)
    cards_per_row = 3

    for i in range(0, len(group_list), cards_per_row):
        row_groups = group_list[i : i + cards_per_row]
        cols = st.columns(cards_per_row)

        for idx, col in enumerate(cols):
            with col:
                if idx < len(row_groups):
                    group = row_groups[idx]

                    schedule = group.get("schedule") or [] 
                    print(schedule)
                    
                    # If the list has items, get the first one. Otherwise, default to "TBD"
                    date_val = str(schedule[0].get("day_of_week", "TBD")) if schedule else "TBD"
                    time_val = str(schedule[0].get("start_time", "TBD")) if schedule else "TBD"

                    study_group_card(
                        user_id=user_id,
                        group_id=str(group.get("id", "")),
                        group_title=str(group.get("name", "")),
                        subject=str(group.get("subject", "")),
                        description=str(group.get("description", "")),
                        date=date_val,
                        time=time_val,
                        location=str(group.get("location_text", "")),
                        capacity=str(group.get("capacity", "")),
                    )
                else:
                    st.empty()