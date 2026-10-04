import tempfile
import unittest
from pathlib import Path

from mediap.doubly_linked_list import DoublyLinkedList
from mediap.models import Track
from mediap.player import MediaPlayer


def track(number, rating=4):
    return Track(number, f"Faixa {number}", "Artista", 125, rating, "2025-01-01")


class LinkedListTests(unittest.TestCase):
    def test_insert_cursor_navigation_and_remove(self):
        playlist = DoublyLinkedList()
        a, b, c = track(1), track(2), track(3)
        playlist.add(a)
        playlist.add(b)
        playlist.add(c)
        self.assertIs(playlist.current(), a)
        self.assertIs(playlist.play_next(), b)
        self.assertIs(playlist.play_prev(), a)
        self.assertIsNone(playlist.play_prev())
        self.assertIs(playlist.remove_at(0), a)
        self.assertIs(playlist.current(), b)
        self.assertEqual(list(playlist), [b, c])
        playlist.set_cursor(1)
        self.assertIs(playlist.current(), c)
        playlist.remove_at(1)
        self.assertIs(playlist.current(), b)

    def test_empty_and_invalid_positions(self):
        playlist = DoublyLinkedList()
        self.assertIsNone(playlist.current())
        with self.assertRaises(IndexError):
            playlist.remove_at(0)


class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.player = MediaPlayer()
        self.player.library = {i: track(i, 5 if i <= 3 else 3) for i in range(1, 7)}

    def test_up_next_precedes_playlist_without_advancing_cursor(self):
        self.player.create_playlist("teste")
        self.player.add_to_playlist(1)
        self.player.add_to_playlist(2)
        self.player.enqueue(5)
        self.assertEqual(self.player.next().id, 5)
        self.assertEqual(self.player.playlist.current().id, 1)
        self.assertEqual(self.player.next().id, 2)

    def test_history_discards_oldest_at_limit(self):
        for i in range(self.player.HISTORY_LIMIT + 2):
            self.player._record(self.player.library[1 + i % 6])
        self.assertEqual(len(self.player.history), self.player.HISTORY_LIMIT)

    def test_priority_queue_favors_rating_and_downgrades_recent(self):
        self.player._record(self.player.library[1])
        self.player.smart_shuffle(6)
        ids = [item.id for item in self.player.playlist]
        self.assertEqual(ids[:2], [2, 3])
        self.assertEqual(ids[-3:], [4, 5, 6])
        self.assertGreater(ids.index(1), ids.index(2))

    def test_state_save_restore_preserves_all_visible_state(self):
        self.player.create_playlist("persistente")
        for i in (1, 2, 3):
            self.player.add_to_playlist(i)
        self.player.playlist.play_next()
        self.player.enqueue(5)
        self.player._record(self.player.library[2])
        before = self.player.state_dict()
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "state.json"
            self.player.save(filename)
            restored = MediaPlayer()
            restored.library = self.player.library.copy()
            restored.restore(filename)
            self.assertEqual(restored.state_dict(), before)

    def test_library_json_load(self):
        library = Path(__file__).parent / "library.json"
        if not library.exists():
            library = library.parent / "mediap" / "library.json"
        self.assertEqual(self.player.load_library(library), 10)
        self.assertEqual(self.player.library[1].title, "Águas de Março")


if __name__ == "__main__":
    unittest.main()
