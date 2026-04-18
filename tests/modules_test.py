#############################################################################
# modules_test.py
#
# Unit tests for modules.py
#
# This file currently contains tests for:
#   - My Groups module only (teammate)
#   - User Profile module (Chris)
#
# Teammates can add their own test classes below for other modules.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest
import streamlit as st


#############################################################################
# WRAPPER FUNCTIONS FOR STREAMLIT APP TESTING
#############################################################################

def render_my_groups_page():
    from modules import display_my_groups_page

    sample_my_groups = [
        {
            "title": "GenAI & Systems Design",
            "icon": "💻",
            "days": "Tue 17:00-19:00",
            "mode": "hybrid",
            "location": "Fisk Library, Room 12",
            "members": "2/8",
        },
        {
            "title": "Calc II Cram",
            "icon": "📐",
            "days": "Thu 16:00-18:00",
            "mode": "in-person",
            "location": "Math Building, Room 3",
            "members": "1/6",
        },
    ]

    display_my_groups_page(sample_my_groups)


def render_empty_my_groups_page():
    from modules import display_my_groups_page
    display_my_groups_page([])


def render_user_profile_page():
    from modules import display_user_profile

    sample_profile = {
        "first_name": "Jane",
        "last_name": "Doe",
        "major": "Computer Science",
        "year": "Junior Year",
        "institution": "Stanford University",
        "email": "jane.doe@stanford.edu",
        "about_me": "Passionate about algorithms and AI.",
        "focus_subjects": ["Data Structures", "Machine Learning"],
        "groups_joined": 4,
        "study_hours": 127,
        "day_streak": 12,
        "weekly_availability": [
            {"day": "Mon", "slots": ["9-11 AM", "2-4 PM"]},
            {"day": "Tue", "slots": ["1-3 PM"]},
        ],
    }

    display_user_profile(sample_profile)


def render_empty_user_profile_page():
    from modules import display_user_profile
    display_user_profile(None)


#############################################################################
# MY GROUPS MODULE TESTS
#############################################################################

