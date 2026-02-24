#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest
from modules import display_user_profile

# Write your tests below

APP_FILE = "app.py"


class TestDisplayUserProfile(unittest.TestCase):

    def test_profile_renders_without_exception(self):
        """Test that the profile page loads cleanly with no errors."""
        at = AppTest.from_file(APP_FILE).run()

        assert not at.exception

    def test_full_name_displayed(self):
        """Test that the user's full name appears as a subheader."""
        at = AppTest.from_file(APP_FILE).run()

        subheader_values = [s.value for s in at.subheader]
        assert any("Jane Doe" in v for v in subheader_values)

    def test_stats_display_correct_values(self):
        """Test that all three stat metrics show the correct values."""
        at = AppTest.from_file(APP_FILE).run()

        metric_labels = [m.label for m in at.metric]
        metric_values = [m.value for m in at.metric]
        assert metric_values[metric_labels.index("Groups Joined")] == "4"
        assert metric_values[metric_labels.index("Study Hours")] == "127"
        assert metric_values[metric_labels.index("Day Streak")] == "12"

    def test_availability_slots_displayed(self):
        """Test that time slot captions are rendered in the availability section."""
        at = AppTest.from_file(APP_FILE).run()

        caption_values = [c.value for c in at.caption]
        assert any("9-11 AM" in v for v in caption_values)
        assert any("1-3 PM" in v for v in caption_values)

    def test_focus_subjects_displayed(self):
        """Test that focus subjects appear on the page."""
        at = AppTest.from_file(APP_FILE).run()

        all_text = " ".join([str(m.value) for m in at.markdown])
        assert "Data Structures" in all_text
        assert "Machine Learning" in all_text

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
