import shlex


class CommandLine:
    def __init__(self, player, input_fn=input, output_fn=print):
        self.player = player
        self.input = input_fn
        self.output = output_fn
        self.running = True

    @staticmethod
    def _format_track(track):
        return f'{track.title} — {track.artist} ({track.duration_text})'

    def _playing(self, track):
        self.output(f'>>> Tocando: "{track.title}" — {track.artist} ({track.duration_text})')

    def execute(self, line):
        try:
            args = shlex.split(line)
            if not args:
                return
            command = args[0]
            if command == "help" and len(args) == 1:
                self._help()
            elif command == "quit" and len(args) == 1:
                self.running = False
            elif command == "library":
                self._library(args)
            elif command == "playlist":
                self._playlist(args)
            elif command == "play" and len(args) == 1:
                self._playing(self.player.play())
            elif command == "next" and len(args) == 1:
                self._playing(self.player.next())
            elif command == "prev" and len(args) == 1:
                self._playing(self.player.prev())
            elif command == "enqueue" and len(args) == 2:
                self.player.enqueue(args[1])
                self.output("Faixa adicionada à fila.")
            elif command == "queue" and args == ["queue", "show"]:
                if not self.player.up_next:
                    self.output("Fila vazia.")
                for pos, track in enumerate(self.player.up_next, 1):
                    self.output(f"{pos}. {self._format_track(track)}")
            elif command == "history" and len(args) == 1:
                self._history()
            elif command == "smart-shuffle" and len(args) == 2:
                count = self.player.smart_shuffle(int(args[1]))
                self.output(f"Playlist smart-shuffle criada com {count} faixas.")
            elif command == "save" and len(args) == 2:
                self.player.save(args[1])
                self.output(f"Estado salvo em {args[1]}.")
            elif command == "load" and len(args) == 2:
                self.player.restore(args[1])
                self.output(f"Estado carregado de {args[1]}.")
            else:
                self.output("Erro: comando inválido. Digite help para ver os comandos.")
        except (ValueError, IndexError, OSError) as exc:
            self.output(f"Erro: {exc}")

    def _library(self, args):
        if len(args) == 3 and args[1] == "load":
            total = self.player.load_library(args[2])
            self.output(f"Biblioteca carregada: {total} faixas.")
            return
        if len(args) in (2, 4) and args[1] == "list":
            key = "id"
            if len(args) == 4:
                if args[2] != "--by" or args[3] not in ("rating", "title", "artist"):
                    raise ValueError("Uso: library list [--by rating|title|artist]")
                key = args[3]
            if not self.player.library:
                self.output("Biblioteca vazia.")
                return
            for track in sorted(self.player.library.values(), key=lambda item: getattr(item, key)):
                self.output(f"{track.id}. {self._format_track(track)} | rating {track.rating}")
            return
        raise ValueError("Uso: library load <arquivo> ou library list [--by rating|title|artist]")

    def _playlist(self, args):
        if len(args) == 3 and args[1] == "new":
            self.player.create_playlist(args[2])
            self.output(f'Playlist "{args[2]}" criada.')
        elif args == ["playlist", "add"] or (len(args) == 3 and args[1] == "add"):
            if len(args) != 3:
                raise ValueError("Uso: playlist add <track_id>")
            self.player.add_to_playlist(args[2])
        elif len(args) == 3 and args[1] == "remove":
            pos = int(args[2]) - 1
            self.player.playlist.remove_at(pos)
        elif args == ["playlist", "show"]:
            if not self.player.playlist_name:
                self.output("Nenhuma playlist foi criada.")
                return
            cursor = self.player.playlist.cursor_index()
            for pos, track in enumerate(self.player.playlist):
                marker = ">" if pos == cursor else " "
                self.output(f"{marker} {pos + 1}. {self._format_track(track)}")
            if not len(self.player.playlist):
                self.output("Playlist vazia.")
        else:
            raise ValueError("Uso: playlist new <nome>, playlist add <id>, playlist remove <pos>, playlist show")

    def _history(self):
        if not self.player.history:
            self.output("Histórico vazio.")
            return
        for pos, item in enumerate(reversed(self.player.history), 1):
            track = self.player.library[item["id"]]
            stamp = item["timestamp"].replace("T", " ")
            self.output(f"{pos}. {track.title} — {track.artist} [{stamp}]")

    def _help(self):
        self.output("Comandos: library load <arquivo>; library list [--by rating|title|artist]; playlist new <nome>; playlist add <id>; playlist remove <pos>; playlist show; play; next; prev; enqueue <id>; queue show; history; smart-shuffle <n>; save <arquivo>; load <arquivo>; help; quit")

    def run(self):
        while self.running:
            try:
                line = self.input("mediap> ")
            except (EOFError, KeyboardInterrupt):
                self.output("")
                break
            self.execute(line)
