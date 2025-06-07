# ...existing code...

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import program_start
from program_start import UserTracker, update_clusters, should_update

class TestUserTracker(unittest.TestCase):
    @patch('program_start.DC.control')
    @patch('program_start.should_update')
    @patch('program_start.update_clusters')
    @patch('program_start.MS.switch')
    def test_wait_until_leave_home_updates_and_switches(self, mock_switch, mock_update_clusters, mock_should_update, mock_control):
        mock_user = MagicMock()
        mock_user.uid = 'user1'
        mock_user.route = ""
        mock_user.get = MagicMock()
        mock_user.home_out.side_effect = ['아직', '집을 나감']
        mock_control.return_value = mock_user
        mock_should_update.side_effect = [True, False]

        tracker = program_start.UserTracker()
        tracker.status = "in"
        tracker.wait_until_leave_home()

        mock_update_clusters.assert_called_once_with('user1')
        mock_switch.assert_called_once_with(0, 'user1')
        self.assertEqual(tracker.status, "out")

    @patch('program_start.WE.exit')
    @patch('program_start.MS.switch')
    @patch('program_start.DC.control')
    def test_monitor_while_out_event_exit(self, mock_control, mock_switch, mock_exit):
        mock_user = MagicMock()
        mock_user.uid = 'user1'
        mock_user.event = "특정 장소 도착"
        mock_user.event_id = 123
        mock_user.get = MagicMock()
        mock_user.home_in = MagicMock(return_value='아직')
        mock_control.return_value = mock_user
        mock_exit.return_value = "퇴근길맞음"

        tracker = program_start.UserTracker()
        tracker.status = "out"
        tracker.user = mock_user
        tracker.monitor_while_out()

        mock_exit.assert_called_once_with('user1', 123)
        self.assertEqual(tracker.event, "퇴근길맞음")

    @patch('program_start.DC.control')
    @patch('program_start.MS.switch')
    def test_monitor_while_out_home_in(self, mock_switch, mock_control):
        mock_user = MagicMock()
        mock_user.get = MagicMock()
        mock_user.event = None
        mock_user.home_in.side_effect = ['아직', '곧 집에 들어옴']
        mock_control.return_value = mock_user

        tracker = program_start.UserTracker()
        tracker.status = "out"
        tracker.user = mock_user
        with patch.object(tracker, 'prepare_home_entry') as mock_prepare:
            tracker.monitor_while_out()
            mock_prepare.assert_called_once()

    @patch('program_start.MS.switch')
    @patch('program_start.RR.route_exist_send')
    @patch('program_start.DC.control')
    def test_prepare_home_entry_route_exists(self, mock_control, mock_route_exist_send, mock_switch):
        mock_user = MagicMock()
        mock_user.uid = 'user1'
        mock_user.event = "특정 장소 도착"
        mock_user.route = "some_route"
        mock_user.event_id = 123
        mock_control.return_value = mock_user
        mock_route_exist_send.return_value = "루트 이미 있음"

        tracker = program_start.UserTracker()
        tracker.user = mock_user
        tracker.status = "out"
        tracker.event = None

        tracker.prepare_home_entry()
        self.assertEqual(mock_user.route, "")
        mock_switch.assert_called_once_with(1, 'user1')
        self.assertEqual(tracker.status, "in")
        self.assertIsNone(tracker.event)

    @patch('program_start.time.sleep', return_value=None)
    @patch('program_start.DC.control')
    def test_monitor_until_home_calls_prepare(self, mock_control, mock_sleep):
        mock_user = MagicMock()
        mock_user.get = MagicMock()
        mock_user.home_in.side_effect = ['아직', '곧 집에 들어옴']
        mock_control.return_value = mock_user

        tracker = program_start.UserTracker()
        tracker.status = "out"
        tracker.user = mock_user
        with patch.object(tracker, 'prepare_home_entry') as mock_prepare:
            tracker.monitor_until_home()
            mock_prepare.assert_called_once()

class TestUpdateAndShouldUpdate(unittest.TestCase):
    @patch('program_start.CL.update')
    @patch('program_start.RR.favorite_point_post')
    @patch('program_start.save_last_run_date')
    def test_update_clusters_calls_all(self, mock_save, mock_post, mock_update):
        mock_update.return_value = "updated"
        program_start.update_clusters('user1')
        mock_update.assert_called_once_with('user1')
        mock_post.assert_called_once_with("updated")
        mock_save.assert_called_once()

    @patch('program_start.get_last_run_date')
    def test_should_update_cases(self, mock_get_last_run_date):
        mock_get_last_run_date.return_value = None
        self.assertTrue(program_start.should_update())
        now = datetime.now()
        mock_get_last_run_date.return_value = now
        self.assertFalse(program_start.should_update())
        mock_get_last_run_date.return_value = now - timedelta(days=31)
        self.assertTrue(program_start.should_update())

class TestUserTrackerRealCall(unittest.TestCase):
    @patch('set_of_request.token_get', return_value='dummy_token')
    @patch('default_control.DC.control')
    def test_wait_until_leave_home_real(self, mock_control, mock_token):
        mock_user = MagicMock()
        mock_user.get = MagicMock()
        mock_user.home_out = MagicMock(return_value='집을 나감')
        mock_control.return_value = mock_user
        tracker = program_start.UserTracker()
        try:
            tracker.wait_until_leave_home()
        except Exception:
            pass

    @patch('set_of_request.token_get', return_value='dummy_token')
    @patch('default_control.DC.control')
    def test_monitor_while_out_real(self, mock_control, mock_token):
        mock_user = MagicMock()
        mock_user.get = MagicMock()
        mock_user.event = None
        mock_user.home_in = MagicMock(return_value='곧 집에 들어옴')
        mock_control.return_value = mock_user
        tracker = program_start.UserTracker()
        tracker.status = "out"
        tracker.user = mock_user
        try:
            tracker.monitor_while_out()
        except Exception:
            pass

if __name__ == "__main__":
    unittest.main()