@patch("data_fetcher.get_my_groups")
class TestMyGroupsPage(unittest.TestCase):

    def test_my_groups_page_renders_without_exception(self, _mock):
        at = AppTest.from_function(render_my_groups_page).run()
        self.assertFalse(at.exception)

    def test_my_groups_title_and_subtitle_render(self, _mock):
        at = AppTest.from_function(render_my_groups_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("My Study Groups", all_markdown)
        self.assertIn("Manage your active groups", all_markdown)

    def test_group_titles_render(self, _mock):
        at = AppTest.from_function(render_my_groups_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("GenAI &amp; Systems Design", all_markdown)
        self.assertIn("Calc II Cram", all_markdown)

    def test_group_locations_and_members_render(self, _mock):
        at = AppTest.from_function(render_my_groups_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("Fisk Library, Room 12", all_markdown)
        self.assertIn("Math Building, Room 3", all_markdown)
        self.assertIn("2/8", all_markdown)
        self.assertIn("1/6", all_markdown)

    def test_group_chat_button_count_matches_group_count(self, _mock):
        at = AppTest.from_function(render_my_groups_page).run()

        group_chat_buttons = [b for b in at.button if b.label == "Group Chat"]
        self.assertEqual(len(group_chat_buttons), 2)

    def test_join_card_buttons_exist(self, _mock):
        at = AppTest.from_function(render_my_groups_page).run()

        button_labels = [b.label for b in at.button]
        self.assertIn("Add New Course", button_labels)
        self.assertIn("Discover Groups", button_labels)

    def test_add_new_course_button_exists(self, _mock):
        at = AppTest.from_function(render_my_groups_page).run()

        add_button = next((b for b in at.button if b.label == "Add New Course"), None)
        self.assertIsNotNone(add_button)

    def test_discover_groups_button_exists(self, _mock):
        at = AppTest.from_function(render_my_groups_page).run()

        discover_button = next((b for b in at.button if b.label == "Discover Groups"), None)
        self.assertIsNotNone(discover_button)

    def test_empty_my_groups_still_renders_join_card(self, _mock):
        at = AppTest.from_function(render_empty_my_groups_page).run()

        self.assertFalse(at.exception)

        button_labels = [b.label for b in at.button]
        self.assertIn("Add New Course", button_labels)
        self.assertIn("Discover Groups", button_labels)

        group_chat_buttons = [b for b in at.button if b.label == "Group Chat"]
        self.assertEqual(len(group_chat_buttons), 0)


#############################################################################
# EXPLORE PAGE TESTS
#############################################################################
APP_FILE = "app.py"

@patch("data_fetcher.get_user_profile", return_value=None)
@patch("data_fetcher.get_my_groups", return_value=[])
class TestExplorePage(unittest.TestCase):
    @patch("modules.get_nearby_groups")
    def test_app_initial_load(self, mock_get, _mock_groups, _mock_profile):
        """Test that the Explore Groups page loads correctly."""
        mock_get.return_value = [
            {
                "id": 1,
                "title": "Python Basics",
                "subject": "CS",
                "description": "Looping, conditionals, and debugging practice",
                "schedule": [{"day_of_week": "Mon", "start_time": "6:00 PM"}],
                "location_text": "Zoom",
                "capacity": 20
            }
        ]

        st.session_state.page = "Explore Groups"
        at = AppTest.from_file(APP_FILE).run(timeout=15)

        assert not at.exception
        assert at.text_input[0].placeholder == "Search by title, subject, or description..."

    @patch("modules.get_nearby_groups")
    def test_search_filtering_logic(self, mock_get, _mock_groups, _mock_profile):
        """Test that typing a query filters groups correctly."""
        mock_get.return_value = [
            {
                "id": 1,
                "title": "Python Basics",
                "subject": "CS",
                "description": "Looping, conditionals, and debugging practice",
                "schedule": [{"day_of_week": "Mon", "start_time": "6:00 PM"}],
                "location_text": "Zoom",
                "capacity": 20,
            },
            {
                "id": 2,
                "title": "Calc II Cram Session",
                "subject": "Math",
                "description": "Exam prep",
                "schedule": [{"day_of_week": "Tue", "start_time": "4:00 PM"}],
                "location_text": "Library Room 3",
                "capacity": 6,
            }
        ]

        st.session_state.page = "Explore Groups"
        at = AppTest.from_file(APP_FILE).run(timeout=15)
        at.text_input[0].set_value("Python").run(timeout=15)

        # Assert the get_nearby_groups call included the search query
        mock_get.assert_called_with(
            user_id="user-uuid-1",  # current_user_id in app.py
            search="python",
            lon=0,
            lat=0,
            filter=[],
        )

    @patch("modules.get_nearby_groups")
    def test_search_no_results(self, mock_get, _mock_groups, _mock_profile):
        """Test that a query with no matches displays 'No groups found'."""
        mock_get.return_value = []
        st.session_state.page = "Explore Groups"

        at = AppTest.from_file(APP_FILE).run(timeout=15)
        at.text_input[0].set_value("NonExistentSubject123").run(timeout=15)

        assert len(at.info) == 1
        assert "No groups found" in at.info[0].value

    # @patch("data_fetcher._get_group_schedule")
    @patch("modules.get_nearby_groups")
    def test_view_details_button(self, mock_get, _mock_groups, _mock_profile):
        """Test that clicking 'View Details' updates session_state correctly."""
        mock_get.return_value = [
            {
                "id": 2,
                "title": "Calc II Cram Session",
                "subject": "Math",
                "description": "Exam prep",
                "schedule": [{"day_of_week": "Tue", "start_time": "4:00 PM"}],
                "location_text": "Library Room 3",
                "capacity": 6,
            }
        ]

        st.session_state.page = "Explore Groups"
        at = AppTest.from_file(APP_FILE).run(timeout=15)
        at.button[0].click().run(timeout=15)

        assert not at.exception
        assert at.session_state.selected_group == "Calc II Cram Session"


#############################################################################
# USER PROFILE MODULE TESTS
#############################################################################

@patch("data_fetcher.get_user_profile")
class TestDisplayUserProfile(unittest.TestCase):

    def test_profile_renders_without_exception(self, _mock):
        """Tests that the profile page loads cleanly with no errors."""
        at = AppTest.from_function(render_user_profile_page).run()
        self.assertFalse(at.exception)

    def test_full_name_is_displayed(self, _mock):
        """Tests that the user's full name appears on the page."""
        at = AppTest.from_function(render_user_profile_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("Jane", all_markdown)
        self.assertIn("Doe", all_markdown)

    def test_focus_subjects_are_displayed(self, _mock):
        """Tests that focus subjects appear in the page markdown."""
        at = AppTest.from_function(render_user_profile_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("Data Structures", all_markdown)
        self.assertIn("Machine Learning", all_markdown)

    def test_availability_slots_are_displayed(self, _mock):
        """Tests that time slots render in the availability section markdown."""
        at = AppTest.from_function(render_user_profile_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("9-11 AM", all_markdown, "Expected '9-11 AM' in markdown")
        self.assertIn("1-3 PM", all_markdown, "Expected '1-3 PM' in markdown")

    def test_edit_and_share_buttons_exist(self, _mock):
        """Tests that the Edit Profile and Share Profile buttons are present."""
        at = AppTest.from_function(render_user_profile_page).run()

        button_labels = [b.label for b in at.button]
        self.assertIn("Edit Profile", button_labels)
        self.assertIn("Share Profile", button_labels)

    def test_update_schedule_button_exists(self, _mock):
        """Tests that the Update Schedule button is present."""
        at = AppTest.from_function(render_user_profile_page).run()

        button_labels = [b.label for b in at.button]
        self.assertIn("Update Schedule", button_labels)

    def test_empty_profile_renders_warning_not_exception(self, _mock):
        """Tests that passing None shows a warning instead of crashing."""
        at = AppTest.from_function(render_empty_user_profile_page).run()

        self.assertFalse(at.exception)
        self.assertTrue(len(at.warning) > 0, "Expected a warning for empty profile")

#############################################################################
# GEN-AI-RECOMMENDATION MODULE TESTS
#############################################################################

# Wrapper functions for GenAI tests
# Each wrapper defines its own data so AppTest's isolated context can access it.

def render_genai_fresh():
    from modules import display_genai_advice
    display_genai_advice("test_user_1", ["Python", "Math"])


def render_genai_with_cache():
    import streamlit as st
    from modules import display_genai_advice
    user_id = "returning_user_2"
    interests = ["Physics"]
    cache_key = f"matches_{user_id}_{str(interests)}"
    st.session_state.matches_cache_key = cache_key
    st.session_state.matches_data = [
        {"major": "Physics", "title": "Quantum Mechanics", "match_pct": 99,
         "keywords": ["Quanta", "Theory"], "time": "Mon 5:00 PM",
         "location": "Science Hall", "members": "2/5"}
    ]
    display_genai_advice(user_id, interests)


def render_genai_with_stale_cache():
    import streamlit as st
    from modules import display_genai_advice
    user_id = "user_4"
    new_interests = ["CS", "AI"]
    # Pre-populate cache with OLD interests so the key mismatch forces a refresh
    st.session_state.matches_cache_key = f"matches_{user_id}_{str(['Math'])}"
    st.session_state.matches_data = [
        {"major": "Math", "title": "Old Data", "match_pct": 50,
         "keywords": [], "time": "TBD", "location": "TBD", "members": "0/0"}
    ]
    display_genai_advice(user_id, new_interests)


def render_genai_empty():
    from modules import display_genai_advice
    display_genai_advice("unlucky_user_3", ["Obscure Topic"])


@patch("modules.get_final_recommendations")
class TestGenAIAdviceJourneys(unittest.TestCase):

    def test_cold_start_journey(self, mock_backend):
        """Backend is called when no cache exists and results are rendered."""
        mock_backend.return_value = [
            {"major": "CS", "title": "Python Hackers", "match_pct": 95,
             "keywords": ["Python"], "time": "Tue 5:00 PM",
             "location": "Fisk Library", "members": "2/5"},
            {"major": "Math", "title": "Calculus Study", "match_pct": 88,
             "keywords": ["Calculus"], "time": "Wed 4:00 PM",
             "location": "Math Hall", "members": "3/6"},
        ]
        at = AppTest.from_function(render_genai_fresh).run()
        self.assertFalse(at.exception)
        mock_backend.assert_called_once_with("test_user_1", ["Python", "Math"])

    def test_zero_refresh_journey(self, mock_backend):
        """Backend is NOT called when the cache key matches — no wasted API calls."""
        at = AppTest.from_function(render_genai_with_cache).run()
        self.assertFalse(at.exception)
        mock_backend.assert_not_called()

    def test_changing_preferences_journey(self, mock_backend):
        """Backend IS called when interests change, forcing a cache refresh."""
        mock_backend.return_value = [
            {"major": "CS", "title": "New Data", "match_pct": 99,
             "keywords": ["AI"], "time": "Fri 6:00 PM",
             "location": "Online", "members": "1/4"}
        ]
        at = AppTest.from_function(render_genai_with_stale_cache).run()
        self.assertFalse(at.exception)
        mock_backend.assert_called_once_with("user_4", ["CS", "AI"])

    def test_empty_results_journey(self, mock_backend):
        """Shows a fallback message when the backend returns no results."""
        mock_backend.return_value = []
        at = AppTest.from_function(render_genai_empty).run()
        self.assertFalse(at.exception)
        info_values = [i.value for i in at.info]
        self.assertTrue(
            any("No recommendations" in v for v in info_values),
            "Expected 'No recommendations' message not found"
        )

    def test_static_ui_elements(self, mock_backend):
        """Adjust Preferences button and Sort by selectbox are rendered."""
        mock_backend.return_value = []
        at = AppTest.from_function(render_genai_fresh).run()
        button_labels = [b.label for b in at.button]
        self.assertIn("Adjust Preferences", button_labels)
        sort_boxes = [s for s in at.selectbox if "Sort" in s.label]
        self.assertGreater(len(sort_boxes), 0)


#############################################################################
# ACCOUNT SETTINGS MODULE TESTS
#############################################################################

# Wrapper functions for Account Settings tests

def render_account_settings_page():
    from modules import display_account_settings_page
    display_account_settings_page("user-123")


def render_account_settings_guest():
    from modules import display_account_settings_page
    display_account_settings_page("unknown_user_99")


@patch("modules.get_user_identity_data")
class TestAccountSettingsPage(unittest.TestCase):

    def test_page_renders_without_exception(self, mock_backend):
        """Tests that the Account Settings page loads without crashing."""
        mock_backend.return_value = {"id": "user-123", "email": "real@fisk.edu"}
        at = AppTest.from_function(render_account_settings_page).run()
        self.assertFalse(at.exception)

    def test_backend_called_once(self, mock_backend):
        """Tests that get_user_identity_data is called exactly once on first visit."""
        mock_backend.return_value = {"id": "user-123", "email": "real@fisk.edu"}
        AppTest.from_function(render_account_settings_page).run()
        mock_backend.assert_called_once_with("user-123")

    def test_guest_fallback_when_no_data(self, mock_backend):
        """Tests that the page still renders when the backend returns None."""
        mock_backend.return_value = None
        at = AppTest.from_function(render_account_settings_guest).run()
        self.assertFalse(at.exception)

    def test_edit_bio_button_exists(self, mock_backend):
        """Tests that the Edit Profile Bio button is present."""
        mock_backend.return_value = {"id": "user-123", "email": "real@fisk.edu"}
        at = AppTest.from_function(render_account_settings_page).run()
        button_labels = [b.label for b in at.button]
        self.assertIn("Edit Profile Bio", button_labels)


if __name__ == "__main__":
    unittest.main()