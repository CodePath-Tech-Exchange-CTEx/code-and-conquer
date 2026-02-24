# modules.py
import streamlit as st
from typing import Callable, Dict, List, Optional


def group_card(
    group: Dict,
    on_chat: Optional[Callable[[Dict], None]] = None,
    key_prefix: str = "group",
) -> None:
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
