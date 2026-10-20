"""Entry point script for launching the Pac-Man game."""

from pacman.error_handler import ErrorHandler
from pacman.game import Game


def main() -> None:
    """Run the Pac-Man game."""
    with ErrorHandler():
        Game().start()


if __name__ == "__main__":
    main()
