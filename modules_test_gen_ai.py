import unittest
from streamlit.testing.v1 import AppTest

APP_FILE = "app.py"

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

    def test_sort_selectbox_initial_state(self):
        """Verify the sort dropdown has the correct options."""
        at = AppTest.from_file("app.py").run()

        at.sidebar.radio[0].set_value("AI Recommendations").run()
        
        sort_box = next((s for s in at.selectbox if s.label == "Sort by:"), None)
        self.assertIsNotNone(sort_box)
        self.assertEqual(sort_box.value, "Match %")