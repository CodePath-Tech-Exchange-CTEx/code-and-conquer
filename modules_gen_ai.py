from html import escape
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import streamlit as st
from data_fetcher_gen_ai import get_final_recommendations


def create_match_card(major, title, match_pct, keywords, time, location, members):
    tags = ""
    if keywords:
        tags = "".join(
            [f"<span class='tag-chip'>{escape(str(word))}</span>" for word in keywords]
        )

    html = f"""
    <div class="glass-card">
      <div class="card-header">
        <div>
          <div class="card-subject">{escape(str(major))}</div>
          <div class="card-title">{escape(str(title))}</div>
        </div>
        <div class="card-meta">
          <div class="meta-pill">{escape(str(match_pct))}% match</div>
        </div>
      </div>
      <div style="margin-top:0.8rem;">{tags}</div>
      <div class="card-inline-meta">🕒 {escape(str(time))}</div>
      <div class="card-inline-meta">📍 {escape(str(location))}</div>
      <div class="card-inline-meta">👥 {escape(str(members))}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    st.button(
        "Request to Join",
        key=f"btn_{str(title).replace(' ', '_')}",
        use_container_width=True,
    )


def display_genai_advice(user_id, user_interests) -> None:
    st.markdown('<div class="page-title">AI Recommendations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Curated matches based on your schedule, interests, and study style.</div>',
        unsafe_allow_html=True,
    )

    top_col, action_col = st.columns([4, 1], vertical_alignment="center")
    with top_col:
        st.markdown("**AI-Powered Matches**")
    with action_col:
        st.button("Adjust Preferences", use_container_width=True, key="adjust_prefs")

    header_col, sort_col = st.columns([3, 1], vertical_alignment="bottom")
    with header_col:
        st.markdown("### Top Matches")
    with sort_col:
        st.selectbox(
            "Sort by:",
            options=["Match %", "Recently Active", "Shared Classes"],
            index=0,
            label_visibility="collapsed",
            key="sort_matches",
        )

    with st.spinner("Finding your perfect study groups..."):
        matches_data = get_final_recommendations(user_id, user_interests)

    if not matches_data:
        st.info("No recommendations found right now.")
        return

    cards_per_row = 2
    for i in range(0, len(matches_data), cards_per_row):
        row_groups = matches_data[i : i + cards_per_row]
        cols = st.columns(len(row_groups))
        for col, group in zip(cols, row_groups):
            with col:
                create_match_card(**group)