import unittest

from experiments.probe_experiment import measure


class ProbeExperimentTests(unittest.TestCase):
    def test_single_bucket_matches_chaining_cost_formulas(self):
        self.assertEqual(measure(1, capacity=1), (1.0, 1.0))
        self.assertEqual(measure(2, capacity=1), (1.5, 2.0))

    def test_rejects_non_positive_inputs(self):
        with self.assertRaises(ValueError):
            measure(0)
        with self.assertRaises(ValueError):
            measure(1, capacity=0)


if __name__ == "__main__":
    unittest.main()
