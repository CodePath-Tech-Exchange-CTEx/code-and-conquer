#############################################################################
# data_fetcher_test.py
#
# Unit tests for data_fetcher.py
#
# This section tests only the My Groups module.
# Teammates can add their own test classes below for other modules.
#############################################################################

import unittest
from unittest.mock import patch

from data_fetcher import get_my_groups


#############################################################################
# MY GROUPS MODULE TESTS
#############################################################################
class TestMyGroupsDataFetcher(unittest.TestCase):

    def test_foo(self):
        """Tests foo."""
        pass
    @patch("data_fetcher._run_query")
    def test_get_my_groups_formats_result_for_ui(self, mock_run_query):
        """Tests that get_my_groups formats database rows for the My Groups UI."""
        mock_run_query.return_value = [
            {
                "group_id": "group-uuid-1",
                "title": "GenAI & Systems Design",
                "subject": "Computer Science",
                "mode": "hybrid",
                "location": "Fisk Library, Room 12",
                "capacity": 8,
                "day_of_week": "Tue",
                "start_time": "17:00",
                "end_time": "19:00",
                "active_members": 2,
            }
        ]

        result = get_my_groups("user-uuid-1")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["group_id"], "group-uuid-1")
        self.assertEqual(result[0]["title"], "GenAI & Systems Design")
        self.assertEqual(result[0]["icon"], "💻")
        self.assertEqual(result[0]["days"], "Tue 17:00-19:00")
        self.assertEqual(result[0]["mode"], "hybrid")
        self.assertEqual(result[0]["location"], "Fisk Library, Room 12")
        self.assertEqual(result[0]["members"], "2/8")

    @patch("data_fetcher._run_query")
    def test_get_my_groups_returns_empty_list_when_no_groups(self, mock_run_query):
        """Tests that get_my_groups returns an empty list when the user has no groups."""
        mock_run_query.return_value = []

        result = get_my_groups("missing-user")

        self.assertEqual(result, [])

    @patch("data_fetcher._run_query")
    def test_get_my_groups_handles_missing_schedule_fields(self, mock_run_query):
        """Tests that get_my_groups still works when schedule fields are missing."""
        mock_run_query.return_value = [
            {
                "group_id": "group-uuid-2",
                "title": "Calc II Cram",
                "subject": "Mathematics",
                "mode": "in-person",
                "location": "Math Building, Room 3",
                "capacity": 6,
                "day_of_week": None,
                "start_time": None,
                "end_time": None,
                "active_members": 1,
            }
        ]

        result = get_my_groups("user-uuid-2")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["icon"], "📐")
        self.assertEqual(result[0]["days"], "TBD")
        self.assertEqual(result[0]["members"], "1/6")


#############################################################################
# DANIEL TESTS
#
# Add additional test classes below this section for other modules.
#############################################################################

    
    @patch("your_module.bq.Client")  # adjust if you didn't alias as bq
    def test_get_groups_returns_data(self, mock_client_class):
        # --- Arrange ---
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock query job and results
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job

        mock_rows = [
            {
                "id": "group-1",
                "name": "AI Study Group",
                "subject": "Computer Science",
                "location_text": "Library",
                "distance_meters": 100.0
            },
            {
                "id": "group-2",
                "name": "Calculus Group",
                "subject": "Mathematics",
                "location_text": "Room 101",
                "distance_meters": 200.0
            }
        ]

        mock_query_job.result.return_value = mock_rows

        # --- Act ---
        result = get_groups("AI", 18.38, -65.83)

        # --- Assert ---
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "AI Study Group")
        self.assertEqual(result[1]["distance_meters"], 200.0)

        # Ensure query was called
        mock_client.query.assert_called_once()

    

if __name__ == "__main__":
    unittest.main()