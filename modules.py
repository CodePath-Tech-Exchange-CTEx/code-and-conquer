#############################################################################
# modules.py
#
# Streamlit UI helpers for the app. This single file includes:
# - home-page helpers (display_my_custom_component, display_post, genai advice)
# - workout helpers (display_activity_summary, display_recent_workouts)
# - my-groups helpers (display_group_card, display_my_groups_page, sample_groups)
#
# These implementations are minimal and defensive so imports won't fail.
#############################################################################

from typing import Optional, List, Dict, Any
import streamlit as st

# Try to import PIL to handle local images gracefully; fall back if not installed.
try:
    from PIL import Image, UnidentifiedImageError  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore
    UnidentifiedImageError = Exception  # type: ignore


def _safe_image(path_or_url: Optional[str]) -> Optional[Any]:
    """
    Return a safe object for st.image:
    - If URL (http/https/data), return as-is.
    - If local path and PIL available, open and return PIL image.
    - Otherwise return original string so st.image can still attempt.
    """
    if not path_or_url:
        return None
    s = str(path_or_url)
    if s.lower().startswith(("http://", "https://", "data:")):
        return s
    if Image is not None:
        try:
            return Image.open(s)
        except (FileNotFoundError, UnidentifiedImageError, OSError):
            return s
    return s


# --------------------
# Home page helpers
# --------------------
def display_my_custom_component(value: Optional[str]) -> None:
    """
    Minimal placeholder for the custom component expected by app.py.
    Accepts a single value (e.g., a name string) and displays a greeting.
    """
    with st.container():
        if value:
            st.markdown(f"### Hello, {value} 👋")
            st.caption("Custom component placeholder")
        else:
            st.markdown("### Hello! 👋")
            st.caption("Type your name above to personalize this section.")
        st.divider()


def display_post(
    username: str,
    user_image: Optional[str],
    timestamp: str,
    content: str,
    post_image: Optional[str] = None
) -> None:
    """
    Render a simple social-style post.
    """
    with st.container():
        left, right = st.columns([0.12, 0.88], vertical_alignment="top")
        with left:
            avatar = _safe_image(user_image)
            if avatar:
                try:
                    st.image(avatar, width=56)
                except Exception:
                    st.write("")
            else:
                st.write("")
        with right:
            st.markdown(f"**{username}**  ·  _{timestamp}_")
            st.write(content)
            img = _safe_image(post_image)
            if img:
                try:
                    st.image(img, use_column_width=True)
                except Exception:
                    pass
        st.divider()


def display_genai_advice(timestamp: str, content: str, image: Optional[str] = None) -> None:
    """
    Show GenAI advice card (minimal).
    """
    with st.container():
        st.subheader("GenAI Advice")
        st.caption(timestamp)
        st.write(content)
        img = _safe_image(image)
        if img:
            try:
                st.image(img, use_column_width=True)
            except Exception:
                pass
        st.divider()


# --------------------
# Workouts helpers
# --------------------
def display_activity_summary(workouts_list: List[Dict[str, Any]]) -> None:
    """
    Compact activity summary: totals, metrics, and list of recent workouts.
    """
    st.subheader("Activity Summary")
    if not workouts_list:
        st.info("No workouts to summarize.")
        return

    total_distance = sum((w.get("distance") or 0) for w in workouts_list)
    total_steps = sum((w.get("steps") or 0) for w in workouts_list)
    total_calories = sum((w.get("calories_burned") or 0) for w in workouts_list)
    count = len(workouts_list)
    avg_distance = (total_distance / count) if count else 0
    avg_calories = (total_calories / count) if count else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Workouts", count)
    c2.metric("Total Distance", f"{total_distance:.1f}")
    c3.metric("Total Steps", f"{int(total_steps):,}")
    c4.metric("Calories", f"{int(total_calories)}")

    st.caption(f"Avg distance: {avg_distance:.2f} • Avg calories/workout: {avg_calories:.0f}")
    st.write("Recent:")
    for w in sorted(workouts_list, key=lambda x: x.get("start_timestamp", ""), reverse=True):
        st.write(
            f"- `{w.get('start_timestamp', '')}` — "
            f"{w.get('distance', 0)} dist • {w.get('steps', 0)} steps • {w.get('calories_burned', 0)} cal"
        )


