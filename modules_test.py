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
# TEAMMATE TESTS
#
# Add additional test classes below this section for other modules.
#############################################################################


if __name__ == "__main__":
    unittest.main()