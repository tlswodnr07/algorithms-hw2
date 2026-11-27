"""A fixed-array hash table using linear probing."""

from typing import Generic, Iterator, TypeVar


_Value = TypeVar("_Value")


class LinearProbeHashTable(Generic[_Value]):
    def __init__(
        self, initial_capacity: int = 8, max_load_factor: float | None = 0.75
    ):
        if not isinstance(initial_capacity, int) or isinstance(initial_capacity, bool):
            raise TypeError("initial_capacity must be an integer")
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be positive")
        if max_load_factor is not None and max_load_factor <= 0:
            raise ValueError("max_load_factor must be positive or None")
        self._buckets: list[tuple[str, _Value] | None] = [None] * initial_capacity
        self._size = 0
        self._max_load_factor = max_load_factor

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def buckets(self) -> list[tuple[str, _Value] | None]:
        return self._buckets

    def _hash(self, key: str) -> int:
        if not isinstance(key, str):
            raise TypeError("keys must be strings")
        value = 0
        for character in key:
            value = (value * 31 + ord(character)) % self.capacity
        return value

    def hash_trace(self, key: str) -> list[tuple[str, int]]:
        if not isinstance(key, str):
            raise TypeError("keys must be strings")
        value = 0
        trace = []
        for character in key:
            value = (value * 31 + ord(character)) % self.capacity
            trace.append((character, value))
        return trace

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return self._find_index(key) is not None

    def __getitem__(self, key: str) -> _Value:
        index = self._find_index(key)
        if index is None:
            raise KeyError(key)
        entry = self._buckets[index]
        if entry is None:
            raise KeyError(key)
        return entry[1]

    def __setitem__(self, key: str, value: _Value) -> None:
        start = self._hash(key)
        for offset in range(self.capacity):
            index = (start + offset) % self.capacity
            entry = self._buckets[index]
            if entry is None:
                self._buckets[index] = (key, value)
                self._size += 1
                if (
                    self._max_load_factor is not None
                    and self._size / self.capacity > self._max_load_factor
                ):
                    self._resize(self.capacity * 2)
                return
            if entry[0] == key:
                self._buckets[index] = (key, value)
                return
        raise OverflowError("hash table is full")

    def get(self, key: str, default: _Value | None = None) -> _Value | None:
        try:
            return self[key]
        except KeyError:
            return default

    def items(self) -> Iterator[tuple[str, _Value]]:
        for entry in self._buckets:
            if entry is not None:
                yield entry

    def bucket_entries(self, index: int) -> Iterator[tuple[str, _Value]]:
        entry = self._buckets[index]
        if entry is not None:
            yield entry

    def probe_trace(self, key: str) -> list[int]:
        start = self._hash(key)
        probes = []
        for offset in range(self.capacity):
            index = (start + offset) % self.capacity
            probes.append(index)
            entry = self._buckets[index]
            if entry is None or entry[0] == key:
                break
        return probes

    def _find_index(self, key: str) -> int | None:
        start = self._hash(key)
        for offset in range(self.capacity):
            index = (start + offset) % self.capacity
            entry = self._buckets[index]
            if entry is None:
                return None
            if entry[0] == key:
                return index
        return None

    def _resize(self, new_capacity: int) -> None:
        old_buckets = self._buckets
        self._buckets = [None] * new_capacity
        self._size = 0
        for entry in old_buckets:
            if entry is not None:
                self[entry[0]] = entry[1]
