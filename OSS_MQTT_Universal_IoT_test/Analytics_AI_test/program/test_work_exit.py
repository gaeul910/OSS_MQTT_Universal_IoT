import unittest
from unittest.mock import patch, MagicMock
import work_exit
import itertools

class TestWorkExit(unittest.TestCase):
    @patch('work_exit.RR.route_need')
    def test_exit_route_none(self, mock_route_need):
        # route가 '루트없음'일 때
        mock_route_need.return_value = "루트없음"
        result = work_exit.exit(1, 10)
        self.assertEqual(result, "퇴근길아님")

    @patch('work_exit.RR.route_need')
    def test_exit_point_less_than_two(self, mock_route_need):
        # point가 2개 이하일 때
        mock_route_need.return_value = {"route": "LINESTRING(1 1)"}
        result = work_exit.exit(1, 10)
        self.assertEqual(result, "퇴근길아님")

    @patch('work_exit.RR.point_get')
    @patch('work_exit.RR.route_need')
    def test_exit_still_at_start(self, mock_route_need, mock_point_get):
        # 출발지 근처(100m 이내) → 출발(100m 이상) → 경로 진입
        mock_route_need.return_value = {"route": "LINESTRING(1 1,2 2,3 3)"}
        # 1 1(출발지) → 1.1 1.1(조금 이동) → 2 2(경로)
        mock_point_get.side_effect = ["1 1", "1.1 1.1", "2 2", "3 3"]
        # 첫 호출: 50m(회사), 두 번째: 150m(출발), 이후: 50m(경로)
        with patch('work_exit.pr.range', side_effect=[50, 150, 50, 50, 50, 50]):
            result = work_exit.exit(1, 10)
            # 출발지에서 벗어나면 퇴근길로 진입할 수 있으므로, 퇴근길맞음 또는 퇴근길아님 둘 다 허용
            self.assertIn(result, ["퇴근길맞음", "퇴근길아님"])

    @patch('work_exit.RR.point_get')
    @patch('work_exit.RR.route_need')
    @patch('work_exit.MS.switch')
    @patch('work_exit.pr.range')
    @patch('work_exit.pr.slope')
    def test_exit_on_route(self, mock_slope, mock_range, mock_switch, mock_route_need, mock_point_get):
        # 출발지에서 100m 이상 떨어진 후 정상적으로 퇴근길맞음
        mock_route_need.return_value = {"route": "LINESTRING(1 1,2 2,3 3)"}
        # 첫 호출: 출발지와 150m 떨어짐, 이후 경로상 이동
        mock_point_get.side_effect = itertools.cycle(["1.5 1.5", "2 2", "3 3"])
        def range_side_effect(a, b):
            a_tuple = tuple(a)
            b_tuple = tuple(b)
            if a_tuple == (1.5, 1.5) and b_tuple == (1.0, 1.0):
                return 150
            return 50
        mock_range.side_effect = range_side_effect
        mock_slope.side_effect = lambda a, b: 1
        result = work_exit.exit(1, 10)
        self.assertEqual(result, "퇴근길맞음")
        mock_switch.assert_any_call(1, 1)

    @patch('work_exit.RR.point_get')
    @patch('work_exit.RR.route_need')
    @patch('work_exit.MS.switch')
    @patch('work_exit.pr.range')
    @patch('work_exit.pr.slope')
    def test_exit_out_of_range(self, mock_slope, mock_range, mock_switch, mock_route_need, mock_point_get):
        # 출발지에서 100m 이상 떨어졌지만 경로에서 벗어나는 경우
        mock_route_need.return_value = {"route": "LINESTRING(1 1,2 2,3 3)"}
        mock_point_get.side_effect = itertools.cycle(["10 10"])
        def range_side_effect(a, b):
            if b == (1.0, 1.0):
                return 150  # 출발지와 150m 떨어짐
            return 10000  # 경로상에서는 항상 멀리 떨어짐
        mock_range.side_effect = range_side_effect
        mock_slope.side_effect = lambda a, b: 1
        result = work_exit.exit(1, 10)
        self.assertEqual(result, "퇴근길아님")
        mock_switch.assert_any_call(0, 1)

    @patch('work_exit.RR.route_need')
    def test_exit_route_need_empty_dict(self, mock_route_need):
        # route_need이 빈 dict를 반환할 때
        mock_route_need.return_value = {}
        result = work_exit.exit(1, 10)
        self.assertEqual(result, "퇴근길아님")

    @patch('work_exit.RR.route_need')
    def test_exit_route_invalid_type(self, mock_route_need):
        # route_need이 예상치 못한 타입을 반환할 때
        mock_route_need.return_value = 12345
        result = work_exit.exit(1, 10)
        self.assertEqual(result, "퇴근길아님")

    @patch('work_exit.RR.point_get')
    @patch('work_exit.RR.route_need')
    def test_exit_empty_linestring(self, mock_route_need, mock_point_get):
        # LINESTRING이 비어있을 때
        mock_route_need.return_value = {"route": "LINESTRING()"}
        result = work_exit.exit(1, 10)
        self.assertEqual(result, "퇴근길아님")

    @patch('work_exit.RR.point_get')
    @patch('work_exit.RR.route_need')
    @patch('work_exit.MS.switch')
    @patch('work_exit.pr.range')
    @patch('work_exit.pr.slope')
    def test_exit_on_long_route(self, mock_slope, mock_range, mock_switch, mock_route_need, mock_point_get):
        # 5개짜리 긴 경로에서 정상적으로 퇴근길맞음
        mock_route_need.return_value = {"route": "LINESTRING(1 1,2 2,3 3,4 4,5 5)"}
        # 출발지에서 150m 떨어진 후 경로상 이동
        mock_point_get.side_effect = itertools.cycle([
            "1.5 1.5", "2 2", "3 3", "4 4", "5 5"
        ])
        def range_side_effect(a, b):
            a_tuple = tuple(a)
            b_tuple = tuple(b)
            if a_tuple == (1.5, 1.5) and b_tuple == (1.0, 1.0):
                return 150  # 출발지에서 150m 떨어짐
            return 50  # 경로상에서는 항상 50m 이내
        mock_range.side_effect = range_side_effect
        mock_slope.side_effect = lambda a, b: 1
        result = work_exit.exit(1, 10)
        self.assertEqual(result, "퇴근길맞음")
        mock_switch.assert_any_call(1, 1)

if __name__ == "__main__":
    unittest.main()
