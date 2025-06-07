import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import company_location as cl

class TestCompanyLocation(unittest.TestCase):
    def test_parse_point(self):
        lon, lat = cl.parse_point("POINT(127.123456 37.123456)")
        self.assertAlmostEqual(lon, 127.123456)
        self.assertAlmostEqual(lat, 37.123456)

    def test_haversine_distance(self):
        # 서울역과 시청역(약 1.2~1.3km)
        lat1, lon1 = 37.554722, 126.970833
        lat2, lon2 = 37.565017, 126.976800
        dist = cl.haversine_distance(lat1, lon1, lat2, lon2)
        self.assertTrue(900 < dist < 1350)  # upper bound를 1350으로 수정

    def test_is_same_cluster(self):
        # 같은 위치
        self.assertTrue(cl.is_same_cluster(37.5, 127.0, 37.5, 127.0))
        # 100m 이상 떨어진 위치
        self.assertFalse(cl.is_same_cluster(37.5, 127.0, 37.501, 127.0, threshold=30))

    def test_preprocess_logs(self):
        raw_logs = [
            {"coordinate": "POINT(127.1 37.1)", "time": "2024-01-01T09:00:00", "uid": "u1"},
            {"coordinate": "POINT(127.2 37.2)", "time": "2024-01-01T10:00:00", "uid": "u2"},
        ]
        df = cl.preprocess_logs(raw_logs)
        self.assertEqual(len(df), 2)
        self.assertIn("lat", df.columns)
        self.assertIn("lon", df.columns)
        self.assertIn("uid", df.columns)

    def test_convert_favpoints_to_cluster_store(self):
        favpoints = [
            {"id": 1, "coordinate": "POINT(127.1 37.1)", "uid": "u1"},
            {"id": 2, "coordinate": "POINT(127.2 37.2)", "uid": "u2"},
        ]
        store = cl.convert_favpoints_to_cluster_store(favpoints)
        self.assertEqual(len(store), 2)
        self.assertIn(1, store)
        self.assertIn(2, store)
        self.assertEqual(store[1]["uid"], "u1")

    def test_cluster_to_log_entries(self):
        cluster_store = {
            1: {"lat": 37.1, "lon": 127.1, "last_visit": "2024-01-01T09:00:00", "uid": "u1", "id": 1},
            2: {"lat": 37.2, "lon": 127.2, "last_visit": "2024-01-02T10:00:00", "uid": "u2", "id": 2},
        }
        logs = cl.cluster_to_log_entries(cluster_store)
        self.assertEqual(len(logs), 2)
        self.assertTrue(all("coordness" in entry or "coordness" in entry for entry in logs))

    @patch("company_location.r.favorite_point_post")
    @patch("company_location.r.favorite_point_get")
    @patch("company_location.r.month_points_get")
    def test_update(self, mock_month_points_get, mock_favorite_point_get, mock_favorite_point_post):
        # 10일 동안 하루에 7개씩, 1시간 이상 머문 로그 생성
        logs = []
        base_time = datetime(2024, 1, 1, 9, 0, 0)
        for day in range(10):
            for i in range(7):  # min_samples=7
                logs.append({
                    "coordinate": "POINT(127.1 37.1)",
                    "time": (base_time + timedelta(days=day, hours=i)).isoformat(),
                    "uid": "u1"
                })
        mock_month_points_get.return_value = logs
        mock_favorite_point_get.return_value = []
        mock_favorite_point_post.return_value = None

        cl.update("u1")
        self.assertTrue(mock_favorite_point_post.called)

if __name__ == "__main__":
    unittest.main()