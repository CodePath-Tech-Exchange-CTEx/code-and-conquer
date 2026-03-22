import unittest
from unittest.mock import patch, MagicMock
from data_fetcher_gen_ai import get_study_group_recommendations

class TestDataFetcher(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def test_get_study_group_recommendations(self, mock_bq_client):
        
        class DummyRow:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs) # kwargs: take any number of keyword arguments and bundle them into a dictionary

        dummy_results = [
            DummyRow(
                group_id="group_123",
                subject="COMPUTER SCIENCE",
                group_name="GenAI & Systems Design",
                match_pct=0.98,               
                features=["Algorithms", "Python"],
                day_of_week="Tuesday",
                start_time="5:00 PM",
                location_text="Fisk Library",
                current_members=3,
                capacity=5
            )
        ]

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = dummy_results
        
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = mock_query_job
        mock_bq_client.return_value = mock_client_instance


        result = get_study_group_recommendations("user_99")

        
        self.assertEqual(len(result), 1)
        
        self.assertEqual(result[0]["match_pct"], 98)
        
        self.assertEqual(result[0]["time"], "Tuesdays 5:00 PM")
        
        self.assertEqual(result[0]["members"], "3/5")
        
        self.assertEqual(result[0]["title"], "GenAI & Systems Design")
        self.assertEqual(result[0]["major"], "COMPUTER SCIENCE")
        self.assertEqual(result[0]["location"], "Fisk Library")
        self.assertEqual(result[0]["keywords"], ["Algorithms", "Python"])

if __name__ == "__main__":
    unittest.main()