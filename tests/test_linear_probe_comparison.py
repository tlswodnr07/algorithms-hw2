import csv
import tempfile
import unittest
from pathlib import Path

from experiments.linear_probe_comparison import (
    CSV_COLUMNS,
    _theory,
    _write_csv,
    measure_comparison,
)


class LinearProbeComparisonTests(unittest.TestCase):
    def test_same_keys_show_increasing_unsuccessful_cost_at_high_load(self):
        low_load = measure_comparison(0.2, capacity=101)
        high_load = measure_comparison(0.8, capacity=101)
        self.assertEqual(len(low_load), 4)
        self.assertEqual(len(high_load), 4)
        self.assertLess(high_load[3], 101)
        self.assertGreater(high_load[3], low_load[3])

    def test_rejects_load_factors_outside_open_unit_interval(self):
        for alpha in (0, 1, 1.1):
            with self.subTest(alpha=alpha):
                with self.assertRaises(ValueError):
                    measure_comparison(alpha)

    def test_csv_rows_preserve_the_measured_and_theoretical_results(self):
        alpha = 0.2
        results = [(alpha, *measure_comparison(alpha, capacity=101), *_theory(alpha))]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results.csv"
            _write_csv(results, output)
            with output.open(encoding="utf-8", newline="") as csv_file:
                rows = list(csv.reader(csv_file))

        self.assertEqual(tuple(rows[0]), CSV_COLUMNS)
        self.assertEqual([float(value) for value in rows[1]], list(results[0]))


if __name__ == "__main__":
    unittest.main()
