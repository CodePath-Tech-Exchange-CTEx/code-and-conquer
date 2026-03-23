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

    

#############################################################################
# USER PROFILE MODULE TESTS
#############################################################################
from data_fetcher import get_user_profile

class TestGetUserProfile(unittest.TestCase):

    @patch("data_fetcher._run_query")
    def test_returns_correct_name(self, mock_run_query):
        """Tests that get_user_profile maps first_name and last_name correctly."""
        mock_run_query.side_effect = [
            # first call: user row
            [{
                "first_name": "Jane",
                "last_name": "Doe",
                "major": "Computer Science",
                "education_level": "Junior Year",
                "institution": "Stanford University",
                "email": "jane.doe@stanford.edu",
                "about_me": "Loves algorithms.",
                "preferences": '{"focus_subjects": ["Data Structures", "Machine Learning"], "study_hours": 127, "day_streak": 12}',
                "availability": '[{"day": "Mon", "slots": ["9-11 AM"]}, {"day": "Tue", "slots": ["1-3 PM"]}]',
            }],
            # second call: membership count
            [{"groups_joined": 4}],
        ]

        result = get_user_profile("user-uuid-1")

        self.assertEqual(result["first_name"], "Jane")
        self.assertEqual(result["last_name"], "Doe")

    @patch("data_fetcher._run_query")
    def test_returns_correct_stats(self, mock_run_query):
        """Tests that study_hours, day_streak, and groups_joined are mapped correctly."""
        mock_run_query.side_effect = [
            [{
                "first_name": "Jane",
                "last_name": "Doe",
                "major": "Computer Science",
                "education_level": "Junior Year",
                "institution": "Stanford University",
                "email": "jane.doe@stanford.edu",
                "about_me": "Loves algorithms.",
                "preferences": '{"focus_subjects": ["Data Structures"], "study_hours": 127, "day_streak": 12}',
                "availability": '[]',
            }],
            [{"groups_joined": 4}],
        ]

        result = get_user_profile("user-uuid-1")

        self.assertEqual(result["study_hours"], 127)
        self.assertEqual(result["day_streak"], 12)
        self.assertEqual(result["groups_joined"], 4)

    @patch("data_fetcher._run_query")
    def test_returns_focus_subjects(self, mock_run_query):
        """Tests that focus_subjects is parsed from the preferences JSON field."""
        mock_run_query.side_effect = [
            [{
                "first_name": "Jane",
                "last_name": "Doe",
                "major": "Computer Science",
                "education_level": "Junior Year",
                "institution": "Stanford University",
                "email": "jane.doe@stanford.edu",
                "about_me": "",
                "preferences": '{"focus_subjects": ["Data Structures", "Machine Learning"], "study_hours": 0, "day_streak": 0}',
                "availability": '[]',
            }],
            [{"groups_joined": 2}],
        ]

        result = get_user_profile("user-uuid-1")

        self.assertIn("Data Structures", result["focus_subjects"])
        self.assertIn("Machine Learning", result["focus_subjects"])

    @patch("data_fetcher._run_query")
    def test_returns_none_when_user_not_found(self, mock_run_query):
        """Tests that get_user_profile returns None when no user matches the ID."""
        mock_run_query.side_effect = [
            [],  # no user row
        ]

        result = get_user_profile("nonexistent-id")

        self.assertIsNone(result)

    @patch("data_fetcher._run_query")
    def test_weekly_availability_is_a_list(self, mock_run_query):
        """Tests that weekly_availability is returned as a list of day/slot dicts."""
        mock_run_query.side_effect = [
            [{
                "first_name": "Jane",
                "last_name": "Doe",
                "major": "Computer Science",
                "education_level": "Junior Year",
                "institution": "Stanford University",
                "email": "jane.doe@stanford.edu",
                "about_me": "",
                "preferences": '{"focus_subjects": [], "study_hours": 0, "day_streak": 0}',
                "availability": '[{"day": "Mon", "slots": ["9-11 AM", "2-4 PM"]}, {"day": "Tue", "slots": ["1-3 PM"]}]',
            }],
            [{"groups_joined": 1}],
        ]

        result = get_user_profile("user-uuid-1")

        self.assertIsInstance(result["weekly_availability"], list)
        self.assertTrue(any(d["day"] == "Mon" for d in result["weekly_availability"]))

    @patch("data_fetcher._run_query")
    def test_handles_missing_preferences_gracefully(self, mock_run_query):
        """Tests that get_user_profile still returns a valid dict when preferences is None."""
        mock_run_query.side_effect = [
            [{
                "first_name": "Alex",
                "last_name": "Kim",
                "major": "Mathematics",
                "education_level": "Sophomore Year",
                "institution": "MIT",
                "email": "alex@mit.edu",
                "about_me": "",
                "preferences": None,
                "availability": None,
            }],
            [{"groups_joined": 0}],
        ]

        result = get_user_profile("user-uuid-2")

        self.assertEqual(result["focus_subjects"], [])
        self.assertEqual(result["weekly_availability"], [])
        self.assertEqual(result["study_hours"], 0)
        self.assertEqual(result["day_streak"], 0)


if __name__ == "__main__":
    unittest.main()