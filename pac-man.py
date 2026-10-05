"""Entry point script for launching the Pac-Man game."""

from mlx_wrapper import AssetManager, MLXApp, Sprite

from pacman.base import Keyboard


class Game(MLXApp):
    def __init__(self, width: int, height: int, title: str) -> None:
        win_w, win_h = (
            (width * 2 + 1) * 32,
            (height * 2 + 1) * 32 + 75 * 2
        )
        super().__init__(win_w, win_h, title)

        self.am = AssetManager("./assets.xml")
        self.main = Sprite.blank(win_w, win_h)
        self.main.fill(0xFF000000)

        self.keyboard = Keyboard(self, 10, 10)

    def update(self) -> None:
        self.main.draw_to_window(self.win_ptr, 0, 0)
        self.keyboard.draw()


if __name__ == "__main__":
    Game(19, 12, "Pac-Man").start()
