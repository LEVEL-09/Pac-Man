"""Entry point script for launching the Pac-Man game."""
from mlx_wrapper import MLXApp

from pacman.maze import Maze


class Game(MLXApp):
    def __init__(self) -> None:
        super().__init__(800, 1000, "PAC-MAN")
        self.maze = Maze(self, 800, 800, 42)

    def update(self):
        self.maze.draw()

if __name__ == "__main__":
    Game().start()
