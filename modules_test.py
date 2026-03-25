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
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from modules import navigation_bar, display_explore_page, study_group_card, display_account_settings_page, display_genai_advice  # replace with actual module name
from data_fetcher import get_nearby_groups
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
class TestExplorePage(unittest.TestCase):
    @patch("modules.get_nearby_groups")
    def test_app_initial_load(self, mock_get):
        """Test that the Explore Groups page loads correctly."""
        mock_get.return_value = [
            {
                "id": 1,
                "title": "Python Basics",
                "subject": "CS",
                "description": "Looping, conditionals, and debugging practice",
                "schedule": [{"day_of_week": "Mon", "start_time": "6:00 PM"}],
                "location_text": "Zoom",
                "capacity": 20,
            }
        ]

        st.session_state.page = "Explore Groups"
        at = AppTest.from_file(APP_FILE).run()

        assert not at.exception
        assert at.text_input[0].placeholder == "Search by title, subject, or description..."

    @patch("modules.get_nearby_groups")
    def test_search_filtering_logic(self, mock_get):
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
            },
        ]

        st.session_state.page = "Explore Groups"
        at = AppTest.from_file(APP_FILE).run()
        at.text_input[0].set_value("Python").run()

        # Assert the get_nearby_groups call included the search query
        mock_get.assert_called_with(
            user_id="user-uuid-1",  # current_user_id in app.py
            search="python",
            lon=0,
            lat=0,
            filter=[],
        )

    @patch("modules.get_nearby_groups")
    def test_search_no_results(self, mock_get):
        """Test that a query with no matches displays 'No groups found'."""
        mock_get.return_value = []
        st.session_state.page = "Explore Groups"

        at = AppTest.from_file(APP_FILE).run()
        at.text_input[0].set_value("NonExistentSubject123").run()

        assert len(at.info) == 1
        assert "No groups found" in at.info[0].value

    @patch("modules.get_nearby_groups")
    def test_view_details_button(self, mock_get):
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
        at = AppTest.from_file(APP_FILE).run()
        at.button[0].click().run()

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
############################################################################

