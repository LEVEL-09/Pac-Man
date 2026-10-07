"""Pac-Man player character."""

from mlx_wrapper import KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP, MLXApp, Sprite

from .base import MovingEntity
from .hitbox import Hitbox


class Player(MovingEntity):
    """Represents the player character in the game.

    Attributes:
        hitbox (Hitbox): hitbox of the player.
        curr_state (str): current state of the player.
        animations (dict[str, AnimatedSprite]): animations of the player.
    """

    def __init__(self, game: MLXApp) -> None:
        """Initialize the player character.

        Args:
            game (Game): Game instance.
        """
        gw = len(game.maze.grid[0]) - 1
        gh = len(game.maze.grid) - 1
        start_cell = (
            (gw // 2) - ((gw // 2) % 2 == 0),
            (gh // 2) - ((gh // 2) % 2 == 0)
        )
        super().__init__(game, start_cell, 4)
        self.hitbox = Hitbox(3, 4, 24, 24)

        self.curr_state = "appear"
        self._add_animation("up", game.am.get_animated_sprite("pac_up"))
        self._add_animation("down", game.am.get_animated_sprite("pac_down"))
        self._add_animation("left", game.am.get_animated_sprite("pac_left"))
        self._add_animation("right", game.am.get_animated_sprite("pac_right"))
        self._add_animation("death", game.am.get_animated_sprite("pac_death"))
        self._add_animation(
            "appear", game.am.get_animated_sprite("pac_appear"))
        self.animations[self.curr_state].play()

        game.bind_key(KEY_UP, self.move_up)
        game.bind_key(KEY_DOWN, self.move_down)
        game.bind_key(KEY_LEFT, self.move_left)
        game.bind_key(KEY_RIGHT, self.move_right)

        self.blank = Sprite.blank(32, 32)
        self.blank.fill(0xFF000000)

    def at_tile_center(self) -> None:
        """Handle when the player reaches the center of a tile."""
        # TODO: Add logic to increase score and notify when all
        # collectibles are collected
        pacgum_type = self.game.maze.collectibles.pop(self.curr_cell, None)
        if pacgum_type is not None:
            self.blank.blit(
                self.game.maze.canvas,
                self.curr_cell[0] * 32,
                self.curr_cell[1] * 32
            )

    def update(self) -> None:
        """Update the player's position and state."""
        if not self.animations['appear'].is_finished:
            self.animations[self.curr_state].update(self.game.dt)
            return

        super().move()

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
