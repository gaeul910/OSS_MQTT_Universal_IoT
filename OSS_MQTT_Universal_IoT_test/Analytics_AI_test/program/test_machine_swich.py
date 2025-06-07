import unittest
from unittest.mock import patch, MagicMock
from machine_swich import switch, machine_status

class TestMachineSwich(unittest.TestCase):
    @patch('machine_swich.r.post')
    @patch('machine_swich.machine_status')
    def test_switch_on(self, mock_machine_status, mock_post):
        # 머신 상태: dev001은 꺼짐(0), dev002는 켜짐(1)
        mock_machine_status.return_value = ["dev001 0", "dev002 1"]
        mock_post.return_value.status_code = 200
        uid = "test_uid"
        result = switch(True, uid)
        self.assertEqual(result, "OK")
        self.assertTrue(mock_post.called)
        # dev001만 켜짐 알림이 가야 함
        called_data = [call.kwargs['data'] for call in mock_post.mock_calls if 'data' in call.kwargs]
        self.assertTrue(any("꺼져있던 머신 켜짐" in d for d in called_data))

    @patch('machine_swich.r.post')
    @patch('machine_swich.machine_status')
    def test_switch_off(self, mock_machine_status, mock_post):
        # 머신 상태: dev001은 꺼짐(0), dev002는 켜짐(1)
        mock_machine_status.return_value = ["dev001 0", "dev002 1"]
        mock_post.return_value.status_code = 200
        uid = "test_uid"
        result = switch(False, uid)
        self.assertEqual(result, "OK")
        self.assertTrue(mock_post.called)
        # dev002만 꺼짐 알림이 가야 함
        called_data = [call.kwargs['data'] for call in mock_post.mock_calls if 'data' in call.kwargs]
        self.assertTrue(any("켜져있던 머신 꺼짐" in d for d in called_data))

    @patch('machine_swich.r.get')
    def test_machine_status_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "stats": [
                "dev001 0",
                "dev002 1"
            ]
        }
        mock_get.return_value = mock_response
        result = machine_status()
        self.assertEqual(result, ["dev001 0", "dev002 1"])

    @patch('machine_swich.r.get')
    def test_machine_status_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        result = machine_status()
        self.assertEqual(result, "머신정보없음")

if __name__ == "__main__":
    unittest.main()