class TestGenAIAdviceJourneys(unittest.TestCase):

    @patch('streamlit.session_state')
    @patch('streamlit.columns')
    @patch('modules.create_match_card')
    @patch('modules.get_final_recommendations')
    def test_cold_start_journey(self, mock_backend, mock_card, mock_cols, mock_state):
        # Tell the mocked session_state to act empty
        mock_state.__contains__.return_value = False
        
        # Mock the backend returning fresh AI-generated data
        mock_backend.return_value = [
            {"major": "CS", "title": "Python Hackers", "match_pct": 95},
            {"major": "Math", "title": "Calculus Study", "match_pct": 88}
        ]
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        user_id = "new_user_1"
        interests = ["Python", "Math"]
        
        # Action
        display_genai_advice(user_id, interests)
        
        # Assertions
        mock_backend.assert_called_once_with(user_id, interests)
        expected_cache_key = f"matches_{user_id}_{str(interests)}"
        self.assertEqual(mock_state.matches_cache_key, expected_cache_key)
        self.assertEqual(mock_card.call_count, 2)

    
    @patch('streamlit.session_state')
    @patch('streamlit.columns')
    @patch('modules.create_match_card')
    @patch('modules.get_final_recommendations')
    def test_zero_refresh_journey(self, mock_backend, mock_card, mock_cols, mock_state):
        user_id = "returning_user_2"
        interests = ["Physics"]
        expected_cache_key = f"matches_{user_id}_{str(interests)}"
        
        # Simulate that cache key and data already exist in session state
        mock_state.__contains__.side_effect = lambda key: key in ["matches_cache_key", "matches_data"]
        
        # Set the expected cache key
        mock_state.matches_cache_key = expected_cache_key
        
        # Provide previously generated dummy data
        mock_state.matches_data = [{"major": "Physics", "title": "Quantum Mechanics", "match_pct": 99}]
        
        # FIX: Return TWO mocks because the UI unpacks: top_col, action_col = st.columns(...)
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        # Execute the UI function
        display_genai_advice(user_id, interests)
        
        # Ensure the backend API was NOT called
        mock_backend.assert_not_called()
        
        # Ensure the UI rendered the cached card
        self.assertEqual(mock_card.call_count, 1)
        mock_card.assert_any_call(major="Physics", title="Quantum Mechanics", match_pct=99)

    
    @patch('streamlit.session_state')
    @patch('streamlit.columns')
    @patch('streamlit.info') # Mocking st.info to check the fallback message
    @patch('modules.create_match_card')
    @patch('modules.get_final_recommendations')
    def test_empty_results_journey(self, mock_backend, mock_card, mock_info, mock_cols, mock_state):
        user_id = "unlucky_user_3"
        interests = ["Obscure Topic"]
        
        # Simulate an empty cache so the backend is forced to run
        mock_state.__contains__.return_value = False
        
        # Simulate the backend failing or finding absolutely zero matches
        mock_backend.return_value = []
        
        # Mock the Streamlit layout columns (The header requires 2 columns)
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        # Execute the UI function
        display_genai_advice(user_id, interests)
        
        # Ensure the backend was actually called
        mock_backend.assert_called_once_with(user_id, interests)
        
        # Verify the empty result was cached to prevent infinite API retries
        self.assertEqual(mock_state.matches_data, [])
        
        # Verify the graceful fallback message was shown to the user
        mock_info.assert_called_once_with("No recommendations found right now.")
        
        # Ensure the UI didn't try to draw any empty cards
        mock_card.assert_not_called()


    @patch('streamlit.session_state')
    @patch('streamlit.columns')
    @patch('modules.create_match_card')
    @patch('modules.get_final_recommendations')
    def test_changing_preferences_journey(self, mock_backend, mock_card, mock_cols, mock_state):
        user_id = "fickle_user_4"
        old_interests = ["Math"]
        new_interests = ["CS", "AI"]
        
        # Simulate existing cache for OLD interests ("Math")
        mock_state.__contains__.side_effect = lambda key: key in ["matches_cache_key", "matches_data"]
        mock_state.matches_cache_key = f"matches_{user_id}_{str(old_interests)}"
        mock_state.matches_data = [{"major": "Math", "title": "Old Data", "match_pct": 50}]
        
        # Mock backend returning new data for NEW interests ("CS", "AI")
        mock_backend.return_value = [{"major": "CS", "title": "New Data", "match_pct": 99}]
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        # Execute UI with NEW interests
        display_genai_advice(user_id, new_interests)
        
        # Verify backend WAS called because the cache key mismatch forced an update
        mock_backend.assert_called_once_with(user_id, new_interests)
        
        # Verify cache was successfully overwritten with the new key
        expected_new_key = f"matches_{user_id}_{str(new_interests)}"
        self.assertEqual(mock_state.matches_cache_key, expected_new_key)
        
        # Verify UI drew the NEW card instead of the old one
        mock_card.assert_called_once_with(major="CS", title="New Data", match_pct=99)

    
    @patch('streamlit.session_state')
    @patch('streamlit.columns')
    @patch('modules.create_match_card')
    @patch('modules.get_final_recommendations')
    def test_grid_layout_math(self, mock_backend, mock_card, mock_cols, mock_state):
        # Force empty cache
        mock_state.__contains__.return_value = False
        
        # Return exactly 3 items to test the odd-number grid logic
        mock_backend.return_value = [
            {"title": "Card 1"}, {"title": "Card 2"}, {"title": "Card 3"}
        ]
        
        # Streamlit unpacks max 2 columns at a time in your code
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        # Execute UI
        display_genai_advice("user", ["Testing"])
        
        # The code calls st.columns 2 times for the headers, plus 2 times for the rows = 4 total calls
        self.assertEqual(mock_cols.call_count, 4)
        
        # Verify exactly 3 cards were drawn, proving the loop didn't drop the odd card out
        self.assertEqual(mock_card.call_count, 3)

    @patch('streamlit.session_state')
    @patch('streamlit.selectbox')
    @patch('streamlit.button')
    @patch('streamlit.columns')
    @patch('modules.create_match_card')
    @patch('modules.get_final_recommendations')
    def test_static_ui_elements(self, mock_backend, mock_card, mock_cols, mock_btn, mock_select, mock_state):
        # Force empty cache and empty results so we just check the static top headers
        mock_state.__contains__.return_value = False
        mock_backend.return_value = []
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        # Execute UI
        display_genai_advice("user", ["Testing"])
        
        # Verify the "Adjust Preferences" button is correctly rendered
        mock_btn.assert_any_call("Adjust Preferences", use_container_width=True, key="adjust_prefs")
        
        # Verify the "Sort by" dropdown is rendered with the exact options provided
        mock_select.assert_called_once_with(
            "Sort by:",
            options=["Match %", "Recently Active", "Shared Classes"],
            index=0,
            label_visibility="collapsed",
            key="sort_matches"
        )


