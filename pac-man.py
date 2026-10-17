"""Entry point script for launching the Pac-Man game."""


from src.pacman.game import Game


def main() -> None:
    """Run the Pac-Man game."""
    Game().start()


if __name__ == "__main__":
    main()
