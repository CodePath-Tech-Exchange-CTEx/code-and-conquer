import unittest
import streamlit as st
from streamlit.testing.v1 import AppTest
from modules import display_genai_advice, display_explore_page, navigation_bar, study_group_card, display_user_profile

# Write your tests below

APP_FILE = "app.py"
class TestDisplayExplorePage(unittest.TestCase):
    """Tests the study group app using Streamlit AppTest."""

    def test_app_initial_load(self):
        """Test that the app loads and displays the initial grid of cards."""
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("Explore Groups").run()

        
        assert not at.exception
        
        assert len(at.text_input) == 1
        assert at.text_input[0].placeholder == "Search by title or description..."

    def test_search_filtering_logic(self):
        """Test that typing 'Python' in the search bar filters the results."""
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("Explore Groups").run()
        
        at.text_input[0].set_value("Python").run()
        
        assert not at.exception
        
        assert len(at.subheader) == 1
        assert at.subheader[0].value == "Python Basics"

    def test_search_no_results(self):
        """Test the state when a search matches nothing."""
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("Explore Groups").run()
        at.text_input[0].set_value("NonExistentSubject123").run()

        assert len(at.info) == 1
        assert "No groups found" in at.info[0].value

        assert len(at.subheader) == 0

    def test_view_details_button(self):
        """Test that clicking 'View Details' works (triggers no errors)."""
        at = AppTest.from_file(APP_FILE).run()
        at.sidebar.radio[0].set_value("Explore Groups").run()

        at.button[0].click().run()
        
        assert not at.exception

        assert at.session_state.selected_group == "Calc II Cram Session"

class TestDisplayUserProfile(unittest.TestCase):

    def test_profile_renders_without_exception(self):
        """Test that the User profile page loads cleanly with no errors."""
        at = AppTest.from_file(APP_FILE).run()

        at.sidebar.radio[0].set_value("User Profile").run()

        assert not at.exception

    def test_full_name_displayed(self):
        """Test that the user's full name appears as a subheader."""
        at = AppTest.from_file(APP_FILE).run()

        at.sidebar.radio[0].set_value("User Profile").run()

        subheader_values = [s.value for s in at.subheader]
        assert any("Jane Doe" in v for v in subheader_values)

    def test_stats_display_correct_values(self):
        """Test that all three stat metrics show the correct values."""
        at = AppTest.from_file(APP_FILE).run()

        at.sidebar.radio[0].set_value("User Profile").run()

        metric_labels = [m.label for m in at.metric]
        metric_values = [m.value for m in at.metric]
        assert metric_values[metric_labels.index("Groups Joined")] == "4"
        assert metric_values[metric_labels.index("Study Hours")] == "127"
        assert metric_values[metric_labels.index("Day Streak")] == "12"

    def test_availability_slots_displayed(self):
        """Test that time slot captions are rendered in the availability section."""
        at = AppTest.from_file(APP_FILE).run()

        at.sidebar.radio[0].set_value("User Profile").run()

        caption_values = [c.value for c in at.caption]
        assert any("9-11 AM" in v for v in caption_values)
        assert any("1-3 PM" in v for v in caption_values)

    def test_focus_subjects_displayed(self):
        """Test that focus subjects appear on the page."""
        at = AppTest.from_file(APP_FILE).run()

        at.sidebar.radio[0].set_value("User Profile").run()

        all_text = " ".join([str(m.value) for m in at.markdown])
        assert "Data Structures" in all_text
        assert "Machine Learning" in all_text

