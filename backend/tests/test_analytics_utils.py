import unittest
from backend.app import normalize_metric


class TestAnalyticsNormalizeMetric(unittest.TestCase):
    def test_valid_numeric_values(self):
        self.assertEqual(normalize_metric(12.345, round_decimals=2), 12.35)
        self.assertEqual(normalize_metric("100"), 100.0)

    def test_invalid_value_returns_default(self):
        self.assertEqual(normalize_metric(None), 0.0)
        self.assertEqual(normalize_metric("abc", default=5), 5.0)

    def test_nan_and_inf_handled(self):
        self.assertEqual(normalize_metric(float("nan"), default=10), 10.0)
        self.assertEqual(normalize_metric(float("inf"), default=1), 1.0)
        self.assertEqual(normalize_metric(float("-inf"), default=1), 1.0)

    def test_min_max_boundaries(self):
        self.assertEqual(normalize_metric(5, min_value=10), 10)
        self.assertEqual(normalize_metric(20, max_value=15), 15)


if __name__ == "__main__":
    unittest.main()
