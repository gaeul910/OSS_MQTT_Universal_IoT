import unittest
from unittest.mock import patch, MagicMock
import set_of_request

class TestSetOfRequest(unittest.TestCase):
    def test_route_get_basic(self):
        self.assertEqual(set_of_request.route_get("37.1 127.1", ""), "37.1 127.1")
        self.assertEqual(set_of_request.route_get("37.1 127.1", "37.1 127.1"), "37.1 127.1")
        self.assertEqual(set_of_request.route_get("37.2 127.2", "37.1 127.1"), "37.1 127.1,37.2 127.2")

    @patch('set_of_request.r.post')
    @patch('set_of_request.token_get', return_value='token')
    def test_route_send(self, mock_token, mock_post):
        mock_post.return_value.text = "ok"
        result = set_of_request.route_send(1, "37.1 127.1", 10)
        self.assertEqual(result, "")
        mock_post.assert_called_once()
        mock_token.assert_called_once()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_route_exist_send_no_data(self, mock_token, mock_get):
        mock_get.return_value.text = 'No data found for startlocation_id: 10'
        with patch('set_of_request.route_send', return_value="called") as mock_route_send:
            result = set_of_request.route_exist_send(1, "37.1 127.1", 10)
            self.assertEqual(result, "called")
            mock_route_send.assert_called_once()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_route_exist_send_already_exists(self, mock_token, mock_get):
        mock_get.return_value.text = 'something else'
        result = set_of_request.route_exist_send(1, "37.1 127.1", 10)
        self.assertEqual(result, "루트 이미 있음")

    @patch('set_of_request.favorite_point_get', return_value=404)
    def test_favorite_point_post_empty(self, mock_fav_get):
        result = set_of_request.favorite_point_post([])
        self.assertEqual(result, "cluster_store가 비어 없다 처리 중단한다")

    @patch('set_of_request.favorite_point_get', return_value=404)
    @patch('set_of_request.r.post')
    @patch('set_of_request.token_get', return_value='token')
    def test_favorite_point_post_save(self, mock_token, mock_post, mock_fav_get):
        cluster_store = [{"uid": 1, "coordness": "37.1 127.1"}]
        result = set_of_request.favorite_point_post(cluster_store)
        self.assertEqual(result, "잘 저장됨")
        mock_post.assert_called_once()
        mock_token.assert_called()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_route_need_no_data(self, mock_token, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.return_value.text = 'No data found for startlocation_id: 10'
        result = set_of_request.route_need(10)
        self.assertEqual(result, "루트없음")

        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'No data found for startlocation_id: 10'
        result = set_of_request.route_need(10)
        self.assertEqual(result, "루트없음")

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_route_need_success(self, mock_token, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'something else'
        mock_get.return_value.json.return_value = [{"a": 1}]
        result = set_of_request.route_need(10)
        self.assertEqual(result, {"a": 1})

    def test_point_to_tuple(self):
        self.assertEqual(set_of_request.point_to_tuple("POINT(37.1 127.1)"), (37.1, 127.1))
        self.assertEqual(set_of_request.point_to_tuple("37.1 127.1"), (37.1, 127.1))

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_home_get(self, mock_token, mock_get):
        # 정상적으로 home 정보가 반환되는 경우
        mock_get.return_value.json.return_value = [{"uid": 1, "coordinate": "37.1 127.1"}]
        result = set_of_request.home_get(1)
        self.assertEqual(result, {"uid": 1, "coordinate": "37.1 127.1"})
        mock_get.assert_called_once()
        mock_token.assert_called_once()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_month_points_get(self, mock_token, mock_get):
        # 정상적으로 month_points 데이터가 반환되는 경우
        mock_get.return_value.json.return_value = [{"uid": 1, "coordinate": "37.1 127.1"}]
        result = set_of_request.month_points_get(1)
        self.assertEqual(result, [{"uid": 1, "coordinate": "37.1 127.1"}])
        mock_get.assert_called_once()
        mock_token.assert_called_once()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_point_get_success(self, mock_token, mock_get):
        # 정상적으로 좌표가 반환되는 경우
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"coordinate": "POINT(37.1 127.1)"}
        result = set_of_request.point_get(1)
        self.assertEqual(result, "37.1 127.1")
        mock_get.assert_called_once()
        mock_token.assert_called_once()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_point_get_error(self, mock_token, mock_get):
        # status_code != 200
        mock_get.return_value.status_code = 404
        result = set_of_request.point_get(1)
        self.assertEqual(result, "Error: Unable to fetch point data")
        mock_get.assert_called_once()
        mock_token.assert_called_once()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_uid_get(self, mock_token, mock_get):
        # 정상적으로 uid가 반환되는 경우
        mock_get.return_value.json.return_value = [{}, {"uid": 1234}]
        result = set_of_request.uid_get()
        self.assertEqual(result, 1234)
        mock_get.assert_called_once()
        mock_token.assert_called_once()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_favorite_point_get_success(self, mock_token, mock_get):
        # 정상적으로 포인트 정보가 반환되는 경우
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"uid": 1, "coordinate": "37.1 127.1"}]
        result = set_of_request.favorite_point_get(1)
        self.assertEqual(result, [{"uid": 1, "coordinate": "37.1 127.1"}])
        mock_get.assert_called_once()
        mock_token.assert_called_once()

    @patch('set_of_request.r.get')
    @patch('set_of_request.token_get', return_value='token')
    def test_favorite_point_get_error(self, mock_token, mock_get):
        # status_code != 200
        mock_get.return_value.status_code = 404
        result = set_of_request.favorite_point_get(1)
        self.assertEqual(result, 404)
        mock_get.assert_called_once()
        mock_token.assert_called_once()

if __name__ == "__main__":
    unittest.main()