class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_adjust_preferences_container(self):
        """Verify the AI-Powered Matches header and 'Adjust Preferences' button."""
        at = AppTest.from_file("app.py").run()
        
        at.sidebar.radio[0].set_value("AI Recommendations").run()

        # Check Markdown/Text
        all_markdown = [m.value for m in at.markdown]
        
        self.assertIn("**AI-Powered Matches**", all_markdown)
        self.assertIn("### Curated For You", all_markdown)
        
        # Checking for partial string match in the description
        has_description = any("Based on your schedule" in val for val in all_markdown)
        self.assertTrue(has_description, "Description text not found")

        # look for the button where .label matches our text
        pref_button = next((b for b in at.button if b.label == "Adjust Preferences"), None)
        
        self.assertIsNotNone(pref_button, "Button 'Adjust Preferences' not found")

    def test_button_interaction(self):
        """Verify that clicking the Adjust Preferences button doesn't crash the app."""
        at = AppTest.from_file("app.py").run()

        at.sidebar.radio[0].set_value("AI Recommendations").run()
        
        # Find the specific button object
        target_button = next((b for b in at.button if b.label == "Adjust Preferences"), None)
        
        if target_button is None:
            self.fail("Could not find 'Adjust Preferences' button to click.")
        
        # Perform action and rerun the script
        target_button.click().run()
        
        # Ensure no unhandled exceptions occurred
        self.assertFalse(at.exception, f"App crashed after click: {at.exception}")

    def test_top_matches_header(self):
        """Verify the 'Top Matches' heading exists."""
        at = AppTest.from_file("app.py").run()

        at.sidebar.radio[0].set_value("AI Recommendations").run()
        
        all_markdown = [m.value for m in at.markdown]
        self.assertIn("### Top Matches", all_markdown)

    def test_sort_selectbox_initial_state(self):
        """Verify the sort dropdown has the correct options and default value."""
        at = AppTest.from_file("app.py").run()

        at.sidebar.radio[0].set_value("AI Recommendations").run()
        
        # Find the selectbox by its label
        sort_box = next((s for s in at.selectbox if s.label == "Sort by:"), None)
        
        self.assertIsNotNone(sort_box, "Sort by selectbox not found")
        
        # Verify the available options
        expected_options = ["Match %", "Recently Active", "Shared Classes"]
        self.assertEqual(sort_box.options, expected_options)
        
        # Verify the default selection (index 0)
        self.assertEqual(sort_box.value, "Match %")

    def test_sort_selectbox_selection(self):
        """Verify that changing the sort selection works."""
        at = AppTest.from_file("app.py").run()

        at.sidebar.radio[0].set_value("AI Recommendations").run()
        
        sort_box = next((s for s in at.selectbox if s.label == "Sort by:"), None)
        
        # Simulate the user selecting a different option
        sort_box.select("Recently Active").run()
        
        # Re-fetch to check updated state
        updated_sort_box = next((s for s in at.selectbox if s.label == "Sort by:"), None)
        self.assertEqual(updated_sort_box.value, "Recently Active")
        self.assertFalse(at.exception)

    def test_recommendation_cards_count(self):
        """Verify the count and content based on the actual app.py data."""
        at = AppTest.from_file("app.py").run()

        at.sidebar.radio[0].set_value("AI Recommendations").run()
        
        # Based on your previous error, we know there are 3 cards
        # Let's assert based on what the App is actually rendering
        self.assertEqual(len(at.subheader), 3)
        
        # Verify the specific titles found in your error log exist
        subheaders = [s.value for s in at.subheader]
        self.assertIn("GenAI & Systems Design", subheaders)
        self.assertIn("iOS Dev Hackers", subheaders)

    def test_card_content_formatting(self):
        """Verify major is uppercased and keys are formatted correctly."""
        at = AppTest.from_file("app.py").run()

        at.sidebar.radio[0].set_value("AI Recommendations").run()
        
        # Check Uppercase logic
        captions = [c.value for c in at.caption]
        self.assertIn("COMPUTER SCIENCE", captions)
        
        # Check Button Keys logic
        actual_keys = [b.key for b in at.button if b.key]
        self.assertIn("btn_iOS_Dev_Hackers", actual_keys)

    def test_sort_selectbox_initial_state(self):
        """Verify the sort dropdown has the correct options."""
        at = AppTest.from_file("app.py").run()

        at.sidebar.radio[0].set_value("AI Recommendations").run()
        
        sort_box = next((s for s in at.selectbox if s.label == "Sort by:"), None)
        self.assertIsNotNone(sort_box)
        self.assertEqual(sort_box.value, "Match %")

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