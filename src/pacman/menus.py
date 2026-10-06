"""In-game menus, including the main menu and its buttons."""

import numpy as np
from mlx_wrapper import (
    KEY_DOWN,
    KEY_ENTER,
    KEY_UP,
    MLXApp,
)

from .base import Menu


class MainMenu(Menu):
    """Main menu of the Pac-Man game.

    Attributes:
        logo (Sprite): The logo sprite.
    """

    def __init__(self, app: MLXApp, width: int, height: int) -> None:
        """Initialize the main menu.

        Args:
            app (MLXApp): The MLX application instance.
            width (int): Width of the menu canvas.
            height (int): Height of the menu canvas.
        """
        super().__init__(app, width, height)
        self.logo = app.asset_manager.get_sprite("logo")
        self.stars = np.random.randint(
            low=[0, 0], high=[width, height], size=(300, 2)
        )
        self.add_button("Start", lambda: print("Start pressed"))
        self.add_button("Leaderboard", lambda: print("Leaderboard pressed"))
        self.add_button("Quit", lambda: print("quit pressed"))

    def mount(self) -> None:
        """Mount the main menu, making it active and visible."""
        super().mount()
        self.game.bind_key(KEY_DOWN, self.focus_next)
        self.game.bind_key(KEY_UP, self.focus_prev)
        self.game.bind_key(KEY_ENTER, self.focus_enter)

    def unmount(self) -> None:
        """Unmouount the main menu, making it inactive and invisible."""
        super().unmount()
        self.game.unbind_key(KEY_DOWN)
        self.game.unbind_key(KEY_UP)
        self.game.unbind_key(KEY_ENTER)

    def draw_background(self) -> None:
        """Draw a background animation of moving stars."""
        self.stars += 1
        self.stars[:, 0] %= self.canvas.width
        self.stars[:, 1] %= self.canvas.height
        self.canvas.fill(0xFF180000)

        star_size = 2
        for x, y in self.stars:
            x_end = min(x + star_size, self.canvas.width)
            y_end = min(y + star_size, self.canvas.height)
            self.canvas.pixels[y:y_end, x:x_end] = 0xFFFFFFFF

    def update(self) -> None:
        """Update the main menu state."""
        self.draw_background()
        y = 50
        self.logo.blit(
            self.canvas, (self.canvas.width - self.logo.width) // 2, y
        )
        y += self.logo.height + 50
        y_pad = 10
        y += self.draw_buttons(y, y_pad)

        y += 100
        font = self.game.asset_manager.get_font("kolostygra")
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
