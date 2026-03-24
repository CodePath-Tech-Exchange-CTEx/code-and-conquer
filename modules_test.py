#############################################################################
# modules_test.py
#
# Unit tests for modules.py
#
# Current owner:
#   - [Your Name]
#
# This file currently contains tests for:
#   - My Groups module only
#
# Teammates can add their own test classes below for other modules.
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from modules import navigation_bar, display_explore_page, study_group_card  # replace with actual module name
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


#############################################################################
# MY GROUPS MODULE TESTS
#############################################################################
class TestMyGroupsPage(unittest.TestCase):
    def test_my_groups_page_renders_without_exception(self):
        at = AppTest.from_function(render_my_groups_page).run()
        self.assertFalse(at.exception)

    def test_my_groups_title_and_subtitle_render(self):
        at = AppTest.from_function(render_my_groups_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])

        self.assertIn("My Study Groups", all_markdown)
        self.assertIn("Manage your active groups", all_markdown)

    def test_group_titles_render(self):
        at = AppTest.from_function(render_my_groups_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])

        self.assertIn("GenAI &amp; Systems Design", all_markdown)
        self.assertIn("Calc II Cram", all_markdown)

    def test_group_locations_and_members_render(self):
        at = AppTest.from_function(render_my_groups_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])

        self.assertIn("Fisk Library, Room 12", all_markdown)
        self.assertIn("Math Building, Room 3", all_markdown)
        self.assertIn("2/8", all_markdown)
        self.assertIn("1/6", all_markdown)

    def test_group_chat_button_count_matches_group_count(self):
        at = AppTest.from_function(render_my_groups_page).run()

        group_chat_buttons = [b for b in at.button if b.label == "Group Chat"]
        self.assertEqual(len(group_chat_buttons), 2)

    def test_join_card_buttons_exist(self):
        at = AppTest.from_function(render_my_groups_page).run()

        button_labels = [b.label for b in at.button]

        self.assertIn("Add New Course", button_labels)
        self.assertIn("Discover Groups", button_labels)

    def test_add_new_course_button_exists(self):
        at = AppTest.from_function(render_my_groups_page).run()

        add_button = next((b for b in at.button if b.label == "Add New Course"), None)
        self.assertIsNotNone(add_button)

    def test_discover_groups_button_exists(self):
        at = AppTest.from_function(render_my_groups_page).run()

        discover_button = next((b for b in at.button if b.label == "Discover Groups"), None)
        self.assertIsNotNone(discover_button)

    def test_empty_my_groups_still_renders_join_card(self):
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


if __name__ == "__main__":
    unittest.main()