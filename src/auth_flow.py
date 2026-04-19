#############################################################################
# auth.py
#
# Authentication and onboarding flow for StudySync.
# Uses Supabase for real sign in, sign up, and password reset.
#
# Flow:
#   Sign In  ←→  Step 1 (Create Account entry)
#                    ↓
#              Step 2 (Account details)
#                    ↓
#              Step 3 (Academic Profile)
#                    ↓
#              Step 4 (Curate Your Curriculum)
#                    ↓
#              Step 5 (Study Schedule)
#                    ↓
#              Step 6 (Final Touches)
#                    ↓
#               Main App
#
#   Sign In → Forgot Password → Restore Access
#############################################################################

import os
import streamlit as st
from supabase import create_client, Client

# ── Supabase client ───────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", ""))
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .streamlit/secrets.toml")
    return create_client(url, key)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _go_to_auth(screen: str) -> None:
    """Navigate to a different auth screen."""
    st.session_state.auth_screen = screen
    st.rerun()


def _progress_bar(current_step: int, total_steps: int = 6) -> None:
    """Render a step progress bar."""
    pct = int((current_step / total_steps) * 100)
    st.markdown(
        f"""
        <div style="margin-bottom: 8px;">
            <div style="display:flex; justify-content:space-between;
                        font-size:0.75rem; color:#888; margin-bottom:4px;">
                <span>Step {current_step} of {total_steps}</span>
                <span>{pct}% complete</span>
            </div>
            <div style="background:#e8e8e8; border-radius:99px; height:6px;">
                <div style="background:#f5c842; width:{pct}%;
                            height:6px; border-radius:99px;
                            transition: width 0.4s ease;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _card_open() -> None:
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)


def _card_close() -> None:
    st.markdown('</div>', unsafe_allow_html=True)


def _auth_styles() -> None:
    st.markdown(
        """
        <style>
        /* ── Auth page wrapper ── */
        .auth-wrap {
            display: flex;
            justify-content: center;
            padding: 0px 16px;
        }
        /* ── Card ── */
        .auth-card {
            background: #ffffff;
            border-radius: 24px;
            padding: 20px 32px;
            max-width: 480px;
            width: 100%;
            box-shadow: 0 4px 32px rgba(0,0,0,0.08);
            margin: 0 auto;
        }
        /* ── Brand ── */
        .auth-brand {
            text-align: center;
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
            color: #1a1a1a;
        }
        .auth-brand-icon {
            font-size: 2rem;
            text-align: center;
            margin-bottom: 4px;
        }
        /* ── Headings ── */
        .auth-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1a1a1a;
            margin: 8px 0 4px 0;
            text-align: center;
        }
        .auth-subtitle {
            font-size: 0.88rem;
            color: #666;
            text-align: center;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        /* ── Social buttons ── */
        .social-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            padding: 12px;
            border: 1.5px solid #e0e0e0;
            border-radius: 12px;
            background: #fff;
            font-size: 0.92rem;
            font-weight: 500;
            color: #1a1a1a;
            cursor: pointer;
            margin-bottom: 10px;
            transition: background 0.15s, border-color 0.15s;
        }
        .social-btn:hover { background: #f9f9f9; border-color: #bbb; }
        /* ── Divider ── */
        .auth-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 16px 0;
            color: #aaa;
            font-size: 0.8rem;
        }
        .auth-divider::before,
        .auth-divider::after {
            content: "";
            flex: 1;
            height: 1px;
            background: #e8e8e8;
        }
        /* ── Footer links ── */
        .auth-footer {
            text-align: center;
            font-size: 0.82rem;
            color: #888;
            margin-top: 20px;
        }
        .auth-link {
            color: #c9a800;
            font-weight: 600;
            cursor: pointer;
            text-decoration: underline;
        }
        /* ── Tag chips ── */
        .tag-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 16px; }
        .tag-chip-auth {
            padding: 6px 14px;
            border-radius: 20px;
            border: 1.5px solid #e0e0e0;
            font-size: 0.82rem;
            cursor: pointer;
            background: #fff;
            color: #444;
            transition: all 0.15s;
        }
        .tag-chip-auth.selected {
            background: #f5c842;
            border-color: #f5c842;
            color: #1a1a1a;
            font-weight: 600;
        }
        /* ── Info box ── */
        .auth-info-box {
            background: #f8f8f8;
            border-radius: 10px;
            padding: 12px 14px;
            font-size: 0.82rem;
            color: #555;
            margin: 12px 0;
            display: flex;
            gap: 8px;
            align-items: flex-start;
        }
        /* Remove Streamlit's default page top padding */
        section.main > div.block-container {
            padding-top: 1rem !important;
        }
        /* Forgot password styled as link, no box */
        div.forgot-link button {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            color: #c9a800 !important;
            text-decoration: underline !important;
            padding: 0 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            margin-top: 2px !important;
        }
        div.forgot-link button:hover {
            color: #a88200 !important;
            background: none !important;
        }
        /* Remove Streamlit default top padding */
        section.main > div.block-container {
            padding-top: 0.5rem !important;
        }
        /* Hide "Press Enter to apply" hint on text inputs */
        [data-testid="InputInstructions"] { display: none !important; }
        /* Forgot password button styled as a link using adjacent sibling */
        div.forgot-link ~ div[data-testid="stButton"] button,
        div.forgot-link + div[data-testid="stButton"] button {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            color: #c9a800 !important;
            text-decoration: underline !important;
            padding: 0 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            min-height: unset !important;
            height: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Screen: Sign In ───────────────────────────────────────────────────────────

def render_sign_in() -> None:
    _auth_styles()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="auth-brand-icon">📚</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-brand">StudySync</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">Welcome Back</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Access your curated academic archive and collaborative study.</div>',
            unsafe_allow_html=True,
        )

        username = st.text_input("Email", placeholder="scholar@university.edu", key="si_username")

        pw_col, forgot_col = st.columns([3, 2])
        with pw_col:
            st.markdown("**Password**")
        with forgot_col:
            if st.button('Forgot Password?', key='si_forgot', use_container_width=True):
                _go_to_auth('restore_access')
        password = st.text_input("Password", type="password", label_visibility="collapsed", key="si_password")
        if st.button("Sign In →", use_container_width=True, key="si_submit", type="primary"):
            if not username or not password:
                st.error("Please enter your username and password.")
            else:
                try:
                    supabase = get_supabase()
                    response = supabase.auth.sign_in_with_password({
                        "email": username,
                        "password": password,
                    })
                    user = response.user
                    st.session_state["authenticated"] = True
                    st.session_state["current_user_id"] = user.id
                    st.session_state["user_email"] = user.email
                    st.rerun()
                except Exception as e:
                    st.error("Invalid email or password. Please try again.")

        st.markdown(
            '<div class="auth-footer">New to the Archive?</div>',
            unsafe_allow_html=True,
        )
        if st.button("Create Account", use_container_width=True, key="si_create"):
            _go_to_auth("step_1")


