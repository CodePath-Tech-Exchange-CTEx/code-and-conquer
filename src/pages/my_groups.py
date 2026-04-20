from html import escape
from textwrap import dedent
from typing import Dict, List, Optional
from components import go_to_page
import uuid
from datetime import datetime
from backend.group_membership_handling import create_group

import streamlit as st

def display_my_groups_page(my_groups: List[Dict], current_user_id: str) -> None:
    st.markdown('<div class="page-title">My Study Groups</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Manage your active groups and discover new study partners.</div>',
        unsafe_allow_html=True,
    )

    cards_per_row = 2
    join_card_rendered = False
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

                    st.markdown(
                        dedent(
                            """
                            <div class="glass-card">
                              <div class="my-group-row">
                                <div class="my-group-icon">＋</div>
                                <div class="my-group-content">
                                  <div class="my-group-title">Join Another Group</div>
                                  <div class="muted-text">Find new study partners and add new courses.</div>
                                </div>
                              </div>
                            </div>
                            """
                        ).strip(),
                        unsafe_allow_html=True,
                    )
                    
                    if st.button(
                        "Discover Groups",
                        key="mg_discover",
                        use_container_width=True,
                    ):
                        go_to_page("Explore Groups")

                else:
                    g = item
                    st.markdown(
                        dedent(
                            f"""
                            <div class="glass-card">
                              <div class="my-group-row">
                                <div class="my-group-icon">{escape(str(g.get("icon", "📚")))}</div>
                                <div class="my-group-content">
                                  <div class="my-group-title">{escape(str(g.get("title", "")))}</div>
                                  <div class="muted-text">{escape(str(g.get("days", "")))} · {escape(str(g.get("mode", "")))}</div>
                                  <div class="card-inline-meta">📍 {escape(str(g.get("location", "")))}</div>
                                  <div class="card-inline-meta">👥 {escape(str(g.get("members", "")))}</div>
                                </div>
                              </div>
                            </div>
                            """
                        ).strip(),
                        unsafe_allow_html=True,
                    )
                    st.button(
                        "Group Chat",
                        key=f"mg_chat_{g.get('title', '')}",
                        use_container_width=True,
                    )
    st.write("") 
    st.divider()
    
    spacer_left, center_col, spacer_right = st.columns([1, 2, 1])
    if create_group:
        with center_col:
            # The form will now render perfectly centered, taking up 50% of the screen width
            create_group_dialog(current_user_id)

def create_group_dialog(user_id: str):
    print(f"🚨 DEBUG - The User ID is: '{user_id}'")
    with st.expander("Create a New Group"):
        with st.form("create_group_form"):
            name = st.text_input("Group Name", placeholder="e.g., Intro to Python Study Group")
            subject = st.text_input("Subject", placeholder="e.g., Computer Science")
            description = st.text_area("Description", placeholder="What will this group focus on?")
            
            col1, col2 = st.columns(2)
            with col1:
                mode = st.selectbox("Meeting Mode", ["in-person", "online", "hybrid"])
                capacity = st.number_input("Capacity", min_value=2, max_value=50, value=10)
            with col2:
                visibility = st.selectbox("Visibility", ["public", "private"])
                location_text = st.text_input("Location / Link", placeholder="Room 101 or Zoom Link")
                
            submit = st.form_submit_button("Create Group")
            
            if submit:
                if not name or not subject:
                    st.error("Name and Subject are required!")
                else:
                    # Call the backend function
                    create_group(user_id, name, description, subject, capacity, mode, visibility, location_text)
                    print("DEBUG - Group created successfully!")
                    st.success("Group created successfully!")
                    st.rerun()