"""Module containing menus for the Pac-Man game."""
from pacman.base import Menu
from src.pacman.scenes import GamePlayScene


class MainMenu(Menu):
    """Main menu of the Pac-Man game."""

    def __init__(self) -> None:
        """Initialize the main menu.

        Args:
            app (MLXApp): The MLX application instance.
            width (int): Width of the menu canvas.
            height (int): Height of the menu canvas.
        """
        super().__init__()
        self.add_button("Start", lambda: self.game.push_scene(GamePlayScene()))
        self.add_button("Leaderboard", lambda: print("Leaderboard pressed"))
        self.add_button("Quit", lambda: print("quit pressed"))

    def update(self) -> None:
        """Update the main menu canvas."""
        logo = self.am.get_sprite("logo")
        self.draw_stars()
        y = (self.canvas.height - 900) // 2
        logo.blit(
            self.canvas, (self.canvas.width - logo.width) // 2, y
        )
        y += logo.height + 50
        y_pad = 10
        y = self.draw_buttons(y, y_pad)

        y += 100
        font = self.am.get_font("kolostygra")
        font.draw_text(
            self.canvas,
            "Contributors",
            (self.canvas.width - font.measure_text("Contributors:")) // 2, y,
            0xFFFFFFFF, cache=True
        )
        y += font.atlas.height + y_pad
        contributors = "Adnan BOUZKRAOUI & Mohammed KHOUBAZ"
        font.draw_text(
            self.canvas,
            contributors,
            (self.canvas.width - font.measure_text(contributors)) // 2, y,
            0xFFFFFFFF, cache=True
        )
