#############################################################################
# modules.py
#
# Shared UI modules for the StudySync app.
#############################################################################

from html import escape
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import streamlit as st


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _go_to_page(page: str) -> None:
    st.session_state.page = page
    st.query_params["page"] = page
    st.rerun()


def apply_styles() -> None:
    css_path = Path(__file__).resolve().parent / "styles.css"
    if not css_path.exists():
        st.warning(f"styles.css not found at {css_path}")
        return

    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_top_nav(selected_page: str = "Explore Groups") -> None:
    labels = ["Explore Groups", "My Groups", "User Profile", "AI Recommendations"]

    def pill(label: str) -> str:
        active = "active" if label == selected_page else ""
        href = f"?page={quote_plus(label)}"
        return (
            f'<a class="nav-pill {active}" href="{href}" target="_self">'
            f"{escape(label)}"
            f"</a>"
        )

    links = "".join([pill(label) for label in labels])

    nav_html = f"""
    <div class="top-nav-wrap">
      <div class="top-nav-shell">
        <div class="brand-pill">StudySync</div>
        <div class="top-nav-links">
          {links}
        </div>
        <div class="utility-pill">Campus Focus</div>
      </div>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)


def create_component_from_template(data: Dict[str, str], html_file_name: str) -> None:
    import streamlit.components.v1 as components

    base = _project_root()
    html_path = base / "custom_components" / f"{html_file_name}.html"

    if not html_path.exists():
        st.warning(f"Custom component HTML not found: {html_path}")
        return

    html = html_path.read_text(encoding="utf-8")
    for k, v in data.items():
        html = html.replace(f"{{{{{k}}}}}", str(v))
    components.html(html, height=220, scrolling=False)


def display_my_custom_component(value: str) -> None:
    data = {"NAME": value}
    create_component_from_template(data, "my_custom_component")


def navigation_bar(full_group_list: List[Dict]) -> List[Dict]:
    st.markdown(
        """
        <div class="section-toolbar">
          <div class="page-title">Explore Groups</div>
          <div class="page-subtitle">
            Discover study sessions that match your schedule and interests.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    search_query = st.text_input(
        "Search",
        placeholder="Search by title, subject, or description...",
        label_visibility="collapsed",
        key="explore_search",
    )

    if not search_query:
        return full_group_list

    q = search_query.lower().strip()
    return [
        group
        for group in full_group_list
        if q in str(group.get("group_title", "")).lower()
        or q in str(group.get("description", "")).lower()
        or q in str(group.get("subject", "")).lower()
    ]


