import unittest

from src.hash_table import HashTable


class HashTableTests(unittest.TestCase):
    def test_empty_table_and_missing_key(self):
        table = HashTable()
        self.assertEqual(len(table), 0)
        self.assertNotIn("missing", table)
        self.assertEqual(table.get("missing", 42), 42)
        with self.assertRaises(KeyError):
            _ = table["missing"]

    def test_insert_update_and_lookup_colliding_keys(self):
        table = HashTable(initial_capacity=4)
        first = "a"
        second = "e"
        self.assertEqual(table._hash(first), table._hash(second))
        table[first] = 1
        table[second] = 2
        self.assertEqual(table[first], 1)
        self.assertEqual(table[second], 2)
        table[first] = 3
        self.assertEqual(table[first], 3)
        self.assertEqual(len(table), 2)
        self.assertIn(second, table)

    def test_resizes_without_losing_entries(self):
        table = HashTable(initial_capacity=2)
        for number in range(20):
            table[str(number)] = number
        self.assertGreater(table.capacity, 2)
        self.assertEqual(len(table), 20)
        for number in range(20):
            self.assertEqual(table[str(number)], number)


if __name__ == "__main__":
    unittest.main()
