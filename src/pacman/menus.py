"""In-game menus, including the main menu and its buttons."""

from mlx_wrapper import MLXApp

from .base import Menu


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
            (self.canvas.width - font.measure_text("Contributors:")) // 2,
            y,
            0xFFFFFFFF, cache=True
        )
        y += font.atlas.height + y_pad
        contributors = "Adnan BOUZKRAOUI & Mohammed KHOUBAZ"
        font.draw_text(
            self.canvas,
            contributors,
            (self.canvas.width - font.measure_text(contributors)) // 2,
            y,
            0xFFFFFFFF, cache=True
        )
