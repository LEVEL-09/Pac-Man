"""Pac-Man player character."""

from mlx_wrapper import KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP, MLXApp

from pacman.hitbox import Hitbox

from .base import MovingEntity


class Player(MovingEntity):
    """Represents the player character in the game.

    Attributes:
        game (MLXApp): Game instance.
        maze_grid (list[list[int]]): maze grid.
        gw (int): width of the maze.
        gh (int): height of the maze.
        hitbox (Hitbox): hitbox of the player.
        curr_cell (tuple[int, int]): current cell the player is in.
        x (int): x-coordinate of the player.
        y (int): y-coordinate of the player.
        y_offset (int): y-offset of the player.
        speed (int): speed of the player.
        dx (int): x-direction of the player.
        dy (int): y-direction of the player.
        next_dx (int): next x-direction of the player.
        next_dy (int): next y-direction of the player.
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
        self.animations = {
            "up": game.am.get_animated_sprite("pac_up"),
            "down": game.am.get_animated_sprite("pac_down"),
            "left": game.am.get_animated_sprite("pac_left"),
            "right": game.am.get_animated_sprite("pac_right"),
            "death": game.am.get_animated_sprite("pac_death"),
            "appear": game.am.get_animated_sprite("pac_appear"),
        }
        self.animations[self.curr_state].play()

        game.bind_key(KEY_UP, self.move_up)
        game.bind_key(KEY_DOWN, self.move_down)
        game.bind_key(KEY_LEFT, self.move_left)
        game.bind_key(KEY_RIGHT, self.move_right)

    def at_tile_center(self) -> None:
        gum_type = self.game.maze.collectibles.pop(self.curr_cell, None)

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
