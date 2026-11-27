"""A separate-chaining hash table with a deterministic Horner hash."""

from typing import Generic, Iterator, TypeVar


_Value = TypeVar("_Value")


class _Node(Generic[_Value]):
    __slots__ = ("key", "value", "next")

    def __init__(self, key: str, value: _Value, next_node: "_Node[_Value] | None" = None):
        self.key = key
        self.value = value
        self.next = next_node


class HashTable(Generic[_Value]):
    def __init__(self, initial_capacity: int = 8):
        if not isinstance(initial_capacity, int) or isinstance(initial_capacity, bool):
            raise TypeError("initial_capacity must be an integer")
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be positive")
        self._buckets: list[_Node[_Value] | None] = [None] * initial_capacity
        self._size = 0

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def buckets(self) -> list[_Node[_Value] | None]:
        return self._buckets

    def _hash(self, key: str, capacity: int | None = None) -> int:
        if not isinstance(key, str):
            raise TypeError("keys must be strings")
        modulus = self.capacity if capacity is None else capacity
        value = 0
        for character in key:
            value = (value * 31 + ord(character)) % modulus
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
        node = self._buckets[self._hash(key)]
        while node is not None:
            if node.key == key:
                return True
            node = node.next
        return False

    def __getitem__(self, key: str) -> _Value:
        node = self._buckets[self._hash(key)]
        while node is not None:
            if node.key == key:
                return node.value
            node = node.next
        raise KeyError(key)

    def __setitem__(self, key: str, value: _Value) -> None:
        index = self._hash(key)
        node = self._buckets[index]
        while node is not None:
            if node.key == key:
                node.value = value
                return
            node = node.next

        self._buckets[index] = _Node(key, value, self._buckets[index])
        self._size += 1
        if self._size / self.capacity > 0.75:
            self._resize(self.capacity * 2)

    def get(self, key: str, default: _Value | None = None) -> _Value | None:
        try:
            return self[key]
        except KeyError:
            return default

    def items(self) -> Iterator[tuple[str, _Value]]:
        for node in self._buckets:
            while node is not None:
                yield node.key, node.value
                node = node.next

    def _resize(self, new_capacity: int) -> None:
        old_buckets = self._buckets
        self._buckets = [None] * new_capacity
        for head in old_buckets:
            node = head
            while node is not None:
                next_node = node.next
                index = self._hash(node.key, new_capacity)
                node.next = self._buckets[index]
                self._buckets[index] = node
                node = next_node
