#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest

class TestDataFetcher(unittest.TestCase):

    def test_foo(self):
        """Tests foo."""
        pass
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