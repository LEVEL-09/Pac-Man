"""Pac-Man player character."""

from typing import Callable

from mlx_wrapper import AssetManager

from pacman.base import MovingEntity
from pacman.hitbox import Hitbox
from pacman.maze import Maze


class Player(MovingEntity):
    """Represents the player character in the game.

    Attributes:
        hitbox: Hitbox for the player.
    """

    def __init__(self, am: AssetManager, maze: Maze, speed: int, on_eat: Callable[..., None]) -> None:
        """Initialize the player character.

        Args:
            am: AssetManager instance.
            maze: Maze instance.
            speed: Movement speed of the player.
        """
        gw = len(maze.grid[0]) - 1
        gh = len(maze.grid) - 1
        start_cell = (
            (gw // 2) - ((gw // 2) % 2 == 0),
            (gh // 2) - ((gh // 2) % 2 == 0)
        )
        super().__init__(am, maze, start_cell, speed)
        self.hitbox = Hitbox(3, 4, 24, 24)

        self.animation_key = "appear"
        self._add_animation("up", self.am.get_animated_sprite("pac_up"))
        self._add_animation("down", self.am.get_animated_sprite("pac_down"))
        self._add_animation("left", self.am.get_animated_sprite("pac_left"))
        self._add_animation("right", self.am.get_animated_sprite("pac_right"))
        self._add_animation("death", self.am.get_animated_sprite("pac_death"))
        self._add_animation(
            "appear", self.am.get_animated_sprite("pac_appear")
        )
        self.animations[self.animation_key].play()
        self.at_tile_center = on_eat

    def reset(self) -> None:
        """Reset the player to its initial state."""
        super().reset()
        self.animation_key = "appear"
        self.animations[self.animation_key].play()

    def die(self) -> None:
        """Die the player."""
        self.animation_key = "death"
        self.animations[self.animation_key].play()

    def move_up(self) -> None:
        """Set the player's next direction to move up."""
        self.next_dx, self.next_dy = 0, -1

    def move_down(self) -> None:
        """Set the player's next direction to move down."""
        self.next_dx, self.next_dy = 0, 1

    def move_left(self) -> None:
        """Set the player's next direction to move left."""
        self.next_dx, self.next_dy = -1, 0

    def move_right(self) -> None:
        """Set the player's next direction to move right."""
        self.next_dx, self.next_dy = 1, 0
