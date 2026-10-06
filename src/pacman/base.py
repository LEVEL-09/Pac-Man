"""Module containing base classes for the game."""


from abc import ABC, abstractmethod
from typing import Callable

from mlx_wrapper import AnimatedSprite, MLXApp, Sprite

from .ui import Button


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
        game (MLXApp): Game instance.
        canvas (Sprite): canvas sprite for drawing.
        buttons (list[Button]): List of buttons in the menu.
        current_btn (int): Index of the currently focused button.

    """

    def __init__(self, game: MLXApp, width: int, height: int) -> None:
        """Initialize the menu with the given MLX application and dimensions.

        Args:
            game (MLXApp): Game instance.
            width (int): Width of the menu canvas.
            height (int): Height of the menu canvas.
        """
        self.game = game
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
        self.buttons.append(Button(text, callback, self.game.am))

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

    def draw(self, x: int, y: int) -> None:
        """Draw the menu to the window.

        x: X-coordinate of the menu.
        y: Y-coordinate of the menu.
        """
        self.canvas.draw_to_window(self.game.win_ptr, x, y)
