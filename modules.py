# modules_mygroups.py
"""
UI helpers for the "My Groups" / "My Study Group" portion of the app.

This module is intentionally small and focused:
- Renders a responsive 2-column grid of "group cards"
- Each card displays an icon, title, schedule, mode, members, and actions
- Includes a simple "Join/Leave" toggle and a "Group Chat" placeholder button
- Safe for unit tests (no side effects beyond Streamlit UI calls)

Usage:
    import streamlit as st
    from modules_mygroups import display_my_groups_page, sample_groups

    display_my_groups_page(sample_groups())
"""

from typing import List, Dict, Optional
import streamlit as st
from PIL import Image, UnidentifiedImageError

# Default mockup image path (optional). If present it'll be shown above the cards.
DEFAULT_MOCKUP_IMAGE_PATH = "/mnt/data/2296caec-640a-4362-8d22-d0dbf854d0f3.png"


def _safe_load_image(path_or_url: Optional[str]):
    """
    Internal helper: try to load a local image file using PIL.
    If the path looks like an http(s) URL or PIL can't open it, return the
    original string so st.image can attempt to render it (or fail gracefully).
    """
    if not path_or_url:
        return None
    s = str(path_or_url)
    if s.lower().startswith(("http://", "https://", "data:")):
        return s
    try:
        return Image.open(s)
    except (FileNotFoundError, UnidentifiedImageError, OSError):
        return s


def display_group_card(group: Dict, card_index: int) -> None:
    """
    Render a single group card in the current Streamlit column.

    group dict keys (all optional except 'title'):
      - title (str): group name (required)
      - schedule (str): e.g., "Tues & Wed"
      - mode (str): e.g., "In person" or "Online"
      - members (str): e.g., "8/16 Members"
      - icon (str): local path or URL to small icon image
      - group_chat_label (str): label to show on chat button (optional)
      - is_member (bool): whether the current user has joined (affects Join button)
      - highlighted (bool): whether to visually emphasize the card

    The function creates a compact visual layout and attaches interactive buttons.
    Buttons are placeholders — they demonstrate interactivity and update the Streamlit
    session state (so repeated presses will toggle 'joined' state locally).
    """
    title = group.get("title", "Unnamed Group")
    schedule = group.get("schedule", "")
    mode = group.get("mode", "")
    members = group.get("members", "")
    icon = _safe_load_image(group.get("icon"))
    chat_label = group.get("group_chat_label", "Group Chat")
    is_member = bool(group.get("is_member", False))
    highlighted = bool(group.get("highlighted", False))

    # Outer card styling: we use a container and columns to approximate a card.
    with st.container():
        # Slight visual emphasis for highlighted groups
        if highlighted:
            st.markdown(f"### 🔵 {title}")
        else:
            st.markdown(f"### {title}")

        # Left: icon (small); Right: metadata + actions
        cols = st.columns([0.28, 0.72])
        with cols[0]:
            if icon:
                # width chosen to keep icons small and consistent
                st.image(icon, width=88)
            else:
                # keep spacing consistent when no icon is provided
                st.write("")

        with cols[1]:
            # Meta lines
            if schedule:
                st.write(f"🕒 {schedule}")
            if mode:
                st.write(f"📍 {mode}")
            if members:
                st.write(f"👥 {members}")

            # Actions row: Group Chat + Join/Leave toggle
            action_cols = st.columns([0.6, 0.4])
            with action_cols[0]:
                # Placeholder chat button; no external effect other than a toast
                if st.button(chat_label, key=f"chat_{card_index}"):
                    st.info(f"Opening chat for '{title}' (placeholder).")

            with action_cols[1]:
                # Track join state in session state to survive re-runs
                join_key = f"joined_{card_index}"
                if join_key not in st.session_state:
                    st.session_state[join_key] = is_member

                if st.session_state[join_key]:
                    if st.button("Leave", key=f"leave_{card_index}"):
                        st.session_state[join_key] = False
                        st.success(f"You left '{title}'.")
                else:
                    if st.button("Join", key=f"join_{card_index}"):
                        st.session_state[join_key] = True
                        st.success(f"You joined '{title}'.")


def display_my_groups_page(
    groups: List[Dict],
    *,
    title: str = "My Study Group",
    subtitle: Optional[str] = "Find and manage your study groups",
    two_columns: bool = True,
    mockup_image_path: Optional[str] = DEFAULT_MOCKUP_IMAGE_PATH,
) -> None:
    """
    Render the full My Groups page.

    Parameters:
      - groups: list of dicts (one per group). See display_group_card for expected keys.
      - title: page title
      - subtitle: small explanatory text under the title
      - two_columns: whether to layout cards in two columns (True) or single column (False)
      - mockup_image_path: optional image to show above the cards (for visual QA)

    Behavior:
      - Shows the mockup image (if path provided and available).
      - Lays out group cards in a 2-column grid (or single column if two_columns=False).
      - Adds a bottom "Join another group" CTA section.
    """
    st.title(title)
    if subtitle:
        st.write(subtitle)

    # Try to show the mockup image; failure is non-fatal.
    if mockup_image_path:
        try:
            mock_img = _safe_load_image(mockup_image_path)
            if mock_img:
                st.image(mock_img, use_column_width=True)
        except Exception:
            # Silently ignore image problems so tests don't fail
            pass

    # Choose grid layout: 2 columns or 1 column
    if two_columns:
        cols = st.columns(2)
        # Place each group into alternating columns
        for i, group in enumerate(groups):
            col = cols[i % 2]
            with col:
                display_group_card(group, card_index=i)
    else:
        # Single-column vertical stack
        for i, group in enumerate(groups):
            display_group_card(group, card_index=i)

    # Footer CTA area: a join/discover action similar to the mockup
    st.markdown("---")
    st.markdown("### Join another group")
    c0, c1 = st.columns([0.2, 0.8])
    with c0:
        st.write("")  # alignment spacer
    with c1:
        if st.button("＋ Join / Discover Groups"):
            st.info("This would open the group discovery flow (placeholder).")


# Small helper that returns sample group data mirroring your mockup
def sample_groups() -> List[Dict]:
    """
    Returns a short list of example groups suitable for local testing or storyboards.
    """
    return [
        {
            "title": "Advanced Chemistry",
            "schedule": "Tues & Wed",
            "mode": "In person",
            "members": "8/16 Members",
            "icon": None,
            "group_chat_label": "Group Chat",
            "is_member": True,
            "highlighted": False,
        },
        {
            "title": "Astronomy",
            "schedule": "Monday & Wed",
            "mode": "Online",
            "members": "5/8 Members",
            "icon": None,
            "group_chat_label": "Group Chat",
            "is_member": False,
            "highlighted": False,
        },
        {
            "title": "Biology",
            "schedule": "Saturday",
            "mode": "In person",
            "members": "4/8 Members",
            "icon": None,
            "group_chat_label": "Group Chat",
            "is_member": False,
            "highlighted": False,
        },
        # space for a "join another group" card if desired
    ]


# If run directly, render a quick demo page in Streamlit when executed as a script.
if __name__ == "__main__":
    # NOTE: Running this file directly will display the streamlit UI inside the streamlit runner.
    # Use `streamlit run modules_mygroups.py` to view the demo page.
    demo_groups = sample_groups()
    display_my_groups_page(demo_groups)
