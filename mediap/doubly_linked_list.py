class _Node:
    __slots__ = ("value", "prev", "next")

    def __init__(self, value=None, prev=None, next_node=None):
        self.value = value
        self.prev = prev
        self.next = next_node


class DoublyLinkedList:
    """Lista duplamente encadeada com cursor de execução."""

    def __init__(self):
        self._head = _Node()
        self._tail = _Node()
        self._head.next = self._tail
        self._tail.prev = self._head
        self._cursor = None
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        node = self._head.next
        while node is not self._tail:
            yield node.value
            node = node.next

    def _node_at(self, pos):
        if not 0 <= pos < self._size:
            raise IndexError("Posição fora dos limites da playlist.")
        if pos < self._size // 2:
            node = self._head.next
            for _ in range(pos):
                node = node.next
        else:
            node = self._tail.prev
            for _ in range(self._size - pos - 1):
                node = node.prev
        return node

    def add(self, track):
        node = _Node(track, self._tail.prev, self._tail)
        self._tail.prev.next = node
        self._tail.prev = node
        self._size += 1
        if self._cursor is None:
            self._cursor = node

    def remove_at(self, pos):
        node = self._node_at(pos)
        if node is self._cursor:
            self._cursor = node.next if node.next is not self._tail else (
                node.prev if node.prev is not self._head else None
            )
        node.prev.next = node.next
        node.next.prev = node.prev
        self._size -= 1
        return node.value

    def current(self):
        return None if self._cursor is None else self._cursor.value

    def play_next(self):
        if self._cursor is None or self._cursor.next is self._tail:
            return None
        self._cursor = self._cursor.next
        return self._cursor.value

    def play_prev(self):
        if self._cursor is None or self._cursor.prev is self._head:
            return None
        self._cursor = self._cursor.prev
        return self._cursor.value

    def reset_cursor(self):
        self._cursor = self._head.next if self._size else None
        return self.current()

    def cursor_index(self):
        if self._cursor is None:
            return 0
        node = self._head.next
        pos = 0
        while node is not self._tail:
            if node is self._cursor:
                return pos
            node = node.next
            pos += 1
        return 0

    def set_cursor(self, pos):
        self._cursor = self._node_at(pos) if self._size else None

    def clear(self):
        self._head.next = self._tail
        self._tail.prev = self._head
        self._cursor = None
        self._size = 0
