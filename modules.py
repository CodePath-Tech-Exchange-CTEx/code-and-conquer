#############################################################################
# modules.py
#
# My Groups UI only. Modern header + card layout for groups.
#
# Functions:
# - display_header() : renders top header with placeholder buttons
# - display_group_card(group, idx): renders a modern card for a group
# - display_my_groups_page(groups): full page composed of header + card grid
# - sample_groups(): example data
#############################################################################

from typing import List, Dict, Optional
import streamlit as st


def _card_css() -> str:
    """Small CSS to give cards a modern look."""
    return """
    <style>
    .mg-header {
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding: 8px 12px;
        border-bottom: 1px solid rgba(0,0,0,0.08);
        margin-bottom: 16px;
    }
    .mg-title {
        font-size:28px;
        font-weight:700;
        margin: 0;
    }
    .mg-subtitle {
        color: #6b7280;
        font-size:14px;
        margin: 0;
    }
    .mg-card {
        background: linear-gradient(180deg, #ffffff, #fbfbfd);
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
        border: 1px solid rgba(15, 23, 42, 0.04);
        margin-bottom: 12px;
        min-height: 160px;
    }
    .mg-card-title { font-size:18px; font-weight:600; margin-bottom:6px; }
    .mg-meta { color:#6b7280; font-size:13px; margin-bottom:6px; }
    .mg-actions { margin-top:10px; display:flex; gap:8px; }
    .mg-new {
        display:flex; align-items:center; justify-content:center;
        height:100%; color:#374151; font-size:18px;
    }
    </style>
    """


def display_header():
    """Renders a modern header with app name and placeholder buttons."""
    st.markdown(_card_css(), unsafe_allow_html=True)
    # header content: left = logo/title, right = placeholder links/buttons
    cols = st.columns([0.7, 0.3])
    with cols[0]:
        st.markdown('<div class="mg-header"><div><p class="mg-title">StudySync</p><p class="mg-subtitle">My Study Groups</p></div></div>', unsafe_allow_html=True)
    with cols[1]:
        # placeholder header buttons (do nothing)
        if st.button("Profile", key="hdr_profile"):
            st.info("Profile clicked (placeholder).")
        if st.button("Recommend", key="hdr_recommend"):
            st.info("Recommend clicked (placeholder).")


def display_group_card(group: Dict, index: int) -> None:
    """
    Render a single modern group card.

    group keys:
      - title (str)
      - schedule (str)
      - mode (str)
      - members (str)
      - is_member (bool)
      - icon (optional str) not required
    """
    title = group.get("title", "Unnamed Group")
    schedule = group.get("schedule", "")
    mode = group.get("mode", "")
    members = group.get("members", "")
    is_member = bool(group.get("is_member", False))

    # Container representing one card with two columns: left meta, right actions
    with st.container():
        st.markdown('<div class="mg-card">', unsafe_allow_html=True)
        cols = st.columns([0.72, 0.28])
        with cols[0]:
            st.markdown(f'<div class="mg-card-title">{title}</div>', unsafe_allow_html=True)
            if schedule:
                st.markdown(f'<div class="mg-meta">🕒 {schedule}</div>', unsafe_allow_html=True)
            if mode:
                st.markdown(f'<div class="mg-meta">📍 {mode}</div>', unsafe_allow_html=True)
            if members:
                st.markdown(f'<div class="mg-meta">👥 {members}</div>', unsafe_allow_html=True)
            # small description placeholder
            st.write("")
        with cols[1]:
            # Actions stacked: group chat + join/leave
            if st.button("Group Chat", key=f"chat_{index}"):
                st.info(f"Open chat for {title} (placeholder).")

            join_key = f"joined_{index}"
            if join_key not in st.session_state:
                st.session_state[join_key] = is_member

            if st.session_state[join_key]:
                if st.button("Leave", key=f"leave_{index}"):
                    st.session_state[join_key] = False
                    st.success(f"You left {title}.")
            else:
                if st.button("Join", key=f"join_{index}"):
                    st.session_state[join_key] = True
                    st.success(f"You joined {title}.")

        st.markdown('</div>', unsafe_allow_html=True)


def display_new_group_card(index: int = 999) -> None:
    """Render a 'New Group' card in the same modern style (placeholder)."""
    with st.container():
        st.markdown('<div class="mg-card">', unsafe_allow_html=True)
        cols = st.columns([0.72, 0.28])
        with cols[0]:
            st.markdown('<div class="mg-card-title">＋ Create / Join New Group</div>', unsafe_allow_html=True)
            st.markdown('<div class="mg-meta">Find or create a new study group</div>', unsafe_allow_html=True)
            st.write("")
        with cols[1]:
            if st.button("New Group", key=f"new_{index}"):
                st.info("New Group flow (placeholder).")
        st.markdown('</div>', unsafe_allow_html=True)


def display_my_groups_page(groups: List[Dict], two_columns: bool = True) -> None:
    """Full page: header + grid of group cards in 1 or 2 columns."""
    display_header()
    st.write("")  # spacing

    if not groups:
        st.info("You have no groups yet. Create or join one!")
        display_new_group_card()
        return

    # Render cards in a 2-column responsive layout
    if two_columns:
        cols = st.columns(2)
        for i, g in enumerate(groups):
            col = cols[i % 2]
            with col:
                display_group_card(g, i)
        # Add a last "new group" card to the grid
        with cols[len(groups) % 2]:
            display_new_group_card(len(groups))
    else:
        for i, g in enumerate(groups):
            display_group_card(g, i)
        display_new_group_card(len(groups))


def sample_groups() -> List[Dict]:
    """Return sample groups matching the mockup."""
    return [
        {
            "title": "Advanced Chemistry",
            "schedule": "Tues & Wed",
            "mode": "In person",
            "members": "8 / 16 Members",
            "is_member": True,
        },
        {
            "title": "Astronomy",
            "schedule": "Mon & Wed",
            "mode": "Online",
            "members": "5 / 8 Members",
            "is_member": False,
        },
        {
            "title": "Biology",
            "schedule": "Saturday",
            "mode": "In person",
            "members": "4 / 8 Members",
            "is_member": False,
        },
    ]