def display_recent_workouts(workouts_list: List[Dict[str, Any]]) -> None:
    """
    Show recent workouts as expanders with details.
    """
    st.subheader("Recent Workouts")
    if not workouts_list:
        st.info("No recent workouts.")
        return

    for w in sorted(workouts_list, key=lambda x: x.get("start_timestamp", ""), reverse=True):
        start = w.get("start_timestamp", "Workout")
        distance = w.get("distance", 0)
        steps = w.get("steps", 0)
        with st.expander(f"{start} — {distance} distance · {steps} steps"):
            st.write(f"**Workout ID:** {w.get('workout_id', '')}")
            st.write(f"Start: {w.get('start_timestamp', '')}")
            if w.get("end_timestamp"):
                st.write(f"End: {w.get('end_timestamp')}")
            st.write(f"Distance: {distance}")
            st.write(f"Steps: {steps}")
            st.write(f"Calories burned: {w.get('calories_burned', 0)}")


# --------------------
# My Groups helpers
# --------------------
DEFAULT_MOCKUP_IMAGE_PATH = "/mnt/data/2296caec-640a-4362-8d22-d0dbf854d0f3.png"


def display_group_card(group: Dict[str, Any], card_index: int) -> None:
    """
    Render one group card. Keys accepted in `group`:
    title, schedule, mode, members, icon, group_chat_label, is_member, highlighted.
    """
    title = group.get("title", "Unnamed Group")
    schedule = group.get("schedule", "")
    mode = group.get("mode", "")
    members = group.get("members", "")
    icon = _safe_image(group.get("icon"))
    chat_label = group.get("group_chat_label", "Group Chat")
    is_member = bool(group.get("is_member", False))
    highlighted = bool(group.get("highlighted", False))

    with st.container():
        if highlighted:
            st.markdown(f"### 🔵 {title}")
        else:
            st.markdown(f"### {title}")

        cols = st.columns([0.28, 0.72])
        with cols[0]:
            if icon:
                try:
                    st.image(icon, width=88)
                except Exception:
                    st.write("")
            else:
                st.write("")
        with cols[1]:
            if schedule:
                st.write(f"🕒 {schedule}")
            if mode:
                st.write(f"📍 {mode}")
            if members:
                st.write(f"👥 {members}")

            action_cols = st.columns([0.6, 0.4])
            with action_cols[0]:
                if st.button(chat_label, key=f"chat_{card_index}"):
                    st.info(f"Opening chat for '{title}' (placeholder).")
            with action_cols[1]:
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
    groups: List[Dict[str, Any]],
    *,
    title: str = "My Study Group",
    subtitle: Optional[str] = "Find and manage your study groups",
    two_columns: bool = True,
    mockup_image_path: Optional[str] = DEFAULT_MOCKUP_IMAGE_PATH,
) -> None:
    """
    Render the My Groups page as a 2-column grid (or single column).
    """
    st.title(title)
    if subtitle:
        st.write(subtitle)

    if mockup_image_path:
        try:
            mock_img = _safe_image(mockup_image_path)
            if mock_img:
                st.image(mock_img, use_column_width=True)
        except Exception:
            pass

    if two_columns:
        cols = st.columns(2)
        for i, group in enumerate(groups):
            col = cols[i % 2]
            with col:
                display_group_card(group, card_index=i)
    else:
        for i, group in enumerate(groups):
            display_group_card(group, card_index=i)

    st.markdown("---")
    st.markdown("### Join another group")
    c0, c1 = st.columns([0.2, 0.8])
    with c0:
        st.write("")
    with c1:
        if st.button("＋ Join / Discover Groups"):
            st.info("This would open the group discovery flow (placeholder).")


def sample_groups() -> List[Dict[str, Any]]:
    """
    Example groups for demos/testing.
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
    ]
