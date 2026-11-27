import unittest

from experiments.linear_probe_comparison import measure_comparison


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


if __name__ == "__main__":
    unittest.main()