# #############################################################################
# # ACCOUNT SETTINGS MODULE TESTS
# #############################################################################
class TestDataFetcher(unittest.TestCase):

    @patch('streamlit.session_state', {})
    @patch('streamlit.columns')
    @patch('modules.get_user_identity_data') 
    def test_happy_path_first_visit(self, mock_backend, mock_cols):
        # Provide mock data to simulate a successful database fetch
        mock_backend.return_value = {"id": "user-123", "email": "real@fisk.edu"}
        
        # Mock the two-column layout expected by the UI
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        # Execute the UI function with our test user
        display_account_settings_page("user-123")
        
        # Verify the backend was called exactly once to fetch the data
        mock_backend.assert_called_once_with("user-123")
        
        # Verify the mock data was correctly saved into the session state cache
        expected_cache_key = "account_cache_user-123"
        self.assertIn(expected_cache_key, st.session_state)
        self.assertEqual(st.session_state[expected_cache_key]["email"], "real@fisk.edu")

    
    @patch('streamlit.session_state', {})
    @patch('streamlit.columns')
    @patch('modules.get_user_identity_data')
    def test_guest_fallback_journey(self, mock_backend, mock_cols):
        # Simulate the database returning no data (e.g., new user or DB error)
        mock_backend.return_value = None
        
        # Mock the Streamlit layout columns
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        # Execute the UI function with an unrecognized user ID
        user_id = "unknown_user_99"
        display_account_settings_page(user_id)
        
        # Verify the backend was actually queried
        mock_backend.assert_called_once_with(user_id)
        
        # Verify the "Guest" fallback data was generated and saved to the cache
        expected_cache_key = f"account_cache_{user_id}"
        self.assertIn(expected_cache_key, st.session_state)
        
        # Confirm the exact guest values are correct
        cached_data = st.session_state[expected_cache_key]
        self.assertEqual(cached_data["email"], "pending@fisk.edu")
        self.assertEqual(cached_data["id"], "No data")
        self.assertTrue(cached_data["is_guest"])

    @patch('streamlit.session_state', {})
    @patch('streamlit.info')
    @patch('streamlit.button')
    @patch('streamlit.columns')
    @patch('modules.get_user_identity_data')
    def test_edit_bio_button_click(self, mock_backend, mock_cols, mock_btn, mock_info):
        # Provide baseline data to render the page
        mock_backend.return_value = {"id": "u1", "email": "e@fisk.edu"}
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        # This brilliant trick forces ONLY the "Edit Profile Bio" button to simulate a click (return True)
        mock_btn.side_effect = lambda name, **kwargs: name == "Edit Profile Bio"
        
        # Execute the UI function
        display_account_settings_page("u1")
        
        # Verify the correct Streamlit banner was triggered by the click
        mock_info.assert_called_once_with("Redirecting to profile editor...")

if __name__ == "__main__":
    unittest.main()