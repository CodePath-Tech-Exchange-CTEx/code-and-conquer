# tests/test_modules.py
import importlib
import modules
import pytest

# --- Simple Streamlit stub used by tests ---
class StreamlitStub:
    def __init__(self, button_map=None):
        """
        button_map: dict mapping button key -> bool (True -> simulated click)
        """
        self.button_map = button_map or {}
        self.logs = []
import unittest
from unittest.mock import MagicMock, patch
import streamlit as st
from streamlit.testing.v1 import AppTest
from modules import display_explore_page, navigation_bar, study_group_card

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


if __name__ == "__main__":
    unittest.main()