def study_group_card(
    group_title: str,
    subject: str,
    description: str,
    date: str,
    time: str,
    location: str,
    members: str,
) -> None:
    html = f"""
    <div class="glass-card">
      <div class="card-header">
        <div>
          <div class="card-title">{escape(group_title)}</div>
          <div class="card-subject">{escape(subject)}</div>
        </div>
        <div class="card-meta">
          <div class="meta-pill">{escape(date)} · {escape(time)}</div>
        </div>
      </div>
      <div class="card-description">{escape(description)}</div>
      <div class="card-inline-meta">📍 {escape(location)}</div>
      <div class="card-inline-meta">👥 {escape(members)}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    if st.button("View Details", key=f"btn_{group_title}", use_container_width=True):
        st.session_state.selected_group = group_title


def display_explore_page(group_list: List[Dict]) -> None:
    if not group_list:
        st.info("No groups found.")
        return


    num_columns = 2 # Number of cards per row
    for i in range(0, len(group_list), num_columns):
        row_groups = group_list[i : i + num_columns]
        cols = st.columns(len(row_groups))
        for col, group in zip(cols, row_groups):
            with col:
                study_group_card(
                    group_title=str(group.get("group_title", "")),
                    subject=str(group.get("subject", "")),
                    description=str(group.get("description", "")),
                    date=str(group.get("date", "")),
                    time=str(group.get("time", "")),
                    location=str(group.get("location", "")),
                    members=str(group.get("members", "")),
                )


def _render_stat_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="stat-card">
          <div class="stat-label">{escape(str(label))}</div>
          <div class="stat-value">{escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_user_profile(profile: Optional[Dict]) -> None:
    if not profile:
        st.warning("No profile data available.")
        return

    st.markdown('<div class="page-title">User Profile</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Your academic profile, focus subjects, and study availability.</div>',
        unsafe_allow_html=True,
    )

    initials = (
        str(profile.get("first_name", ""))[:1] + str(profile.get("last_name", ""))[:1]
    ).upper() or "U"

    col_avatar, col_info, col_btns = st.columns([1.2, 5, 2])

    with col_avatar:
        st.markdown(
            f"""
            <div class="profile-avatar-card">
              <div class="profile-avatar-initials">{escape(initials)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_info:
        full_name = (
            f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
        )
        institution = str(profile.get("institution", profile.get("university", "")))
        email = str(profile.get("email", ""))
        major = str(profile.get("major", ""))
        year = str(profile.get("year", profile.get("education_level", "")))

        st.markdown(
            f'<div class="profile-name">{escape(full_name)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="profile-subline">{escape(major)} · {escape(year)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="profile-meta-line">
              <span>🏛 {escape(institution)}</span>
              <span>✉ <a class="inline-link" href="mailto:{escape(email)}">{escape(email)}</a></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_btns:
        st.button("Edit Profile", use_container_width=True, key="profile_edit")
        st.button("Share Profile", use_container_width=True, key="profile_share")

    st.divider()

    st.markdown("**ABOUT ME**")
    st.write(profile.get("about_me", ""))

    st.markdown("**FOCUS SUBJECTS**")
    subjects = profile.get("focus_subjects", [])
    if subjects:
        chips = "".join(
            [f"<span class='tag-chip'>{escape(str(s))}</span>" for s in subjects]
        )
        st.markdown(chips, unsafe_allow_html=True)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        _render_stat_card("Groups Joined", profile.get("groups_joined", 0))
    with col2:
        _render_stat_card("Study Hours", profile.get("study_hours", 0))
    with col3:
        _render_stat_card("Day Streak", profile.get("day_streak", 0))

    st.divider()

    header_col, button_col = st.columns([4, 1])
    with header_col:
        st.markdown("**Weekly Availability**")
    with button_col:
        st.button("Update Schedule", use_container_width=True, key="update_schedule")

    availability = profile.get("weekly_availability", [])
    if availability:
        cols = st.columns(len(availability))
        for col, day_data in zip(cols, availability):
            slots = day_data.get("slots", [])
            slot_html = "".join(
                [f"<div class='availability-slot'>{escape(str(slot))}</div>" for slot in slots]
            )
            with col:
                st.markdown(
                    f"""
                    <div class="availability-card">
                      <div class="availability-day">{escape(str(day_data.get('day', '')))}</div>
                      {slot_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def display_recent_workouts(workouts_list):
    pass


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


def display_genai_advice(matches_data: List[Dict]) -> None:
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

    cards_per_row = 2
    for i in range(0, len(matches_data), cards_per_row):
        row_groups = matches_data[i : i + cards_per_row]
        cols = st.columns(len(row_groups))
        for col, group in zip(cols, row_groups):
            with col:
                create_match_card(**group)


def display_my_groups_page(my_groups: List[Dict]) -> None:
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
                        """
                        <div class="glass-card">
                          <div class="my-group-row">
                            <div class="my-group-icon">＋</div>
                            <div>
                              <div class="my-group-title">Join Another Group</div>
                              <div class="muted-text">Find new study partners and add new courses.</div>
                            </div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "Add New Course",
                        key="mg_add_course",
                        use_container_width=True,
                    ):
                        _go_to_page("Explore Groups")

                    if st.button(
                        "Discover Groups",
                        key="mg_discover",
                        use_container_width=True,
                    ):
                        _go_to_page("Explore Groups")

                else:
                    g = item
                    st.markdown(
                        f"""
                        <div class="glass-card">
                          <div class="my-group-row">
                            <div class="my-group-icon">{escape(str(g.get("icon", "📚")))}</div>
                            <div style="flex:1;">
                              <div class="my-group-title">{escape(str(g.get("title", "")))}</div>
                              <div class="muted-text">{escape(str(g.get("days", "")))} · {escape(str(g.get("mode", "")))}</div>
                              <div class="card-inline-meta">📍 {escape(str(g.get("location", "")))}</div>
                              <div class="card-inline-meta">👥 {escape(str(g.get("members", "")))}</div>
                            </div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.button(
                        "Group Chat",
                        key=f"mg_chat_{g.get('title', '')}",
                        use_container_width=True,
                    )