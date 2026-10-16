"""UI components for the Pac-Man game."""

from collections.abc import Callable
from typing import Any

from mlx_wrapper import (
    KEY_DOWN,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_SPACE,
    KEY_UP,
    AssetManager,
    Sprite,
)

from pacman.base import GameContext


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
        callback: Callable[..., None],
        am: AssetManager,
        focused: bool = False,
    ) -> None:
        """Initialize the button with a title, callback, and asset manager.

        Args:
            title: Text to display on the button.
            callback: Function to call when the button is
                pressed.
            am: Asset manager to use for rendering.
            focused: Whether the button should be focused initially.
                Defaults to False.
        """
        self.am = am
        self.callback: Callable[..., None] = callback
        self.focused = focused
        self.set_title(title)

    def set_title(self, title: str) -> None:
        """Set the title of the button and update its dimensions.

        Args:
            title: Text to display on the button.
        """
        font = self.am.get_font("kolostygra")
        text_w = font.measure_text(title)
        slice_w = 58
        slice_h = 64
        mid_segments = text_w // slice_w + 1

        self.w = (mid_segments + 2) * slice_w
        self.h = slice_h

        self.states = {
            False: Sprite.blank(self.w, slice_h),
            True: Sprite.blank(self.w, slice_h),
        }

        self.am.get_sprite(
            "btn_unfocused_start"
        ).blit(self.states[False], 0, 0)
        self.am.get_sprite("btn_focused_start").blit(self.states[True], 0, 0)
        for _ in range(1, mid_segments + 1):
            self.am.get_sprite("btn_unfocused_mid").blit(
                self.states[False], _ * slice_w, 0
            )
            self.am.get_sprite("btn_focused_mid").blit(
                self.states[True], _ * slice_w, 0
            )
        self.am.get_sprite("btn_unfocused_end").blit(
            self.states[False], self.w - slice_w, 0)
        self.am.get_sprite("btn_focused_end").blit(
            self.states[True], self.w - slice_w, 0)

        font.draw_text(
            self.states[False],
            title,
            (self.states[False].width - text_w) // 2,
            (self.states[False].height - font.atlas.height) // 2 - 3,
            color=0xFF9B6800
        )
        font.draw_text(
            self.states[True],
            title,
            (self.states[True].width - text_w) // 2,
            (self.states[True].height - font.atlas.height) // 2 - 3,
            color=0xFF189FC2,
        )

    def draw(self, target: Sprite, x: int, y: int) -> None:
        """Draw the button's current state on the target sprite.

        Args:
            target: Target sprite to draw on.
            x: X-coordinate of the top-left corner of the button.
            y: Y-coordinate of the top-left corner of the button.
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


class Keyboard:
    """In-game keyboard for typing characters.

    Attributes:
        ctx: Game context.
        x: X-coordinate of the keyboard.
        y: Y-coordinate of the keyboard.
        font: Font used for rendering characters.
        square_size: Size of each character square.
        width: Width of the keyboard.
        height: Height of the keyboard.
        layouts: dictionary of keyboard layouts (lowercase and uppercase).
        row: Current row of the focused key.
        col: Current column of the focused key.
        buffer: Buffer of characters typed by the user.
    """

    def __init__(
        self, ctx: GameContext, x: int, y: int, text_limit: int
    ) -> None:
        """Initialize the keyboard with the given game instance and position.

        Args:
            ctx: Game context.
            x: X-coordinate of the keyboard.
            y: Y-coordinate of the keyboard.
            text_limit: maximum number of characters allowed in the buffer.
        """
        self.game = ctx.game
        self.x, self.y = x, y
        self.text_limit = text_limit

        self.font_med = ctx.am.get_font("minecraft_medium")
        self.font_sm = ctx.am.get_font("minecraft_small")
        char_width = self.font_med["m"][1]
        char_height = self.font_med.atlas.height
        self.pad = 8
        self.margin = 5
        self.border = 3

        self.square_size = (
            max(char_width, char_height) + (self.margin + self.border) * 2
        )
        self.width = (self.square_size + self.pad) * 10 - self.pad
        self.height = (
            (self.square_size + self.pad) * 4 +
            self.font_sm.atlas.height * 2 + self.pad
        )

        self.layouts = {
            True: Sprite.blank(self.width, self.height),
            False: Sprite.blank(self.width, self.height),
        }

        # Characters for lowercase and uppercase layouts
        self._chars_lc = [
            "0123456789", "qwertyuiop", "↑asdfghjkl", "zxcvbnm–←"]
        self._chars_uc = [
            "0123456789", "QWERTYUIOP", "↑ASDFGHJKL", "ZXCVBNM–←"]

        # Whether the caps lock is on
        self._caps_lock = False
        self.row, self.col = 0, 0
        self.buffer = ""

        self._render_keyboard()
        self._set_key_color(0xFFFFFFFF)

    def mount(self) -> None:
        """Mount the keyboard by binding key events."""
        self.game.bind_key(KEY_SPACE, self._type_char)
        self.game.bind_key(KEY_UP, self._focus_up)
        self.game.bind_key(KEY_DOWN, self._focus_down)
        self.game.bind_key(KEY_RIGHT, self._focus_right)
        self.game.bind_key(KEY_LEFT, self._focus_left)

    def unmount(self) -> None:
        """Unmount the keyboard by unbinding key events."""
        self.game.unbind_key(KEY_SPACE)
        self.game.unbind_key(KEY_UP)
        self.game.unbind_key(KEY_DOWN)
        self.game.unbind_key(KEY_RIGHT)
        self.game.unbind_key(KEY_LEFT)

    def _curr_layout(self) -> list[str]:
        """Get the current layout (lowercase or uppercase).

        Returns:
            list[str]: current layout as a list of strings.
        """
        return self._chars_uc if self._caps_lock else self._chars_lc

    def _render_keyboard(self) -> None:
        """Create the keyboard layouts (lower and uppercase)."""
        y = 0
        for chars in self._chars_lc:
            x = 0
            for char in chars:
                self._draw_char(self.layouts[False], char, x, y, 0x7FFFFFFF)
                self._draw_char(
                    self.layouts[True], char.upper(), x, y, 0x7FFFFFFF
                )
                x += self.square_size + self.pad
            y += self.square_size + self.pad
        instructions = [
            "arrows (←↑↓→) to navigate keyboard",
            "space-bar to confirm"
        ]
        self.font_sm.draw_text(
            self.layouts[True],
            instructions[0],
            (self.width - self.font_sm.measure_text(instructions[0])) // 2,
            y,
            color=0xFFFFFFFF,
        )
        self.font_sm.draw_text(
            self.layouts[False],
            instructions[0],
            (self.width - self.font_sm.measure_text(instructions[0])) // 2,
            y,
            color=0xFFFFFFFF,
        )
        y += self.font_sm.atlas.height + self.pad
        self.font_sm.draw_text(
            self.layouts[True],
            instructions[1],
            (self.width - self.font_sm.measure_text(instructions[1])) // 2,
            y,
            color=0xFFFFFFFF,
        )
        self.font_sm.draw_text(
            self.layouts[False],
            instructions[1],
            (self.width - self.font_sm.measure_text(instructions[1])) // 2,
            y,
            color=0xFFFFFFFF,
        )

    def _draw_char(
        self, target: Sprite, char: str, x: int, y: int, color: int
    ) -> None:
        """Draw a character and its border on the target sprite at (x, y).

        Args:
            target: the target sprite to draw on.
            char: the character to draw.
            x: x-coordinate of the top-left corner.
            y: y-coordinate of the top-left corner.
            color: the color to use for the character.
        """
        target.pixels[
            y + self.border: y + self.square_size - self.border,
            x: x + self.border
        ] = color
        target.pixels[
            y + self.border: y + self.square_size - self.border,
            x + self.square_size - self.border: x + self.square_size
        ] = color
        target.pixels[
            y: y + self.border,
            x + self.border: x + self.square_size - self.border
        ] = color
        target.pixels[
            y + self.square_size - self.border: y + self.square_size,
            x + self.border: x + self.square_size - self.border
        ] = color

        self.font_med.draw_text(
            target,
            char,
            x + self.pad + self.border + self.margin,
            y + self.border + self.margin,
            color=color,
        )

    # TODO: decide whether to keep draw or blit
    def draw(self) -> None:
        """Draw the keyboard to the window."""
        self.layouts[self._caps_lock].draw_to_window(self.x, self.y)

    def blit(self, target: Sprite) -> None:
        """Blit the keyboard to the target sprite.

        Args:
            target: sprite to blit onto.
        """
        self.layouts[self._caps_lock].blit(target, self.x, self.y)

    def _key_coords(self) -> tuple[int, int]:
        """Get the coordinates of the current key.

        Returns:
            tuple[int, int]: (x, y) coordinates of the current key.
        """
        return (
            self.col * (self.square_size + self.pad),
            self.row * (self.square_size + self.pad),
        )

    def _set_key_color(self, color: int) -> None:
        """Set the color of the current key to the given color.

        Args:
            color: color to set the key to.
        """
        x, y = self._key_coords()
        char = self._curr_layout()[self.row][self.col]

        self.layouts[self._caps_lock].pixels[
            y: y + self.square_size, x: x + self.square_size
        ] = 0

        self._draw_char(self.layouts[self._caps_lock], char, x, y, color)

    def _focus_up(self) -> None:
        """Focus the key above the current key."""
        self._set_key_color(0x7FFFFFFF)
        self.row = max(0, self.row - 1)
        self.col = min(self.col, len(self._curr_layout()[self.row]) - 1)
        self._set_key_color(0xFFFFFFFF)

    def _focus_down(self) -> None:
        """Focus the key below the current key."""
        self._set_key_color(0x7FFFFFFF)
        self.row = min(3, self.row + 1)
        self.col = min(self.col, len(self._curr_layout()[self.row]) - 1)
        self._set_key_color(0xFFFFFFFF)

    def _focus_right(self) -> None:
        """Focus the key to the right of the current key."""
        self._set_key_color(0x7FFFFFFF)
        self.col = min(self.col + 1, len(self._curr_layout()[self.row]) - 1)
        self._set_key_color(0xFFFFFFFF)

    def _focus_left(self) -> None:
        """Focus the key to the left of the current key."""
        self._set_key_color(0x7FFFFFFF)
        self.col = max(0, self.col - 1)
        self._set_key_color(0xFFFFFFFF)

    def _type_char(self) -> None:
        """Fill up the buffer with the current character."""
        char = self._curr_layout()[self.row][self.col]

        if char == "↑":
            self._caps_lock = not self._caps_lock
            self._set_key_color(0xFFFFFFFF)
        elif char == "←":
            self.buffer = self.buffer[:-1]
        elif len(self.buffer) < self.text_limit:
            if char == "–":
                self.buffer += " "
            else:
                self.buffer += char