# ── Screen: Step 1 — Create Account Entry ────────────────────────────────────

def render_step_1() -> None:
    _auth_styles()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        _progress_bar(1)
        st.markdown('<div class="auth-brand-icon">📚</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-brand">StudySync</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">Create your StudySync Account</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Find study partners and groups that match your courses and goals.</div>',
            unsafe_allow_html=True,
        )

        if st.button("🇬 Continue with Google", use_container_width=True, key="s1_google"):
            st.info("Google sign-up coming soon.")

        if st.button("🍎 Continue with Apple", use_container_width=True, key="s1_apple"):
            st.info("Apple sign-up coming soon.")

        if st.button("✉ Continue with Email", use_container_width=True, key="s1_email"):
            _go_to_auth("step_2")

        st.markdown(
            '<div class="auth-footer">Already have an account?</div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign In", use_container_width=True, key="s1_signin"):
            _go_to_auth("sign_in")


# ── Screen: Step 2 — Account Details ─────────────────────────────────────────

def render_step_2() -> None:
    _auth_styles()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        _progress_bar(2)
        st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Join the curated community of scholars.</div>',
            unsafe_allow_html=True,
        )

        full_name = st.text_input("Full Name", placeholder="John Doe", key="s2_name")

        email = st.text_input("School Email Address", placeholder="scholar@university.edu", key="s2_email")

        pw_col, cpw_col = st.columns(2)
        with pw_col:
            password = st.text_input("Password", type="password", key="s2_password")
        with cpw_col:
            confirm  = st.text_input("Confirm Password", type="password", key="s2_confirm")

        tos = st.checkbox("I agree to Terms of Service and Privacy Policy", key="s2_tos")

        if st.button("Continue →", use_container_width=True, key="s2_submit", type="primary"):
            if not full_name or not email or not password or not confirm:
                st.error("Please fill in all fields.")
            elif not email.endswith(".edu"):
                st.error("Please use a valid school email address ending in .edu")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif not tos:
                st.error("You must agree to the Terms of Service to continue.")
            else:
                st.session_state.onboarding = st.session_state.get("onboarding", {})
                st.session_state.onboarding.update({
                    "full_name": full_name,
                    "email": email,
                    "password": password,
                })
                _go_to_auth("step_3")

        if st.button("← Back", use_container_width=False, key="s2_back"):
            _go_to_auth("step_1")


