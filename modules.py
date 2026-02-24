# modules.py
import streamlit as st
from typing import Callable, Dict, List, Optional


def group_card(
    group: Dict,
    on_chat: Optional[Callable[[Dict], None]] = None,
    key_prefix: str = "group",
) -> None:
from internals import create_component
import streamlit as st

# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    Render a simple group card using native Streamlit containers.
    group example:
      {"name": "Advanced Chemistry", "icon": "🧪", "days": "Tue & Wed",
       "mode": "In person", "members": "4/6 Members"}
    """
    # card container
    with st.container():
        # small top row: icon and optional badge
        cols = st.columns([0.18, 0.82])
        with cols[0]:
            st.markdown(f"### {group.get('icon','📚')}")
        with cols[1]:
            # keep name bold but small; actual big title below if you want
            st.write(f"**{group.get('name','Unnamed Group')}**")

        # metadata lines
        st.write(f"🕒 {group.get('days','—')}")
        st.write(f"📍 {group.get('mode','—')}")
        st.write(f"👥 {group.get('members','—')}")

        # action button (Group Chat)
        chat_key = f"{key_prefix}_chat_{group.get('name','unknown')}"
        if st.button("Group Chat", key=chat_key):
            if on_chat:
                on_chat(group)

        # small separator so cards don't touch
        st.write("")  


def join_group_card(
    label: str = "Join Another Group",
    on_join: Optional[Callable[[], None]] = None,
    key: str = "join_card",
) -> None:
    """Simple Join card with a button."""
    with st.container():
        st.markdown("### ➕")
        st.write(f"**{label}**")
        if st.button("Browse Groups", key=key):
            if on_join:
                on_join()
        st.write("")
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


def groups_grid(
    groups: List[Dict],
    on_chat: Optional[Callable[[Dict], None]] = None,
    on_join: Optional[Callable[[], None]] = None,
    columns: int = 2,
) -> None:
    """
    Render group tiles in a simple grid (using st.columns).
    The join card is appended as the last tile.
    """
    tiles = groups + [{"_join_tile": True}]
    # iterate in slices of `columns`
    for i in range(0, len(tiles), columns):
        row_tiles = tiles[i : i + columns]
        cols = st.columns(columns)
        for col, tile in zip(cols, row_tiles):
            with col:
                if tile.get("_join_tile"):
                    join_group_card(on_join=on_join, key=f"join_{i}")
                else:
                    group_card(tile, on_chat=on_chat, key_prefix=f"g{i}")


def render_my_groups_page(
    groups: List[Dict],
    on_chat: Optional[Callable[[Dict], None]] = None,
    on_join: Optional[Callable[[], None]] = None,
    columns: int = 2,
) -> None:
    """
    Single-call renderer for the My-Groups page.
    Use this from main.py to render the whole area.
    """
    groups_grid(groups, on_chat=on_chat, on_join=on_join, columns=columns)
