from html import escape
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from backend.data_fetcher import get_explore_page_groups
from backend.group_membership_handling import join_group


import streamlit as st

def project_root() -> Path:
    return Path(__file__).resolve().parent


def go_to_page(page: str) -> None:
    st.session_state.page = page
    st.query_params["page"] = page
    st.rerun()


def apply_styles() -> None:
    css_path = Path(__file__).resolve().parent.parent / "styles.css"
    if not css_path.exists():
        st.warning(f"styles.css not found at {css_path}")
        return

    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_top_nav(selected_page: str = "Explore Groups") -> None:
    labels = ["Explore Groups", "My Groups", "User Profile", "AI Recommendations", "Account Settings"]

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
    st.markdown(dedent(nav_html).strip(), unsafe_allow_html=True)


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


def navigation_bar(full_group_list: List[Dict], user_id) -> List[Dict]:
    st.markdown(
        dedent(
            """
            <div class="section-toolbar">
              <div class="page-title">Explore Groups</div>
              <div class="page-subtitle">
                Discover study sessions that match your schedule and interests.
              </div>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    # Layout: search bar + filter button
    col1, col2 = st.columns([4, 2])

    with col1:
        search_query = st.text_input(
            "Search",
            placeholder="Search by title, subject, or description...",
            label_visibility="collapsed",
            key="explore_search"
        )

    with col2:
        selected_subjects = []
    
        selected_subjects = st.multiselect(
            "Filter by subject",
            options=[
                "Computer Science",
                "Mathematics",
                "Biology",
                "Chemistry",
                "Physics"
            ],
            label_visibility="collapsed",  # <-- THIS fixes alignment
            placeholder="Filter by subject",
            key="subject_filter"
        )

    filter = [f.lower() for f in selected_subjects]

    # Process search
    q = search_query.lower().strip() if search_query else ""

    # Call backend with filters
    return get_explore_page_groups(
        user_id=user_id,
        search=q,
        lon=0,
        lat=0,
        filter=filter 
    )


def study_group_card(
    user_id: str,
    group_id: str,
    group_title: str,
    subject: str,
    description: str,
    date: str,
    time: str,
    location: str,
    capacity: str
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
      <div class="card-inline-meta">👥 Max: {escape(capacity)}</div>
    </div>
    """
    st.markdown(dedent(html).strip(), unsafe_allow_html=True)

    if st.button("Join Group", key=f"btn_{group_id}", use_container_width=True):
        join_group(user_id, group_id)
        st.rerun()