# ── Screen: Step 3 — Academic Profile ────────────────────────────────────────

def render_step_3() -> None:
    _auth_styles()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        _progress_bar(3)
        st.markdown('<div class="auth-title">Academic Profile</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Tell us about your scholarly environment.</div>',
            unsafe_allow_html=True,
        )

        university = st.text_input("University or College Name", placeholder="🎓 e.g Oxford University", key="s3_uni")
        location   = st.text_input("Campus Location", placeholder="📍 City, Country", key="s3_location")

        major_col, year_col = st.columns(2)
        with major_col:
            major = st.text_input("Major or Program", placeholder="e.g Philosophy", key="s3_major")
        with year_col:
            year = st.selectbox(
                "Year of Study",
                ["Freshman", "Sophomore", "Junior", "Senior", "Graduate", "PhD"],
                key="s3_year",
            )

        grad_year = st.text_input("Graduation Year", placeholder="2027", key="s3_grad")

        if st.button("Continue →", use_container_width=True, key="s3_submit", type="primary"):
            if not university or not major or not grad_year:
                st.error("Please fill in all required fields.")
            else:
                st.session_state.onboarding = st.session_state.get("onboarding", {})
                st.session_state.onboarding.update({
                    "university": university,
                    "location": location,
                    "major": major,
                    "year": year,
                    "grad_year": grad_year,
                })
                _go_to_auth("step_4")

        if st.button("← Back to Step 2", use_container_width=False, key="s3_back"):
            _go_to_auth("step_2")


# ── Screen: Step 4 — Curate Your Curriculum ──────────────────────────────────

INTEREST_TAGS = [
    "Mathematics", "Computer Science", "Biology", "Chemistry",
    "Business", "Writing", "Exam Prep", "Physics", "History",
    "Engineering", "Art", "Psychology",
]

STUDY_GOALS = [
    "Improve GPA",
    "Pass Upcoming Exams",
    "Find Study Partners",
    "Prepare for Technical Interviews",
    "Build a Study Habit",
    "Explore a New Subject",
    "Stay Accountable with Others",
]

def render_step_4() -> None:
    _auth_styles()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        _progress_bar(4)
        st.markdown('<div class="auth-title">Curate Your Curriculum</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Tell us about your academic focus to personalize your study sessions.</div>',
            unsafe_allow_html=True,
        )

        courses = st.text_input(
            "Current Courses or Subjects",
            placeholder="e.g Organic Chemistry II...",
            key="s4_courses",
        )

        st.markdown("**Interest Tags**")
        st.caption("Select all that apply.")
        selected_tags = st.multiselect(
            "Interest Tags",
            INTEREST_TAGS,
            label_visibility="collapsed",
            key="s4_tags",
        )

        if st.button("Continue →", use_container_width=True, key="s4_submit", type="primary"):
            if not courses:
                st.error("Please enter at least one course or subject.")
            elif not selected_tags:
                st.error("Please select at least one interest tag.")
            else:
                st.session_state.onboarding = st.session_state.get("onboarding", {})
                st.session_state.onboarding.update({
                    "courses": courses,
                    "interest_tags": selected_tags,
                })
                _go_to_auth("step_5")

        if st.button("← Back", use_container_width=False, key="s4_back"):
            _go_to_auth("step_3")


# ── Screen: Step 5 — Weekly Availability ─────────────────────────────────────
# This step was missing from the mockups but is essential — the weekly
# availability data is displayed on the User Profile page and used by
# the AI recommendation engine to match study groups by schedule.

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TIME_SLOTS = [
    "8-10 AM", "10-12 PM", "12-2 PM", "2-4 PM",
    "4-6 PM", "6-8 PM", "8-10 PM",
]

