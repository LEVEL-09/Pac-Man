"""In-game menus, including the main menu and its buttons."""

from mlx_wrapper import KEY_ENTER, MLXApp

from pacman.base import Scene
from pacman.ui import Keyboard


class EndScene(Scene):
    """End scene for the game.

    Displays the game over or win screen and waits for the player
    to press Enter.

    Attributes:
        lost: Whether the player lost or won.
    """

    def __init__(self, game: MLXApp, lost: bool) -> None:
        """Initialize the end scene.

        Args:
            game: Game instance.
            lost: Whether the player lost or won.
        """
        super().__init__(game)
        self.font = game.am.get_font("kolostygra")
        if lost:
            self.title = game.am.get_sprite('win')
        else:
            self.title = game.am.get_sprite('game_over')
        self.keyboard = Keyboard(game, 0, 0, 30)
        self.keyboard.x = (game.width - self.keyboard.width) // 2
        self.keyboard.y = (game.height - self.title.height) // 2

    def mount(self) -> None:
        """Mount the end scene."""
        self.keyboard.mount()
        self.game.bind_key(KEY_ENTER, self._on_enter)

    def unmount(self) -> None:
        """Unmount the end scene."""
        self.keyboard.unmount()
        self.game.unbind_key(KEY_ENTER)

    def _on_enter(self) -> None:
        """Handle the Enter key press."""
        print("Enter pressed")

    def update(self) -> None:
        """Update the end scene."""
        self.draw_stars()
        self.title.blit(
            self.canvas, (self.canvas.width - self.title.width) // 2, 50
        )
        self.keyboard.blit(self.canvas)
        text_center = (
            self.canvas.width -
            self.font.measure_text(f"Your score: {1000}")
        ) // 2
        self.font.draw_text(
            self.canvas,
            f"Your score: {1000}",
            text_center, self.title.height + 150,
            0xFFFFFF00, cache=True
        )
        text_center = (
            self.canvas.width -
            self.font.measure_text("Type in your username")
        ) // 2
        self.font.draw_text(
            self.canvas,
            "Type in your username:",
            text_center, self.keyboard.y - self.font.atlas.height - 100,
            0xFFFFFFFF, cache=True
        )
        if self.keyboard.buffer:
            text_center = (self.canvas.width -
                           self.font.measure_text(self.keyboard.buffer)) // 2
            self.font.draw_text(
                self.canvas,
                self.keyboard.buffer,
                text_center, self.keyboard.y - self.font.atlas.height - 50,
                0xFFFFFFFF
            )

    def draw(self, x: int, y: int) -> None:
        """Draw the end scene.

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        self.canvas.draw_to_window(self.game.win_ptr, 0, 0)
