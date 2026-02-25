import unittest
import streamlit as st
from streamlit.testing.v1 import AppTest
from modules import display_explore_page, navigation_bar, study_group_card, display_user_profile

# Write your tests below

APP_FILE = "app.py"
class TestDisplayExplorePage(unittest.TestCase):
    """Tests the study group app using Streamlit AppTest."""

    def test_app_initial_load(self):
        """Test that the app loads and displays the initial grid of cards."""
        at = AppTest.from_file(APP_FILE).run()
        
        assert not at.exception
        
        assert len(at.text_input) == 1
        assert at.text_input[0].placeholder == "Search by title or description..."

    def test_search_filtering_logic(self):
        """Test that typing 'Python' in the search bar filters the results."""
        at = AppTest.from_file(APP_FILE).run()
        
        at.text_input[0].set_value("Python").run()
        
        assert not at.exception
        
        assert len(at.subheader) == 1
        assert at.subheader[0].value == "Python Basics"

    def test_search_no_results(self):
        """Test the state when a search matches nothing."""
        at = AppTest.from_file(APP_FILE).run()

        at.text_input[0].set_value("NonExistentSubject123").run()

        assert len(at.info) == 1
        assert "No groups found" in at.info[0].value

        assert len(at.subheader) == 0

    def test_view_details_button(self):
        """Test that clicking 'View Details' works (triggers no errors)."""
        at = AppTest.from_file(APP_FILE).run()

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


if __name__ == "__main__":
    unittest.main()