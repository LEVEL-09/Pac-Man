"""Module containing base classes for the game."""


from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from mlx_wrapper import (
    KEY_DOWN,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_SPACE,
    KEY_UP,
    AnimatedSprite,
    AssetManager,
    MLXApp,
    Sprite,
)


class MovingEntity:
    """Base class for all moving entities in the game.

    Attributes:
        game (MLXApp): Game instance.
        gw (int): width of the maze grid.
        gh (int): height of the maze grid.
        curr_cell (tuple[int, int]): current cell position.
        x (int): X-coordinate of the entity.
        y (int): Y-coordinate of the entity.
        speed (int): Speed of the entity.
        dx (int): X-direction of the entity.
        dy (int): Y-direction of the entity.
        next_dx (int): Next x-direction of the entity.
        next_dy (int): Next y-direction of the entity.
        curr_state (str): current state of the entity.
        animations (dict[str, AnimatedSprite]): Animations of the entity.
    """

    CELL_SIZE = 32

    def __init__(
        self, game: MLXApp, start_cell: tuple[int, int], speed: int
    ) -> None:
        """Initialize the moving entity.

        Args:
            game (MLXApp): Game instance.
            start_cell (tuple[int, int]): Starting cell position.
            speed (int): Speed of the entity.
        """
        self.game = game
        self.gw = len(game.maze.grid[0]) - 1
        self.gh = len(game.maze.grid) - 1
        self.curr_cell = start_cell

        self.x = self.curr_cell[0] * 32
        self.y = self.curr_cell[1] * 32
        self.speed = speed

        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

        self.curr_state = 'left'
        self.animations: dict[str, AnimatedSprite] = {}

    def _add_animation(self, state: str, animation: AnimatedSprite) -> None:
        """Add an animation to the entity's animations dictionary."""
        self.animations[state] = animation

    def _is_walkable(self, gx: int, gy: int) -> bool:
        """Whether the given grid position is walkable.

        Returns:
            bool: True if the position is walkable, False otherwise.
        """
        if gx < 0 or gx >= self.gw or gy < 0 or gy >= self.gh:
            return False
        return bool(self.game.maze.grid[gy][gx] == 0)

    def _update_direction(self, new_dx: int, new_dy: int) -> None:
        """Update the entity's direction and state based on the new direction.

        Args:
            new_dx (int): new x direction.
            new_dy (int): new y direction.
        """
        old_state = self.curr_state
        self.dx = new_dx
        self.dy = new_dy

        if self.dx == 1:
            self.curr_state = "right"
        elif self.dx == -1:
            self.curr_state = "left"
        elif self.dy == 1:
            self.curr_state = "down"
        elif self.dy == -1:
            self.curr_state = "up"

        if old_state != self.curr_state:
            self.animations[self.curr_state].play()

    def at_tile_center(self) -> None:
        """Override to handle when the entity reaches the center of a tile."""

    def move(self) -> None:
        """Move the entity's position and state.

        Based on the current direction and speed, it moves the entity along the
        current direction by one pixel per update to ensure smooth movement and
        no jitter.
        """
        if (self.dx != 0 and self.next_dx == -self.dx) or (
            self.dy != 0 and self.next_dy == -self.dy
        ):
            self._update_direction(self.next_dx, self.next_dy)

        remaining_steps = self.speed
        while remaining_steps > 0:
            if self.x % self.CELL_SIZE == 0 and self.y % self.CELL_SIZE == 0:
                self.curr_cell = (
                    self.x // self.CELL_SIZE,
                    self.y // self.CELL_SIZE,
                )
                self.at_tile_center()
                if self._is_walkable(
                    self.curr_cell[0] + self.next_dx,
                    self.curr_cell[1] + self.next_dy,
                ):
                    self._update_direction(self.next_dx, self.next_dy)

                if not self._is_walkable(
                    self.curr_cell[0] + self.dx,
                    self.curr_cell[1] + self.dy,
                ):
                    if self.curr_state in self.animations:
                        self.animations[self.curr_state].stop()
                    break

            self.x += self.dx
            self.y += self.dy
            remaining_steps -= 1

        if self.curr_state in self.animations:
            self.animations[self.curr_state].update(self.game.dt)

    def draw(self) -> None:
        """Draw the entity to the window."""
        self.animations[self.curr_state].draw_to_window(
            self.game.win_ptr, self.x, self.y + self.game.maze.y_offset
        )


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
        self.app = app
        self.canvas = Sprite.blank(width, height)
        self.buttons: list[Button] = []
        self.current_btn = -1
        # Whether the menu is currently active.
        self._is_active = False

    def mount(self) -> None:
        """Mount the menu, making it active and visible."""
        self._is_active = True

    def unmount(self) -> None:
        """Unmount the menu, making it inactive and hidden."""
        self._is_active = False

    @abstractmethod
    def draw_background(self) -> None:
        """Draw the background of the menu."""

    @abstractmethod
    def update(self) -> None:
        """Update the menu state."""

    def add_button(self, text: str, callback: Callable[..., None]) -> None:
        """Add a button to the menu.

        Args:
            text (str): The text to display on the button.
            callback (Callable[..., None]): The function to call when the
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
                self.canvas, (self.canvas.width - btn.w) // 2, y + y_offset
            )
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

        self.w = (mid_segments + 2) * slice_w
        self.h = slice_h
        self.states = {
            False: Sprite.blank(self.w, slice_h),
            True: Sprite.blank(self.w, slice_h),
        }
        self.callback: Callable[..., None] = callback
        self.focused = focused

        am.get_sprite("btn_unfocused_start").blit(self.states[False], 0, 0)
        am.get_sprite("btn_focused_start").blit(self.states[True], 0, 0)
        for _ in range(1, mid_segments + 1):
            am.get_sprite("btn_unfocused_mid").blit(
                self.states[False], _ * slice_w, 0)
            am.get_sprite("btn_focused_mid").blit(
                self.states[True], _ * slice_w, 0)
        am.get_sprite("btn_unfocused_end").blit(
            self.states[False], self.w - slice_w, 0)
        am.get_sprite("btn_focused_end").blit(
            self.states[True], self.w - slice_w, 0)

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


class Keyboard:
    """In-game keyboard for typing characters.

    Attributes:
        game: The game instance.
        x: The x-coordinate of the keyboard.
        y: The y-coordinate of the keyboard.
        font: The font used for rendering characters.
        square_size: The size of each character square.
        width: The width of the keyboard.
        height: The height of the keyboard.
        layouts: A dictionary of keyboard layouts (lowercase and uppercase).
        row: The current row of the focused key.
        col: The current column of the focused key.
        buffer: The buffer of characters typed by the user.
    """

    def __init__(self, game: MLXApp, x: int, y: int) -> None:
        """Initialize the keyboard with the given game instance and position.

        Args:
            game: game instance.
            x: X-coordinate of the keyboard.
            y: Y-coordinate of the keyboard.
        """
        self.game = game
        self.x, self.y = x, y

        self.font = self.game.am.get_font('minecraft')
        char_width = self.font['m'][1]
        char_height = self.font.atlas.height
        self.pad = 8
        self.margin = 5
        self.border = 3

        self.square_size = max(char_width, char_height) + \
            (self.margin + self.border) * 2
        self.width = (self.square_size + self.pad +
                      (self.border + self.margin) * 2) * 10
        self.height = (self.square_size + self.pad +
                       (self.border + self.margin) * 2) * 3

        self.layouts = {
            True: Sprite.blank(self.width, self.height),
            False: Sprite.blank(self.width, self.height)
        }

        # Characters for lowercase and uppercase layouts
        self._chars_lc = ["qwertyuiop", "↑asdfghjkl", "zxcvbnm–←"]
        self._chars_uc = ["QWERTYUIOP", "↑ASDFGHJKL", "ZXCVBNM–←"]

        # Whether the caps lock is on
        self._caps_lock = False
        self.row, self.col = 0, 0
        self.buffer = ""

        self._render_keyboard()
        self._set_key_color(0xFFFFFFFF)

        self.game.bind_key(KEY_SPACE, self._type_char)
        self.game.bind_key(KEY_UP, self._focus_up)
        self.game.bind_key(KEY_DOWN, self._focus_down)
        self.game.bind_key(KEY_RIGHT, self._focus_right)
        self.game.bind_key(KEY_LEFT, self._focus_left)

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
                    self.layouts[True], char.upper(), x, y, 0x7FFFFFFF)
                x += self.square_size + self.pad
            y += self.square_size + self.pad

    def _draw_char(
        self, target: Sprite, char: str, x: int, y: int, color: int
    ) -> None:
        """Draw a character and its border on the target sprite at (x, y).

        Args:
            target (Sprite): the target sprite to draw on.
            char (str): the character to draw.
            x (int): the x-coordinate of the top-left corner.
            y (int): the y-coordinate of the top-left corner.
            color (int): the color to use for the character.
        """
        target.pixels[
            y + self.border:y + self.square_size - self.border,
            x: x + self.border
        ] = color
        target.pixels[
            y + self.border:y + self.square_size - self.border,
            x + self.square_size - self.border:x + self.square_size
        ] = color
        target.pixels[
            y: y + self.border,
            x + self.border: x + self.square_size - self.border
        ] = color
        target.pixels[
            y + self.square_size - self.border:y + self.square_size,
            x + self.border:x + self.square_size - self.border
        ] = color

        self.font.draw_text(
            target, char,
            x + self.pad + self.border + self.margin,
            y + self.border + self.margin,
            color
        )

    def draw(self) -> None:
        """Draw the keyboard to the window."""
        self.layouts[self._caps_lock].draw_to_window(
            self.game.win_ptr, self.x, self.y
        )

    def _key_coords(self) -> tuple[int, int]:
        """Get the coordinates of the current key.

        Returns:
            tuple[int, int]: (x, y) coordinates of the current key.
        """
        return (
            self.col * (self.square_size + self.pad),
            self.row * (self.square_size + self.pad)
        )

    def _set_key_color(self, color: int) -> None:
        """Set the color of the current key to the given color."""
        x, y = self._key_coords()
        char = self._curr_layout()[self.row][self.col]

        self.layouts[self._caps_lock].pixels[
            y: y + self.square_size,
            x: x + self.square_size
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
        self.row = min(2, self.row + 1)
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

        if char == '↑':
            self._caps_lock = not self._caps_lock
            self._set_key_color(0xFFFFFFFF)
        elif char == '–':
            self.buffer += ' '
        elif char == '←':
            self.buffer = self.buffer[:-1]
        else:
            self.buffer += char
