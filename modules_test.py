# modules_test.py
import unittest
from streamlit.testing.v1 import AppTest

APP_FILE = "app.py"


class TestDisplayExplorePage(unittest.TestCase):
    def test_app_initial_load(self):
        at = AppTest.from_file(APP_FILE).run()
        self.assertFalse(at.exception)

        self.assertEqual(len(at.text_input), 1)
        self.assertEqual(at.text_input[0].placeholder, "Search by title or description...")

    def test_search_filtering_logic(self):
        at = AppTest.from_file(APP_FILE).run()
        at.text_input[0].set_value("Python").run()
        self.assertFalse(at.exception)

        # Expect only the Python Basics subheader from explore page
        subs = [s.value for s in at.subheader]
        self.assertIn("Python Basics", subs)

    def test_search_no_results(self):
        at = AppTest.from_file(APP_FILE).run()
        at.text_input[0].set_value("NonExistentSubject123").run()
        self.assertFalse(at.exception)

        self.assertEqual(len(at.info), 1)
        self.assertIn("No groups found", at.info[0].value)
        # No cards when empty
        self.assertEqual(len(at.subheader), 0)

    def test_view_details_button(self):
        at = AppTest.from_file(APP_FILE).run()
        first_view_btn = next((b for b in at.button if b.label == "View Details"), None)
        self.assertIsNotNone(first_view_btn)

        first_view_btn.click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state.selected_group, "Calc II Cram Session")


class TestDisplayUserProfile(unittest.TestCase):
    def test_profile_renders_without_exception(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("User Profile").run()
        self.assertFalse(at.exception)

    def test_full_name_displayed(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("User Profile").run()
        subheader_values = [s.value for s in at.subheader]
        self.assertTrue(any("Jane Doe" in v for v in subheader_values))

    def test_stats_display_correct_values(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("User Profile").run()

        metric_labels = [m.label for m in at.metric]
        metric_values = [m.value for m in at.metric]
        self.assertEqual(metric_values[metric_labels.index("Groups Joined")], "4")
        self.assertEqual(metric_values[metric_labels.index("Study Hours")], "127")
        self.assertEqual(metric_values[metric_labels.index("Day Streak")], "12")

    def test_availability_slots_displayed(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("User Profile").run()

        caption_values = [c.value for c in at.caption]
        self.assertTrue(any("9-11 AM" in v for v in caption_values))
        self.assertTrue(any("1-3 PM" in v for v in caption_values))

    def test_focus_subjects_displayed(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("User Profile").run()

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("Data Structures", all_markdown)
        self.assertIn("Machine Learning", all_markdown)


class TestDisplayGenAiAdvice(unittest.TestCase):
    def test_adjust_preferences_container(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("AI Recommendations").run()

        all_markdown = [m.value for m in at.markdown]
        self.assertIn("**AI-Powered Matches**", all_markdown)
        self.assertIn("### Curated For You", all_markdown)

        has_description = any("Based on your schedule" in val for val in all_markdown)
        self.assertTrue(has_description)

        pref_button = next((b for b in at.button if b.label == "Adjust Preferences"), None)
        self.assertIsNotNone(pref_button)

    def test_button_interaction(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("AI Recommendations").run()

        target_button = next((b for b in at.button if b.label == "Adjust Preferences"), None)
        self.assertIsNotNone(target_button)

        target_button.click().run()
        self.assertFalse(at.exception)

    def test_top_matches_header(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("AI Recommendations").run()

        all_markdown = [m.value for m in at.markdown]
        self.assertIn("### Top Matches", all_markdown)

    def test_sort_selectbox_initial_state(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("AI Recommendations").run()

        sort_box = next((s for s in at.selectbox if s.label == "Sort by:"), None)
        self.assertIsNotNone(sort_box)
        self.assertEqual(sort_box.value, "Match %")
        self.assertEqual(sort_box.options, ["Match %", "Recently Active", "Shared Classes"])

    def test_sort_selectbox_selection(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("AI Recommendations").run()

        sort_box = next((s for s in at.selectbox if s.label == "Sort by:"), None)
        self.assertIsNotNone(sort_box)

        sort_box.select("Recently Active").run()
        updated_sort_box = next((s for s in at.selectbox if s.label == "Sort by:"), None)
        self.assertEqual(updated_sort_box.value, "Recently Active")
        self.assertFalse(at.exception)

    def test_recommendation_cards_count(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("AI Recommendations").run()

        self.assertEqual(len(at.subheader), 3)
        subheaders = [s.value for s in at.subheader]
        self.assertIn("GenAI & Systems Design", subheaders)
        self.assertIn("iOS Dev Hackers", subheaders)

    def test_card_content_formatting(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("AI Recommendations").run()

        captions = [c.value for c in at.caption]
        self.assertIn("COMPUTER SCIENCE", captions)

        actual_keys = [b.key for b in at.button if b.key]
        self.assertIn("btn_iOS_Dev_Hackers", actual_keys)


class TestMyGroupsPage(unittest.TestCase):
    def test_my_groups_page_renders(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("My Groups").run()
        self.assertFalse(at.exception)

        all_markdown = " ".join([m.value for m in at.markdown])
        self.assertIn("My Study Group", all_markdown)

    def test_group_chat_buttons_count(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("My Groups").run()
        self.assertFalse(at.exception)

        group_chat_buttons = [b for b in at.button if b.label == "Group Chat"]
        self.assertEqual(len(group_chat_buttons), 3)

    def test_add_new_course_button_exists(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("My Groups").run()
        self.assertFalse(at.exception)

        add_btn = next((b for b in at.button if b.label == "Add New Course"), None)
        self.assertIsNotNone(add_btn, "Add New Course button not found")

    def test_discover_groups_navigates_to_explore(self):
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("My Groups").run()
        self.assertFalse(at.exception)

        discover_btn = next((b for b in at.button if b.label == "Discover Groups"), None)
        self.assertIsNotNone(discover_btn)

        discover_btn.click().run()
        # clicking Discover Groups should set page to Explore Groups
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state.page, "Explore Groups")


if __name__ == "__main__":
    unittest.main()