def render_step_5() -> None:
    _auth_styles()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        _progress_bar(5)
        st.markdown('<div class="auth-title">Your Study Schedule</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Let us know when you\'re free so we can match you with groups that fit your schedule.</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Select your available days and times**")

        availability = {}
        for day in DAYS:
            with st.expander(day):
                slots = st.multiselect(
                    f"Available times on {day}",
                    TIME_SLOTS,
                    label_visibility="collapsed",
                    key=f"s5_{day}",
                )
                if slots:
                    availability[day] = slots

        if st.button("Continue →", use_container_width=True, key="s5_submit", type="primary"):
            if not availability:
                st.error("Please select at least one available time slot.")
            else:
                # Format into the shape display_user_profile() expects
                weekly_availability = [
                    {"day": day, "slots": slots}
                    for day, slots in availability.items()
                ]
                st.session_state.onboarding = st.session_state.get("onboarding", {})
                st.session_state.onboarding.update({
                    "weekly_availability": weekly_availability,
                })
                _go_to_auth("step_6")

        if st.button("← Back", use_container_width=False, key="s5_back"):
            _go_to_auth("step_4")


# ── Screen: Step 6 — Final Touches ───────────────────────────────────────────

HELP_OPTIONS = [
    "Staying Accountable",
    "Preparing for Exams",
    "Finish Assignments",
    "Weekly Group Sync",
    "Find Classmates",
]

def render_step_6() -> None:
    _auth_styles()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        _progress_bar(6)
        st.markdown('<div class="auth-title">Final Touches</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Help us create the perfect academic experience for you.</div>',
            unsafe_allow_html=True,
        )

        study_goal = st.selectbox(
            "What is your main study goal?",
            STUDY_GOALS,
            key="s6_goal",
        )

        st.markdown("**Profile Photo**")
        photo = st.file_uploader(
            "Upload Photo",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="s6_photo",
        )
        if photo:
            st.image(photo, width=80)

        if st.button("Create Account", use_container_width=True, key="s6_submit", type="primary"):
            onboarding = st.session_state.get("onboarding", {})
            onboarding.update({"study_goal": study_goal})
            try:
                supabase = get_supabase()
                email = onboarding.get("email", "")
                password = onboarding.get("password", "")
                full_name = onboarding.get("full_name", "")

                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": full_name,
                            "university": onboarding.get("university", ""),
                            "major": onboarding.get("major", ""),
                            "year": onboarding.get("year", ""),
                            "study_goal": study_goal,
                        }
                    }
                })
                user = response.user
                st.session_state["authenticated"] = True
                st.session_state["current_user_id"] = user.id
                st.session_state["user_email"] = user.email
                st.session_state["onboarding"] = onboarding
                st.success("Account created! Welcome to StudySync 🎉")
                st.rerun()
            except Exception as e:
                st.error(f"Could not create account: {e}")

        if st.button("← Back", use_container_width=False, key="s6_back"):
            _go_to_auth("step_5")


# ── Screen: Restore Access ────────────────────────────────────────────────────

def render_restore_access() -> None:
    _auth_styles()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            '<div style="text-align:center; font-size:2.5rem; margin-bottom:8px;">🔒</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="auth-title">Restore Access</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Enter your email to receive a password reset link for your account.</div>',
            unsafe_allow_html=True,
        )

        email = st.text_input(
            "Email Address",
            placeholder="placeholder@studysync.edu",
            key="ra_email",
        )

        st.markdown(
            '<div class="auth-info-box">ℹ️ If an account exists for this email, '
            'you will receive a reset link shortly.</div>',
            unsafe_allow_html=True,
        )

        if st.button("Send Request Link →", use_container_width=True, key="ra_submit", type="primary"):
            if not email:
                st.error("Please enter your email address.")
            else:
                try:
                    supabase = get_supabase()
                    supabase.auth.reset_password_email(email)
                    st.success(f"Reset link sent to {email}. Check your inbox.")
                except Exception as e:
                    st.error(f"Could not send reset email: {e}")

        if st.button("← Back to Sign In", use_container_width=True, key="ra_back"):
            _go_to_auth("sign_in")


# ── Main entry point ──────────────────────────────────────────────────────────

def render_auth_flow() -> None:
    """
    Main entry point. Call this from app.py before rendering the main app.
    Checks both session_state and query_params for auth status so it survives
    href-based navigation reruns.

    Usage in app.py:
        from auth import render_auth_flow
        if not st.session_state.get("authenticated"):
            render_auth_flow()
            st.stop()
    """
    screen = st.session_state.get("auth_screen", "sign_in")

    screens = {
        "sign_in":        render_sign_in,
        "step_1":         render_step_1,
        "step_2":         render_step_2,
        "step_3":         render_step_3,
        "step_4":         render_step_4,
        "step_5":         render_step_5,
        "step_6":         render_step_6,
        "restore_access": render_restore_access,
    }

    renderer = screens.get(screen, render_sign_in)
    renderer()