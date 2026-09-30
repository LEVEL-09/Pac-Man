"""Pac-Man player character."""

from mlx_wrapper import KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP, MLXApp


class Player:
    """Represents the player character in the game.

    Attributes:
        game (MLXApp): Game instance.
        maze_grid (list[list[int]]): maze grid.
        gw (int): width of the maze.
        gh (int): height of the maze.
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

    def __init__(self, game: MLXApp, y_offset: int) -> None:
        """Initialize the player character.

        Args:
            game (Game): Game instance.
            y_offset (int): y-offset of the player.
        """
        self.game = game
        self.maze_grid = game.maze.maze
        self.gw = len(self.maze_grid[0]) - 1
        self.gh = len(self.maze_grid) - 1
        maze_width = self.gw // 2
        maze_height = self.gh // 2

        self.curr_cell = (
            maze_width - (maze_width % 2 == 0),
            maze_height - (maze_height % 2 == 0),
        )
        self.x = self.curr_cell[0] * 32
        self.y = self.curr_cell[1] * 32
        self.y_offset = y_offset
        self.speed = 5
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

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

        self.appeared = False

    def _is_walkable(self, gx: int, gy: int) -> bool:
        """Whether the given grid position is walkable.

        Returns:
            bool: True if the position is walkable, False otherwise.
        """
        if gx < 0 or gx >= self.gw or gy < 0 or gy >= self.gh:
            return False
        return bool(self.maze_grid[gy][gx] == 0)

    def _update_direction(self, new_dx: int, new_dy: int) -> None:
        """Update player's direction and state based on the new direction.

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

    def update(self) -> None:
        """Update the player's position and state.

        Based on the current direction and speed, it moves the player along the
        current direction by one pixel per update to ensure smooth movement and
        no jitter.
        """
        if not self.animations['appear'].is_finished:
            self.animations[self.curr_state].update(self.game.dt)
            return
        if (self.dx != 0 and self.next_dx == -self.dx) or (
            self.dy != 0 and self.next_dy == -self.dy
        ):
            self._update_direction(self.next_dx, self.next_dy)

        remaining_steps = self.speed
        while remaining_steps > 0:
            if self.x % 32 == 0 and self.y % 32 == 0:
                self.curr_cell = (self.x // 32, self.y // 32)
                if (
                    (self.next_dx != 0 or self.next_dy != 0)
                    and self._is_walkable(
                        self.curr_cell[0] + self.next_dx,
                        self.curr_cell[1] + self.next_dy)
                ):
                    self._update_direction(self.next_dx, self.next_dy)
                if not self._is_walkable(
                    self.curr_cell[0] + self.dx, self.curr_cell[1] + self.dy
                ):
                    self.animations[self.curr_state].stop()
                    break

            self.x += self.dx
            self.y += self.dy
            remaining_steps -= 1

        self.animations[self.curr_state].update(self.game.dt)

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

    def draw(self) -> None:
        """Draw the player character to the window."""
        self.animations[self.curr_state].draw_to_window(
            self.game.win_ptr, self.x, self.y + self.y_offset
        )
