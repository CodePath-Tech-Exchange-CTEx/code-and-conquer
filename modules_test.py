#############################################################################
# modules_test.py
#
# Unit tests for modules.py
#
# This file currently contains tests for:
#   - My Groups module only
#
# Teammates can add their own test classes below for other modules.
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest


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
# USER PROFILE MODULE TESTS
#############################################################################
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


class TestDisplayUserProfile(unittest.TestCase):

    def test_profile_renders_without_exception(self):
        """Tests that the profile page loads cleanly with no errors."""
        at = AppTest.from_function(render_user_profile_page).run()
        self.assertFalse(at.exception)

    def test_full_name_is_displayed(self):
        """Tests that the user's full name appears on the page."""
        at = AppTest.from_function(render_user_profile_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("Jane", all_markdown)
        self.assertIn("Doe", all_markdown)

    def test_focus_subjects_are_displayed(self):
        """Tests that focus subjects appear in the page markdown."""
        at = AppTest.from_function(render_user_profile_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("Data Structures", all_markdown)
        self.assertIn("Machine Learning", all_markdown)

    def test_availability_slots_are_displayed(self):
        """Tests that time slots render in the availability section markdown."""
        at = AppTest.from_function(render_user_profile_page).run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("9-11 AM", all_markdown, "Expected '9-11 AM' in markdown")
        self.assertIn("1-3 PM", all_markdown, "Expected '1-3 PM' in markdown")

    def test_edit_and_share_buttons_exist(self):
        """Tests that the Edit Profile and Share Profile buttons are present."""
        at = AppTest.from_function(render_user_profile_page).run()

        button_labels = [b.label for b in at.button]
        self.assertIn("Edit Profile", button_labels)
        self.assertIn("Share Profile", button_labels)

    def test_update_schedule_button_exists(self):
        """Tests that the Update Schedule button is present."""
        at = AppTest.from_function(render_user_profile_page).run()

        button_labels = [b.label for b in at.button]
        self.assertIn("Update Schedule", button_labels)

    def test_empty_profile_renders_warning_not_exception(self):
        """Tests that passing None shows a warning instead of crashing."""
        at = AppTest.from_function(render_empty_user_profile_page).run()

        self.assertFalse(at.exception)
        self.assertTrue(len(at.warning) > 0, "Expected a warning for empty profile")


if __name__ == "__main__":
    unittest.main()