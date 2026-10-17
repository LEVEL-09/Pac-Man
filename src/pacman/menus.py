"""Module containing menus for the Pac-Man game."""

from collections.abc import Callable

from mlx_wrapper import KEY_DOWN, KEY_ENTER, KEY_ESC, KEY_UP

from pacman.base import Scene
from pacman.ui import Button


class Menu(Scene):
    """Abstract base class for menus.

    Attributes:
        buttons: List of buttons in the menu.
        current_btn: Index of the currently focused button.

    """

    def __init__(self) -> None:
        """Initialize the menu."""
        super().__init__()
        self.buttons: list[Button] = []
        self.current_btn = -1

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

    def add_button(self, text: str, callback: Callable[..., None]) -> None:
        """Add a button to the menu.

        Args:
            text: The text to display on the button.
            callback: The function to call when the
                button is clicked.
        """
        self.buttons.append(Button(text, callback, self.am))

    def focus_enter(self) -> None:
        """Trigger the callback of the currently focused button."""
        if self.current_btn != -1:
            self.buttons[self.current_btn].on_click()

    def focus_next(self) -> None:
        """Move focus to the next button."""
        if self.current_btn == -1:
            self.current_btn = 0
        else:
            self.buttons[self.current_btn].focused = False
            self.current_btn = (self.current_btn + 1) % len(self.buttons)
        self.buttons[self.current_btn].focused = True

    def focus_prev(self) -> None:
        """Move focus to the previous button."""
        if self.current_btn == -1:
            self.current_btn = len(self.buttons) - 1
        else:
            self.buttons[self.current_btn].focused = False
            self.current_btn = (self.current_btn - 1) % len(self.buttons)
        self.buttons[self.current_btn].focused = True

    def draw_buttons(self, y: int, y_pad: int) -> int:
        """Draw all buttons on the canvas.

        Args:
            y: Starting y-coordinate for the first button.
            y_pad: Padding between buttons.

        Returns:
            int: The final y-coordinate after drawing all buttons.
        """
        y_offset = 0
        for btn in self.buttons:
            btn.draw(
                self.canvas,
                (self.canvas.width - btn.w) // 2,
                y + y_offset
            )
            y_offset += btn.h + y_pad
        return y + y_offset


class MainMenu(Menu):
    """Main menu of the Pac-Man game."""

    def __init__(self) -> None:
        """Initialize the main menu."""
        from pacman.scenes import GamePlayScene, HighscoreScene
        super().__init__()
        self.font = self.am.get_font("kolostygra")
        self.logo = self.am.get_sprite("logo")
        self.add_button(
            "Start",
            lambda: self.game.switch_scene(GamePlayScene())
        )
        self.add_button(
            "Leaderboard",
            lambda: self.game.switch_scene(HighscoreScene())
        )
        self.add_button(
            "Quit",
            lambda: print("quit pressed")
        )

    def update(self) -> None:
        """Update the main menu canvas."""
        self.draw_background()
        y = (self.canvas.height - 900) // 2
        self.logo.blit(
            self.canvas, (self.canvas.width - self.logo.width) // 2, y
        )
        y += self.logo.height + 50
        y_pad = 10
        y = self.draw_buttons(y, y_pad)

        y += 100
        self.font.draw_text(
            self.canvas,
            "Contributors",
            (self.canvas.width - self.font.measure_text("Contributors:")) // 2,
            y,
            cache=True,
            color=0xFFFFFFFF
        )
        y += self.font.atlas.height + y_pad
        contributors = "Adnan BOUZKRAOUI & Mohamed KHOUBAZ"
        self.font.draw_text(
            self.canvas,
            contributors,
            (self.canvas.width - self.font.measure_text(contributors)) // 2,
            y,
            cache=True,
            color=0xFFFFFFFF
        )


class PauseMenu(Menu):
    """Pause menu of the Pac-Man game."""

    def __init__(self) -> None:
        """Initialize the pause menu."""
        super().__init__()
        self.add_button("Resume", lambda: self.game.pop_scene())
        self.add_button(
            "Cheat Menu",
            lambda: self.game.push_scene(CheatMenu())
        )
        self.add_button("Quit", self.quit)

    def mount(self) -> None:
        """Bind Escape to return to the Gameplay."""
        super().mount()
        self.game.bind_key(KEY_ESC, lambda: self.game.pop_scene())

    def unmount(self) -> None:
        """Unbind Escape."""
        super().unmount()
        self.game.unbind_key(KEY_ESC)

    def update(self) -> None:
        """Update the pause menu canvas."""
        self.draw_background()
        self.draw_buttons((self.canvas.height - 300) // 2, 10)

    def quit(self) -> None:
        """Quit the game."""
        self.game.pop_scene()
        self.game.switch_scene(MainMenu())


class CheatFlags:
    """Cheat flags for the Pac-Man game."""

    visualize_path = False
    inf_lives = False
    invincibility = False
    x2_speed = False


class CheatMenu(Menu):
    """Cheat menu of the Pac-Man game."""

    def __init__(self) -> None:
        """Initialize the cheat menu."""
        super().__init__()

        self.add_button(
            self._button_text("Visualize path", CheatFlags.visualize_path),
            self._toggle_visualize_path
        )
        self.add_button(
            self._button_text("Infinite lives", CheatFlags.inf_lives),
            self._toggle_inf_lives
        )
        self.add_button(
            self._button_text("Invincibility", CheatFlags.invincibility),
            self._toggle_invincibility
        )
        self.add_button(
            self._button_text("X2 speed", CheatFlags.x2_speed),
            self._toggle_x2_speed
        )

    def mount(self) -> None:
        """Bind Escape to return to the Main Menu."""
        super().mount()
        self.game.bind_key(KEY_ESC, lambda: self.game.pop_scene())

    def unmount(self) -> None:
        """Unbind Escape."""
        super().unmount()
        self.game.unbind_key(KEY_ESC)

    def _button_text(self, title: str, is_active: bool) -> str:
        """Format the button's text based on the title and active state.

        Returns:
            str: formatted button text.
            is_active: Whether the cheat flag is active or not.
        """
        return f"{title}: {'ON' if is_active else 'OFF'}"

    def _toggle_visualize_path(self) -> None:
        """Toggle the visualize path cheat flag and updates the button text."""
        CheatFlags.visualize_path = not CheatFlags.visualize_path
        self.buttons[0].set_title(
            self._button_text("Visualize path", CheatFlags.visualize_path)
        )

    def _toggle_inf_lives(self) -> None:
        """Toggle the inf lives cheat flag and updates the button text."""
        CheatFlags.inf_lives = not CheatFlags.inf_lives
        self.buttons[1].set_title(
            self._button_text("Infinite lives", CheatFlags.inf_lives)
        )

    def _toggle_invincibility(self) -> None:
        """Toggle the invincibility cheat flag and updates the button text."""
        CheatFlags.invincibility = not CheatFlags.invincibility
        self.buttons[2].set_title(
            self._button_text("Invincibility", CheatFlags.invincibility)
        )

    def _toggle_x2_speed(self) -> None:
        """Toggle the x2 speed cheat flag and updates the button text."""
        CheatFlags.x2_speed = not CheatFlags.x2_speed
        self.buttons[3].set_title(
            self._button_text("X2 speed", CheatFlags.x2_speed)
        )

    def update(self) -> None:
        """Update the scene, drawing the background and buttons."""
        self.draw_background()
        self.draw_buttons((self.game.height - 296) // 2, 10)
