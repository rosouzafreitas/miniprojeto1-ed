import csv
import json
from collections import deque
from datetime import datetime
from pathlib import Path
from queue import PriorityQueue

from .doubly_linked_list import DoublyLinkedList
from .models import Track


class MediaPlayer:
    HISTORY_LIMIT = 20

    def __init__(self):
        self.library = {}
        self.playlist = DoublyLinkedList()
        self.playlist_name = None
        self.up_next = deque()
        self.history = deque(maxlen=self.HISTORY_LIMIT)
        self.current_track = None

    def load_library(self, filename):
        path = Path(filename)
        try:
            if path.suffix.lower() == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix.lower() == ".csv":
                with path.open(encoding="utf-8-sig", newline="") as stream:
                    data = list(csv.DictReader(stream))
            else:
                raise ValueError("Use um arquivo .json ou .csv.")
            tracks = [Track.from_dict(item) for item in data]
        except (OSError, json.JSONDecodeError, csv.Error) as exc:
            raise ValueError(f"Não foi possível ler a biblioteca: {exc}") from exc
        if len({track.id for track in tracks}) != len(tracks):
            raise ValueError("A biblioteca contém IDs repetidos.")
        self.library = {track.id: track for track in tracks}
        return len(self.library)

    def create_playlist(self, name):
        self.playlist = DoublyLinkedList()
        self.playlist_name = name
        self.current_track = None

    def add_to_playlist(self, track_id):
        self.playlist.add(self._get_track(track_id))

    def _get_track(self, track_id):
        try:
            return self.library[int(track_id)]
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError(f"Faixa {track_id} não encontrada na biblioteca.") from exc

    def _record(self, track):
        self.current_track = track
        self.history.append({"id": track.id, "timestamp": datetime.now().isoformat(timespec="seconds")})
        return track

    def play(self):
        track = self.playlist.current()
        if track is None:
            raise ValueError("A playlist está vazia.")
        return self._record(track)

    def next(self):
        if self.up_next:
            return self._record(self.up_next.popleft())
        track = self.playlist.play_next()
        if track is None:
            raise ValueError("Não há próxima faixa na playlist.")
        return self._record(track)

    def prev(self):
        track = self.playlist.play_prev()
        if track is None:
            raise ValueError("Não há faixa anterior na playlist.")
        return self._record(track)

    def enqueue(self, track_id):
        self.up_next.append(self._get_track(track_id))

    def smart_shuffle(self, count):
        if count < 0 or count > len(self.library):
            raise ValueError(f"Informe um número entre 0 e {len(self.library)}.")
        recent = {}
        for position, item in enumerate(reversed(self.history)):
            recent.setdefault(item["id"], position)
        priority = PriorityQueue()
        for track in self.library.values():
            penalty = 5 - recent[track.id] if recent.get(track.id, 99) < 5 else 0
            priority.put((-10 * track.rating + penalty, track.id, track))
        self.playlist.clear()
        for _ in range(count):
            self.playlist.add(priority.get()[2])
        self.playlist_name = "smart-shuffle"
        self.current_track = None
        return count

    def state_dict(self):
        return {
            "playlist_name": self.playlist_name,
            "playlist": [track.id for track in self.playlist],
            "cursor": self.playlist.cursor_index(),
            "up_next": [track.id for track in self.up_next],
            "history": list(self.history),
            "current_track": self.current_track.id if self.current_track else None,
        }

    def save(self, filename):
        Path(filename).write_text(json.dumps(self.state_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def restore(self, filename):
        try:
            data = json.loads(Path(filename).read_text(encoding="utf-8"))
            playlist_ids = data["playlist"]
            queue_ids = data["up_next"]
            history = data["history"]
            cursor = int(data["cursor"])
            tracks = [self._get_track(track_id) for track_id in playlist_ids]
            queue_tracks = [self._get_track(track_id) for track_id in queue_ids]
            restored_history = deque(({"id": int(item["id"]), "timestamp": str(item["timestamp"])} for item in history), maxlen=self.HISTORY_LIMIT)
            current = self._get_track(data["current_track"]) if data.get("current_track") is not None else None
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Estado inválido ou incompatível: {exc}") from exc
        if tracks and not 0 <= cursor < len(tracks):
            raise ValueError("Cursor inválido no arquivo de estado.")
        if not tracks and cursor != 0:
            raise ValueError("Cursor inválido no arquivo de estado.")
        self.playlist.clear()
        for track in tracks:
            self.playlist.add(track)
        if tracks:
            self.playlist.set_cursor(cursor)
        self.playlist_name = data.get("playlist_name")
        self.up_next = deque(queue_tracks)
        self.history = restored_history
        self.current_track = current
