"""Module containing base classes for the game."""


from abc import ABC, abstractmethod
from typing import Callable

import numpy as np
from mlx_wrapper import (
    KEY_DOWN,
    KEY_ENTER,
    KEY_UP,
    AnimatedSprite,
    MLXApp,
    Sprite,
)

from pacman.ui import Button


class Scene(ABC):
    """Base class for all scenes in the game."""

    def __init__(self, game: MLXApp) -> None:
        """Initialize the scene.

        game: Game instance.
        """
        self.game = game
        self.canvas = Sprite.blank(game.width, game.height)
        self.canvas.fill(0xFF180000)
        self.buttons: list[Button] = []
        self.current_btn = -1
        self._stars = np.random.randint(
            low=[0, 0], high=[game.width, game.height], size=(300, 2)
        )

    @abstractmethod
    def mount(self) -> None:
        """Mount the scene."""

    @abstractmethod
    def unmount(self) -> None:
        """Unmount the scene."""

    @abstractmethod
    def update(self) -> None:
        """Update the scene."""

    @abstractmethod
    def draw(self, x: int, y: int) -> None:
        """Draw the scene.

        x: X-coordinate to draw the scene.
        y: Y-coordinate to draw the scene.
        """

    def draw_stars(self) -> None:
        """Draw a background animation of moving stars."""
        self._stars += 1
        self._stars[:, 0] %= self.canvas.width
        self._stars[:, 1] %= self.canvas.height
        self.canvas.fill(0xFF180000)

        star_size = 2
        for x, y in self._stars:
            x_end = min(x + star_size, self.canvas.width)
            y_end = min(y + star_size, self.canvas.height)
            self.canvas.pixels[y:y_end, x:x_end] = 0xFFFFFFFF


class Menu(Scene, ABC):
    """Abstract base class for menus.

    Attributes:
        game: Game instance.
        canvas: canvas sprite for drawing.
        buttons: List of buttons in the menu.
        current_btn: Index of the currently focused button.

    """

    def __init__(self, game: MLXApp) -> None:
        """Initialize the menu with the given MLX application and dimensions.

        Args:
            game: Game instance.
        """
        super().__init__(game)
        self.canvas = Sprite.blank(game.width, game.height)
        self.buttons: list[Button] = []
        self.current_btn = -1
        self._stars = np.random.randint(
            low=[0, 0], high=[game.width, game.height], size=(300, 2)
        )

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

    @abstractmethod
    def update(self) -> None:
        """Update the menu state."""

    def add_button(self, text: str, callback: Callable[..., None]) -> None:
        """Add a button to the menu.

        Args:
            text: The text to display on the button.
            callback: The function to call when the
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
            y: Starting y-coordinate for the first button.
            y_pad: Padding between buttons.

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


class MovingEntity:
    """Base class for all moving entities in the game.

    Attributes:
        game: Game instance.
        gw: width of the maze grid.
        gh: height of the maze grid.
        curr_cell: current cell position.
        x: X-coordinate of the entity.
        y: Y-coordinate of the entity.
        speed: Speed of the entity.
        dx: X-direction of the entity.
        dy: Y-direction of the entity.
        next_dx: Next x-direction of the entity.
        next_dy: Next y-direction of the entity.
        curr_state: current state of the entity.
        animations: Animations of the entity.
    """

    CELL_SIZE = 32

    def __init__(
        self, game: MLXApp, start_cell: tuple[int, int], speed: int
    ) -> None:
        """Initialize the moving entity.

        Args:
            game: Game instance.
            start_cell: Starting cell position.
            speed: Speed of the entity.
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
            new_dx: new x direction.
            new_dy: new y direction.
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
