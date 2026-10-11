"""Module containing base classes for the game."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

import numpy as np
from mlx_wrapper import AnimatedSprite, AssetManager, Sprite

from pacman.maze import Maze
from pacman.parser import Config

if TYPE_CHECKING:
    from pacman.game import Game


class GameContext:
    """App-wide services shared by scenes/components.

    Should be set before any scene is initialized.

    Attributes:
        game: Game instance.
        am: Asset manager.
        config: Game configuration.
    """

    _current: ClassVar[GameContext | None] = None

    def __init__(self, game: Game, am: AssetManager, config: Config) -> None:
        """Initialize the game context.

        Args:
            game: The game instance.
            am: The asset manager.
            config: The game configuration.
        """
        self.game = game
        self.am = am
        self.config = config

    @classmethod
    def set_context(cls, context: GameContext) -> None:
        """Set the current game context.

        Args:
            context: Game context to set.
        """
        cls._current = context

    @classmethod
    def get_context(cls) -> GameContext:
        """Get the current game context.

        Returns:
            The current game context.

        Raises:
            RuntimeError: If no game context is set.
        """
        if cls._current is None:
            raise RuntimeError("No game context is set.")
        return cls._current


class StarField:
    """Animated background of moving stars."""

    def __init__(self, width: int, height: int, count: int = 300) -> None:
        """Initialize the star field.

        Args:
            width: Width of the canvas.
            height: Height of the canvas.
            count: Number of stars to generate.
        """
        self._stars = np.random.randint(
            low=[0, 0], high=[width, height], size=(count, 2)
        )

    def draw(self, canvas: Sprite) -> None:
        """Draw the stars on the given canvas.

        Args:
            canvas: Canvas to draw on.
        """
        self._stars += 1
        self._stars[:, 0] %= canvas.width
        self._stars[:, 1] %= canvas.height
        canvas.fill(0xFF080000)

        star_size = 2
        for x, y in self._stars:
            canvas.pixels[y: y + star_size, x: x + star_size] = 0xFFFFFFFF


class Scene(ABC):
    """Base class for all scenes in the game.

    Attributes:
        ctx: game context.
        canvas: canvas to draw on.
    """

    USE_STARFIELD: ClassVar[bool] = True

    def __init__(self) -> None:
        """Initialize the scene."""
        self.ctx = GameContext.get_context()
        self.canvas = Sprite.blank(self.game.width, self.game.height)
        # initialize starfield if enabled
        self._starfield = (
            StarField(self.game.width, self.game.height)
            if self.USE_STARFIELD else None
        )

    @property
    def game(self) -> Game:
        """Game: game instance."""
        return self.ctx.game

    @property
    def am(self) -> AssetManager:
        """AssetManager: asset manager."""
        return self.ctx.am

    @property
    def config(self) -> Config:
        """Config: game configuration."""
        return self.ctx.config

    @abstractmethod
    def mount(self) -> None:
        """Mount the scene."""

    @abstractmethod
    def unmount(self) -> None:
        """Unmount the scene."""

    @abstractmethod
    def update(self) -> None:
        """Update the scene."""

    # TODO: Rename to draw_background
    def draw_starfield(self) -> None:
        """Draw the starfield."""
        if self._starfield:
            self._starfield.draw(self.canvas)
        else:
            self.canvas.fill(0xFF000000)

    def draw(self) -> None:
        """Draw the scene."""
        self.canvas.draw_to_window(0, 0)


class MovingEntity:
    """Base class for all moving entities in the game.

    Attributes:
        maze: Maze instance.
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
        start_cell: Starting cell position.
        curr_state: Current state of the entity.
        animations: Animations of the entity.
    """

    DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))
    CELL_SIZE = 32

    def __init__(
        self,
        am: AssetManager,
        maze: Maze,
        start_cell: tuple[int, int],
        speed: int
    ) -> None:
        """Initialize the moving entity.

        Args:
            am: AssetManager for loading assets.
            maze: Maze instance.
            start_cell: Starting cell position.
            speed: Speed of the entity.
        """
        self.maze = maze
        self.am = am
        self.gw = len(maze.grid[0]) - 1
        self.gh = len(maze.grid) - 1
        self.start_cell = start_cell
        self.curr_cell = start_cell

        self.x = self.curr_cell[0] * 32
        self.y = self.curr_cell[1] * 32
        self.speed = speed

        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

        self.animation_key = 'left'
        self.animations: dict[str, AnimatedSprite] = {}

    def _add_animation(self, key: str, animation: AnimatedSprite) -> None:
        """Add an animation to the entity's animations dictionary.

        Args:
            state: State name for the animation.
            animation: AnimatedSprite to add.
        """
        self.animations[key] = animation

    def _is_walkable(self, gx: int, gy: int) -> bool:
        """Whether the given grid position is walkable.

        Args:
            gx: x grid position.
            gy: y grid position.

        Returns:
            bool: True if the position is walkable, False otherwise.
        """
        if gx < 0 or gx >= self.gw or gy < 0 or gy >= self.gh:
            return False
        return bool(self.maze.grid[gy][gx] == 0)

    def _update_direction(self, new_dx: int, new_dy: int) -> None:
        """Update the entity's direction and state based on the new direction.

        Args:
            new_dx: new x direction.
            new_dy: new y direction.
        """
        old_state = self.animation_key
        self.dx = new_dx
        self.dy = new_dy

        if self.dx == 1:
            self.animation_key = 'right'
        elif self.dx == -1:
            self.animation_key = 'left'
        elif self.dy == 1:
            self.animation_key = 'down'
        elif self.dy == -1:
            self.animation_key = 'up'

        if old_state != self.animation_key:
            self.animations[self.animation_key].play()

    def at_tile_center(self) -> None:
        """Override to handle when the entity reaches the center of a tile."""

    def reset(self) -> None:
        """Override to reset the entity to its initial state."""
        self.curr_cell = self.start_cell
        self.dx, self.dy = 0, 0
        self.next_dx, self.next_dy = 0, 0
        self.animation_key = "left"
        self.x = self.curr_cell[0] * 32
        self.y = self.curr_cell[1] * 32

        for animation in self.animations.values():
            animation.reset()

    def update_animation(self, dt: float) -> None:
        """Update the entity's animation based on its current state."""
        self.animations[self.animation_key].update(dt)

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
                    if self.animation_key in ('left', 'right', 'up', 'down'):
                        self.animations[self.animation_key].stop()
                    break

            self.x += self.dx
            self.y += self.dy
            remaining_steps -= 1

    def draw(self) -> None:
        """Draw the entity to the window."""
        self.animations[self.animation_key].draw_to_window(
            self.x, self.y + self.maze.y_offset
        )
