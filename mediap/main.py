from .cli import CommandLine
from .player import MediaPlayer


def main():
    CommandLine(MediaPlayer()).run()


if __name__ == "__main__":
    main()
