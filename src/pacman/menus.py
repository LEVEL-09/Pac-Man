"""In-game menus, including the main menu and its buttons."""

from abc import ABC, abstractmethod
from typing import Any, Callable

import numpy as np
from mlx_wrapper import AssetManager, MLXApp, Sprite

KEY_LEFT = 0xFF51
KEY_UP = 0xFF52
KEY_RIGHT = 0xFF53
KEY_DOWN = 0xFF54
KEY_ENTER = 0xFF0D


class Menu(ABC):
    """Abstract base class for menus.

    Attributes:
        app (MLXApp): The MLX application instance.
        canvas (Sprite): The canvas sprite for drawing.
        buttons (list[Button]): List of buttons in the menu.
        current_btn (int): Index of the currently focused button.

    """

    def __init__(self, app: MLXApp, width: int, height: int) -> None:
        """Initialize the menu with the given MLX application and dimensions.

        Args:
            app (MLXApp): The MLX application instance.
            width (int): Width of the menu canvas.
            height (int): Height of the menu canvas.
        """
        self.app: MLXApp = app
        self.canvas: Sprite = Sprite.blank(width, height)
        self.buttons: list[Button] = []
        self.current_btn: int = -1
        # Whether the menu is currently active.
        self._is_active: bool = False

    def mount(self) -> None:
        """Mount the menu, making it active and visible."""
        self._is_active = True

    def unmount(self) -> None:
        """Unmount the menu, making it inactive and hidden."""
        self._is_active = False

    @abstractmethod
    def draw_background(self) -> None:
        """Draw the background of the menu."""
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the menu state."""
        pass

    def add_button(self, text: str, callback: Callable[[], None]) -> None:
        """Add a button to the menu.

        Args:
            text (str): The text to display on the button.
            callback (Callable[[], None]): The function to call when the
                button is clicked.
        """
        self.buttons.append(Button(text, callback, self.app.asset_manager))

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
            y (int): Starting y-coordinate for the first button.
            y_pad (int): Padding between buttons.

        Returns:
            int: The final y-coordinate after drawing all buttons.
        """
        y_offset = 0
        for btn in self.buttons:
            btn.draw(
                self.canvas, (self.canvas.width - btn.w) // 2, y + y_offset)
            y_offset += btn.h + y_pad
        return y + y_offset

    def draw(self, win_ptr: int, x: int, y: int) -> None:
        """Draw the menu to the window.

        Args:
            win_ptr (int): Pointer to the window.
            x (int): X-coordinate of the top-left corner.
            y (int): Y-coordinate of the top-left corner.
        """
        self.canvas.draw(win_ptr, x, y)


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
        self.logo: Sprite = app.asset_manager.get_sprite("logo")
        self.stars: np.ndarray = np.random.randint(
            low=[0, 0], high=[width, height], size=(300, 2)
        )
        self.add_button("Start", lambda: print("Start pressed"))
        self.add_button("Leaderboard", lambda: print("Leaderboard pressed"))
        self.add_button("Quit", lambda: print("quit pressed"))

    def mount(self) -> None:
        """Mount the main menu, making it active and visible."""
        super().mount()
        self.app.bind_key(KEY_DOWN, self.focus_next)
        self.app.bind_key(KEY_UP, self.focus_prev)
        self.app.bind_key(KEY_ENTER, self.focus_enter)

    def unmount(self) -> None:
        """Unmouount the main menu, making it inactive and invisible."""
        super().unmount()
        self.app.unbind_key(KEY_DOWN)
        self.app.unbind_key(KEY_UP)
        self.app.unbind_key(KEY_ENTER)

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
        font = self.app.asset_manager.get_font("kolostygra")
        font.draw_text(
            self.canvas,
            "Contributors",
            (self.canvas.width - font.measure_text("Contributors:")) // 2,
            y,
            0xFFFFFFFF,
            cache=True,
        )
        y += font.atlas.height + y_pad
        contributors = "Adnan BOUZKRAOUI & Mohammed KHOUBAZ"
        font.draw_text(
            self.canvas,
            contributors,
            (self.canvas.width - font.measure_text(contributors)) // 2,
            y,
            0xFFFFFFFF,
            cache=True,
        )

    def draw(self, win_ptr: int, x: int, y: int) -> None:
        """Draw the menu on the window.

        Args:
            win_ptr (int): Window pointer.
            x (int): X-coordinate of the top-left corner.
            y (int): Y-coordinate of the top-left corner.
        """
        self.canvas.draw_to_window(win_ptr, x, y)


class Button:
    """Button that can be focused/unfocused and triggers a callback.

    The callback is triggered when the button is focused and pressed
    using KEY_ENTER. It builds the button's states (focused/unfocused)
    from the given title and callback.

    Attributes:
        w (int): Width of the button.
        h (int): Height of the button.
        states (dict[bool, Sprite]): Dictionary of rendered states
            (focused/unfocused).
        callback (Callable[..., None]): Function to call when the button is
            pressed.
        focused (bool): Whether the button is currently focused.

    """

    def __init__(
        self,
        title: str,
        callback: Callable[[], None],
        am: AssetManager,
        focused: bool = False,
    ) -> None:
        """Initialize the button with a title, callback, and asset manager.

        Args:
            title (str): Text to display on the button.
            callback (Callable[..., None]): Function to call when the button is
                pressed.
            am (AssetManager): Asset manager to use for rendering.
            focused (bool): Whether the button should be focused initially.
                Defaults to False.
        """
        font = am.get_font("kolostygra")
        text_w = font.measure_text(title)
        slice_w = 58
        slice_h = 64
        mid_segments = text_w // slice_w + 1

        self.w: int = (mid_segments + 2) * slice_w
        self.h: int = slice_h
        self.states: dict[bool, Sprite] = {
            False: Sprite.blank(self.w, slice_h),
            True: Sprite.blank(self.w, slice_h),
        }
        self.callback: Callable[..., None] = callback
        self.focused: bool = focused

        am.get_sprite("btn_unfocused_start").blit(self.states[False], 0, 0)
        am.get_sprite("btn_focused_start").blit(self.states[True], 0, 0)
        for _ in range(1, mid_segments + 1):
            am.get_sprite("btn_unfocused_mid").blit(
                self.states[False], _ * slice_w, 0
            )
            am.get_sprite("btn_focused_mid").blit(
                self.states[True], _ * slice_w, 0
            )
        am.get_sprite("btn_unfocused_end").blit(
            self.states[False], self.w - slice_w, 0
        )
        am.get_sprite("btn_focused_end").blit(
            self.states[True], self.w - slice_w, 0
        )

        font.draw_text(
            self.states[False],
            title,
            (self.states[False].width - text_w) // 2,
            (self.states[False].height - font.atlas.height) // 2 - 3,
            0xFF9B6800,
        )
        font.draw_text(
            self.states[True],
            title,
            (self.states[True].width - text_w) // 2,
            (self.states[True].height - font.atlas.height) // 2 - 3,
            0xFF189FC2,
        )

    def draw(self, target: Sprite, x: int, y: int) -> None:
        """Draw the button's current state on the target sprite.

        Args:
            target (Sprite): Target sprite to draw on.
            x (int): X-coordinate of the top-left corner of the button.
            y (int): Y-coordinate of the top-left corner of the button.
        """
        self.states[self.focused].blit(target, x, y)

    def on_click(self, *args: Any, **kwargs: Any) -> None:
        """Event handler for when the button is clicked.

        Args:
            *args: Variable length argument list.
            **kwargs: Variable length keyword arguments.
        """
        if self.focused:
            self.callback(*args, **kwargs)
