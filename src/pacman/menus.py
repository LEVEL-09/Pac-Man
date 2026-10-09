"""Module containing menus for the Pac-Man game."""
from mlx_wrapper import MLXApp, KEY_ESC

from pacman.base import Menu


class MainMenu(Menu):
    """Main menu of the Pac-Man game."""

    def __init__(self, game: MLXApp) -> None:
        """Initialize the main menu.

        Args:
            app (MLXApp): The MLX application instance.
            width (int): Width of the menu canvas.
            height (int): Height of the menu canvas.
        """
        super().__init__(game)
        self.add_button("Start", lambda: print("Start pressed"))
        self.add_button("Leaderboard", lambda: print("Leaderboard pressed"))
        self.add_button("Quit", lambda: print("quit pressed"))

    def update(self) -> None:
        """Update the main menu canvas."""
        logo = self.game.am.get_sprite("logo")
        self.draw_stars()
        y = (self.canvas.height - 900) // 2
        logo.blit(
            self.canvas, (self.canvas.width - logo.width) // 2, y
        )
        y += logo.height + 50
        y_pad = 10
        y = self.draw_buttons(y, y_pad)

        y += 100
        font = self.game.am.get_font("kolostygra")
        font.draw_text(
            self.canvas,
            "Contributors",
            (self.canvas.width - font.measure_text("Contributors:")) // 2, y,
            0xFFFFFFFF, cache=True
        )
        y += font.atlas.height + y_pad
        contributors = "Adnan BOUZKRAOUI & Mohamed KHOUBAZ"
        font.draw_text(
            self.canvas,
            contributors,
            (self.canvas.width - font.measure_text(contributors)) // 2, y,
            0xFFFFFFFF, cache=True
        )

class PauseMenu(Menu):
    """Pause menu of the Pac-Man game."""

    def __init__(self, game: MLXApp) -> None:
        """Initialize the pause menu.

        Args:
            app (MLXApp): The MLX application instance.
            width (int): Width of the menu canvas.
            height (int): Height of the menu canvas.
        """
        super().__init__(game)
        self.add_button("Resume", lambda: self.game.switch_scene(self))
        self.add_button("Cheat", lambda: print("Cheat pressed"))
        self.add_button("Quit", self.quit)

    def mount(self) -> None:
        """Mount the pause menu, making it active and visible."""
        super().mount()
        self.game.unbind_key(KEY_ESC)

    def unmount(self) -> None:
        """Unmount the pause menu, making it inactive and invisible."""
        super().unmount()
        self.game.bind_key(KEY_ESC, lambda: self.game.push_scene(PauseMenu(self.game)))

    def update(self) -> None:
        """Update the pause menu canvas."""
        self.draw_stars()
        self.draw_buttons((self.canvas.height - 300) // 2, 10)

    def quit(self) -> None:
        """Quit the game."""
        self.game.pop_scene()
        self.game.pop_scene()
