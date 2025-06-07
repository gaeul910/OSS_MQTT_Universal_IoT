import unittest
from point_range import range, slope

class TestPointRange(unittest.TestCase):
    def test_range_same_point(self):
        self.assertAlmostEqual(range((0, 0), (0, 0)), 0, places=5)

    def test_range_one_degree_latitude(self):
        result = range((0, 0), (0, 1))
        self.assertAlmostEqual(result, 111195, delta=1000)

    def test_range_one_degree_longitude_equator(self):
        result = range((0, 0), (1, 0))
        self.assertAlmostEqual(result, 111195, delta=1000)

    def test_range_seoul_busan(self):
        # Seoul: (126.9780, 37.5665), Busan: (129.0756, 35.1796)
        result = range((126.9780, 37.5665), (129.0756, 35.1796))
        self.assertAlmostEqual(result, 325000, delta=10000)

    def test_slope_same_point(self):
        self.assertEqual(slope((0, 0), (0, 0)), 0)

    def test_slope_vertical(self):
        self.assertEqual(slope((1, 1), (1, 5)), 0)

    def test_slope_horizontal(self):
        self.assertEqual(slope((1, 2), (4, 2)), (2-2)-(4-1))

    def test_slope_general(self):
        self.assertEqual(slope((1, 2), (4, 6)), (6-2)-(4-1))

if __name__ == "__main__":
    unittest.main()