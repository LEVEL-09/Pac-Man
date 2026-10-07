"""In-game menus, including the main menu and its buttons."""

from mlx_wrapper import (
    KEY_DOWN,
    KEY_ENTER,
    KEY_UP,
    MLXApp,
    Sprite,
)

from src.pacman.base import Scene
from src.pacman.ui import Keyboard

from .base import Menu


class EndScene(Scene):
    def __init__(self, game, lost):
        super().__init__(game)
        self.font = game.am.get_font("kolostygra")
        self.title = game.am.get_sprite('game_over') if lost else game.am.get_sprite('win')
        self.blank = Sprite.blank(game.width, game.height)
        self.blank.fill(0xFF000000)
        self.keyboard = Keyboard(game, 0, 0)
        self.keyboard.x = (game.width - self.keyboard.width) // 2
        self.keyboard.y = self.title.height + 30 + 100
        max_chars = 30
        self.user_input_sprite = Sprite.blank(self.font['m'][1] * max_chars, self.font.atlas.height)

    def mount(self):
        self.keyboard.mount()
        self.game.bind_key(KEY_ENTER, lambda: self.game.pop_scene())

    def unmount(self):
        self.game.unbind_key(KEY_ENTER)
        self.keyboard.unmount()

    def update(self):
        self.user_input_sprite.fill(0)
        if self.keyboard.buffer:
            self.font.draw_text(
                self.user_input_sprite,
                self.keyboard.buffer,
                (self.user_input_sprite.width - self.font.measure_text(self.keyboard.buffer)) // 2,
                0,
                0xFFFFFFFF
            )

    def draw(self, x, y):
        self.blank.draw_to_window(self.game.win_ptr, 0, 0)
        self.title.draw_to_window(self.game.win_ptr, (self.game.width - self.title.width) // 2, 30)
        self.keyboard.draw()
        self.user_input_sprite.draw_to_window(self.game.win_ptr, (self.game.width - self.user_input_sprite.width) // 2, 150)


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
        self.add_button(
            "Start",
            lambda: self.game.push_scene(EndScene(self.game, True))
        )
        self.add_button("Leaderboard", lambda: print("Leaderboard pressed"))
        self.add_button("Quit", lambda: print("quit pressed"))

    def mount(self) -> None:
        """Mount the main menu, making it active and visible."""
        self.game.bind_key(KEY_DOWN, self.focus_next)
        self.game.bind_key(KEY_UP, self.focus_prev)
        self.game.bind_key(KEY_ENTER, self.focus_enter)

    def unmount(self) -> None:
        """Unmouount the main menu, making it inactive and invisible."""
        self.game.unbind_key(KEY_DOWN)
        self.game.unbind_key(KEY_UP)
        self.game.unbind_key(KEY_ENTER)

    def update(self) -> None:
        """Update the main menu state."""
        logo = self.game.am.get_sprite("logo")
        self.draw_background()
        y = 50
        logo.blit(
            self.canvas, (self.canvas.width - logo.width) // 2, y
        )
        y += logo.height + 50
        y_pad = 10
        y += self.draw_buttons(y, y_pad)

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
