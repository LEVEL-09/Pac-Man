"""Entry point script for launching the Pac-Man game."""

from mlx_wrapper import AssetManager, MLXApp, Sprite

from pacman.ghost import Pinky
from pacman.maze import Maze
from pacman.player import Player


class Game(MLXApp):
    def __init__(self, width: int, height: int, title: str) -> None:
        win_w, win_h = (
            (width * 2 + 1) * 32,
            (height * 2 + 1) * 32 + 75 * 2
        )
        super().__init__(win_w, win_h, title)

        self.am = AssetManager("./assets.xml")
        self.maze = Maze(self, width, height, 4, self.am, 10)
        self.maze.create_sprite(2)
        self.main = Sprite.blank(win_w, win_h)
        self.main.fill(0xFF000000)
        self.maze.draw(self.main)

        self.pacman = Player(self)
        self.pinky = Pinky(self, (1, 1), 4, 0x80FF00FF)

    def update(self) -> None:
        self.pacman.update()
        self.pinky.update()

        self.main.draw_to_window(self.win_ptr, 0, 0)

        self.pinky.visualize_path()
        self.pinky.draw()
        self.pacman.draw()


if __name__ == "__main__":
    Game(15, 15, "Pac-Man").start()
