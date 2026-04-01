import unittest
from backend.app import normalize_metric
from backend.trips.services import _parse_date


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


class TestParseDateHelper(unittest.TestCase):
    def test_parse_date_formats(self):
        self.assertEqual(_parse_date('2026-03-31').isoformat(), '2026-03-31')
        self.assertEqual(_parse_date('08/02/2026').isoformat(), '2026-02-08')
        self.assertEqual(_parse_date('2026-03-31T12:30:00').isoformat(), '2026-03-31')
        self.assertEqual(_parse_date('2026-03-31 12:30:00').isoformat(), '2026-03-31')

    def test_parse_date_invalid(self):
        self.assertIsNone(_parse_date(None))
        self.assertIsNone(_parse_date('invalid-date'))


if __name__ == "__main__":
    unittest.main()
