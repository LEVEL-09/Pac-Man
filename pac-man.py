"""Entry point script for launching the Pac-Man game."""


from src.pacman.game import Game


def main() -> None:
    """Run the Pac-Man game."""


if __name__ == "__main__":
    Game(15, 12, "Pac-Man").start()
