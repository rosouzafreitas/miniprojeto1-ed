from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Track:
    id: int
    title: str
    artist: str
    duration: int
    rating: int
    data_adicao: str

    @classmethod
    def from_dict(cls, data):
        try:
            track = cls(
                id=int(data["id"]), title=str(data["title"]),
                artist=str(data["artist"]), duration=int(data["duration"]),
                rating=int(data["rating"]),
                data_adicao=str(data.get("data_adicao", "")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Dados de faixa inválidos ou incompletos.") from exc
        if track.id < 0 or track.duration < 0 or not 1 <= track.rating <= 5:
            raise ValueError("ID e duração devem ser não negativos; rating deve ficar entre 1 e 5.")
        if not track.title.strip() or not track.artist.strip():
            raise ValueError("Título e artista não podem ficar vazios.")
        return track

    def to_dict(self):
        return asdict(self)

    @property
    def duration_text(self):
        return f"{self.duration // 60}:{self.duration % 60:02d}"
