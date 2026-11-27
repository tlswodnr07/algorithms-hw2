import unittest

from src.linear_probe_hash_table import LinearProbeHashTable


class LinearProbeHashTableTests(unittest.TestCase):
    def test_insert_lookup_update_and_resize(self):
        table = LinearProbeHashTable(initial_capacity=2)
        table["a"] = 1
        table["b"] = 2
        self.assertEqual(table["a"], 1)
        self.assertEqual(table["b"], 2)
        table["a"] = 3
        self.assertEqual(table["a"], 3)
        self.assertEqual(len(table), 2)
        self.assertGreater(table.capacity, 2)

    def test_resize_preserves_all_entries(self):
        table = LinearProbeHashTable(initial_capacity=2)
        for number in range(20):
            table[str(number)] = number
        self.assertGreater(table.capacity, 2)
        self.assertEqual(len(table), 20)
        for number in range(20):
            self.assertEqual(table[str(number)], number)

    def test_probe_wraps_from_last_slot_to_first(self):
        table = LinearProbeHashTable(initial_capacity=5, max_load_factor=None)
        candidates = [f"key-{number}" for number in range(100)]
        start = next(key for key in candidates if table._hash(key) == 4)
        second = next(
            key for key in candidates if key != start and table._hash(key) == 4
        )
        table[start] = "first"
        table[second] = "second"
        self.assertEqual(table._buckets[4][0], start)
        self.assertEqual(table._buckets[0][0], second)
        self.assertEqual(table.probe_trace(second), [4, 0])

    def test_full_fixed_table_raises_without_hanging(self):
        table = LinearProbeHashTable(initial_capacity=2, max_load_factor=None)
        table["a"] = 1
        table["b"] = 2
        self.assertEqual(len(table), 2)
        self.assertEqual(table.probe_trace("missing"), [0, 1])
        with self.assertRaises(KeyError):
            _ = table["missing"]
        with self.assertRaises(OverflowError):
            table["third"] = 3


if __name__ == "__main__":
    unittest.main()
