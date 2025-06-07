import unittest
from default_control import control
from unittest.mock import patch

class TestControl(unittest.TestCase):
    @patch('default_control.RR.uid_get', return_value="test_uid")
    @patch('default_control.PR.range')
    def test_home_in_near(self, mock_range, mock_uid):
        c = control()
        c.home_point = "0 0"
        c.now_point = "0 0"
        mock_range.return_value = 100  # 500m 미만
        result = c.home_in()
        self.assertEqual(result, "곧 집에 들어옴")
        self.assertEqual(c.level, 1)

    @patch('default_control.RR.uid_get', return_value="test_uid")
    @patch('default_control.PR.range')
    def test_home_in_far(self, mock_range, mock_uid):
        c = control()
        c.home_point = "0 0"
        c.now_point = "1 1"
        mock_range.return_value = 1000  # 500m 이상
        result = c.home_in()
        self.assertEqual(result, "아직 아님")
        self.assertNotEqual(c.level, 1)

    @patch('default_control.RR.uid_get', return_value="test_uid")
    @patch('default_control.PR.range')
    def test_home_out_outside(self, mock_range, mock_uid):
        c = control()
        c.home_point = "0 0"
        c.now_point = "1 1"
        mock_range.return_value = 600  # 500m 이상
        result = c.home_out()
        self.assertEqual(result, "집을 나감")
        self.assertEqual(c.level, 0)

    @patch('default_control.RR.uid_get', return_value="test_uid")
    @patch('default_control.PR.range')
    def test_home_out_inside(self, mock_range, mock_uid):
        c = control()
        c.home_point = "0 0"
        c.now_point = "0 0"
        mock_range.return_value = 100  # 500m 미만
        result = c.home_out()
        self.assertEqual(result, "집을 안나감")
        self.assertEqual(c.level, 0)

    # get 함수 테스트 추가
    @patch('default_control.PR.range', return_value=50)
    @patch('default_control.RR.favorite_point_get', return_value=[
        {"coordinate": "0 0"},
        {"coordinate": "1 1", "id": 123}
    ])
    @patch('default_control.RR.point_get', return_value="0 0")
    @patch('default_control.RR.home_get', return_value={"coordinate": "0 0"})
    @patch('default_control.RR.uid_get', return_value="test_uid")
    def test_get_arrive_at_favorite(self, mock_uid, mock_home, mock_point, mock_fav, mock_range):
        c = control()
        c.get()
        self.assertEqual(c.event, "특정 장소 도착")
        self.assertEqual(c.event_id, 123)

    @patch('default_control.RR.favorite_point_get', return_value=[])
    @patch('default_control.RR.point_get', return_value="0 0")
    @patch('default_control.RR.home_get', return_value={"coordinate": "0 0"})
    @patch('default_control.RR.uid_get', return_value="test_uid")
    def test_get_no_favorite(self, mock_uid, mock_home, mock_point, mock_fav):
        c = control()
        result = c.get()
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()