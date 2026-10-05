"""Module containing the Ghosts classes and its states."""

import math
from abc import ABC, abstractmethod
from collections import deque
from enum import Enum, auto

from mlx_wrapper import MLXApp, Sprite

from pacman.base import MovingEntity
from pacman.hitbox import Hitbox


class GhostState(Enum):
    """Possible behavioral states of a ghost.

    Attributes:
        SCATTER: Ghost retreats to and roams around its home corner.
        CHASE: Ghost actively pursues its target cell (Pac-Man).
        FRIGHTENED: Ghost flees and can be eaten by Pac-Man.
        EATEN: Ghost has been eaten and returns to its respawn point.
    """

    SCATTER = auto()
    CHASE = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class Ghost(ABC, MovingEntity):
    """Abstract base class for all ghosts in the game.

    Handles pathfinding (BFS), state management, and path visualization
    shared by all ghost types. Subclasses must implement `chase_mode` to
    define how the ghost selects its target cell while chasing.

    Attributes:
        hitbox (Hitbox): Collision hitbox of the ghost.
        state (GhostState): Current behavioral state of the ghost.
        target_cell (tuple[int, int]): Grid cell the ghost is pathing towards.
        path (list[tuple[int, int]]): Sequence of cells from the ghost's
            current position to its target cell.
        path_color (int): Color used when visualizing the ghost's path.
        drawable_path (Sprite): Blank sprite used to draw the visualized
            path onto.
    """

    DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))

    def __init__(
        self,
        game: MLXApp,
        corner: tuple[int, int],
        speed: int,
        path_color: int,
    ) -> None:
        """Initialize the ghost.

        Args:
            game (MLXApp): Game instance.
            corner (tuple[int, int]): Starting cell position of the ghost,
                typically its home corner.
            speed (int): Speed of the ghost.
            path_color (int): Color used when visualizing the ghost's path.
        """
        super().__init__(game, corner, speed)
        self.hitbox = Hitbox(3, 4, 24, 24)
        self.state = GhostState.CHASE
        self.corner = corner
        self.target_cell: tuple[int, int] = corner
        self.path: list[tuple[int, int]] = []
        self.path_color = path_color
        self.drawable_path = Sprite.blank(
            game.maze.canvas.width, game.maze.canvas.height
        )

    def at_tile_center(self) -> None:
        """Advance the ghost along its path when it reaches a tile center.

        Pops the current cell off the path if reached, then sets the next
        direction towards the upcoming cell in the path. If the path is
        no longer valid (e.g. the next tile isn't adjacent), recomputes it
        via `find_path`.
        """
        if self.path and self.path[0] == self.curr_cell:
            self.path.pop(0)

        if self.path:
            next_tile = self.path[0]
            raw_dx = next_tile[0] - self.curr_cell[0]
            raw_dy = next_tile[1] - self.curr_cell[1]

            if abs(raw_dx) + abs(raw_dy) != 1:
                self.find_path()
                if not self.path:
                    return
                next_tile = self.path[0]
                raw_dx = next_tile[0] - self.curr_cell[0]
                raw_dy = next_tile[1] - self.curr_cell[1]

            self.next_dx = raw_dx
            self.next_dy = raw_dy

    def find_path(self) -> None:
        """Compute the shortest path to `target_cell` using BFS.

        Walks the maze grid breadth-first from the ghost's current cell,
        avoiding walls and the cell directly behind the ghost (to prevent
        immediate reversal), and stores the resulting path (excluding the
        starting cell) in `self.path`. If no path is found, `self.path` is
        left unchanged.
        """
        visited: set = set(self.curr_cell)

        walkable_cells = sum([
            1 for dx, dy in self.DIRECTIONS
            if self._is_walkable(
                self.curr_cell[0] + dx, self.curr_cell[1] + dy)
        ])
        if (self.dx != 0 or self.dy != 0) and walkable_cells > 1:
            visited.add((
                self.curr_cell[0] - self.dx,
                self.curr_cell[1] - self.dy,
            ))

        q = deque([(self.curr_cell, [self.curr_cell])])
        while q:
            curr, path = q.popleft()

            if curr == self.target_cell:
                self.path = path[1:]
                return

            for dx, dy in self.DIRECTIONS:
                next_x, next_y = curr[0] + dx, curr[1] + dy
                if (
                    self._is_walkable(next_x, next_y)
                    and (next_x, next_y) not in visited
                ):
                    visited.add((next_x, next_y))
                    q.append(((next_x, next_y), path + [(next_x, next_y)]))

    def set_target(self, target: tuple[int, int]) -> None:
        """Set the ghost's target.

        Args:
            target (tuple[int, int]): New target cell.
        """
        self.target_cell = target

    def visualize_path(self) -> None:
        """Draw the ghost's current path onto the maze for debugging.

        Renders a line segment between each pair of consecutive cells in
        `self.path` using `path_color`, then draws the result to the game
        window. Does nothing if the path has fewer than two cells.
        """
        self.drawable_path.fill(0)

        if len(self.path) < 2:
            return

        half_cell = self.CELL_SIZE // 2
        thickness = 6
        half_thickness = thickness // 2

        for i in range(len(self.path) - 1):
            c1, r1 = self.path[i]
            c2, r2 = self.path[i + 1]

            x1 = c1 * self.CELL_SIZE + half_cell
            y1 = r1 * self.CELL_SIZE + half_cell
            x2 = c2 * self.CELL_SIZE + half_cell
            y2 = r2 * self.CELL_SIZE + half_cell

            min_x = min(x1, x2) - half_thickness
            max_x = max(x1, x2) + half_thickness
            min_y = min(y1, y2) - half_thickness
            max_y = max(y1, y2) + half_thickness

            self.drawable_path.pixels[
                min_y: max_y, min_x: max_x
            ] = self.path_color

        self.drawable_path.draw_to_window(
            self.game.win_ptr, 0, self.game.maze.y_offset
        )

    def scatter_mode(self) -> None:
        """Handle behavior while in `GhostState.SCATTER`."""

    @abstractmethod
    def chase_mode(self) -> None:
        """Handle behavior while in `GhostState.CHASE`.

        Must be implemented by subclasses to set `target_cell` (and
        typically call `find_path`) according to the ghost's unique
        chasing behavior.
        """

    def frightened_mode(self) -> None:
        """Handle behavior while in `GhostState.FRIGHTENED`."""

    def eaten_mode(self) -> None:
        """Handle behavior while in `GhostState.EATEN`."""

    def update(self) -> None:
        """Update the ghost for the current frame.

        Dispatches to the handler matching the ghost's current `state`,
        finds a path to the target cell, and moves the ghost along it.
        """
        if self.state == GhostState.CHASE:
            self.chase_mode()
        elif self.state == GhostState.SCATTER:
            self.scatter_mode()
        elif self.state == GhostState.FRIGHTENED:
            self.frightened_mode()
        elif self.state == GhostState.EATEN:
            self.eaten_mode()

        self.find_path()
        super().move()

    def draw(self) -> None:
        """Draw the ghost to the window."""
        # TODO: Check if path visualization is enabled in cheat mode then
        # call `visualize_path` before drawing
        self.visualize_path()
        super().draw()


class Pinky(Ghost):
    """Pinky ghost implementation.

    Pinky's chase behavior is an ambush strategy: instead of targeting
    Pac-Man's current cell directly, it targets a cell a few tiles ahead
    of Pac-Man in whichever direction Pac-Man is currently facing.

    Attributes:
        arrows (dict[str, Sprite]): Sprites for the directional arrow shown
            at Pinky's target cell, keyed by direction ("up", "down",
            "left", "right").
        arrow (Sprite): Arrow sprite currently selected based on Pac-Man's
            direction.
    """

    def __init__(
        self,
        game: MLXApp,
    ) -> None:
        """Initialize Pinky with the given game instance.

        Args:
            game (MLXApp): Game instance.
            corner (tuple[int, int]): Starting cell position of the ghost,
                typically its home corner.
            speed (int): Speed of the ghost.
            path_color (int): Color used when visualizing the ghost's path.
        """
        super().__init__(game, (1, 1), 3, 0x80FF00FF)
        self.curr_state = "down"
        self._add_animation('up', game.am.get_animated_sprite('pinky_up'))
        self._add_animation('down', game.am.get_animated_sprite('pinky_down'))
        self._add_animation('left', game.am.get_animated_sprite('pinky_left'))
        self._add_animation(
            'right', game.am.get_animated_sprite('pinky_right')
        )
        self.animations[self.curr_state].play()
        self.arrows = {
            'up': game.am.get_sprite('pinky_arrow_up'),
            'down': game.am.get_sprite('pinky_arrow_down'),
            'left': game.am.get_sprite('pinky_arrow_left'),
            'right': game.am.get_sprite('pinky_arrow_right'),
        }
        self.arrow = self.arrows[self.curr_state]
        for arrow in self.arrows.values():
            arrow.pixels[:] &= 0x80FFFFFF

    def chase_mode(self) -> None:
        """Set Pinky's target to a cell ahead of Pac-Man in chase mode.

        Targets the cell 3 tiles ahead of Pac-Man in the direction Pac-Man
        is currently facing. Falls back to Pac-Man's current cell if Pinky
        has no path or Pac-Man's direction is unrecognized.
        """
        if self.path:
            if self.game.pacman.curr_state == "up":
                x = self.game.pacman.curr_cell[0]
                y = self.game.pacman.curr_cell[1] - 3
            elif self.game.pacman.curr_state == "down":
                x = self.game.pacman.curr_cell[0]
                y = self.game.pacman.curr_cell[1] + 3
            elif self.game.pacman.curr_state == "left":
                x = self.game.pacman.curr_cell[0] - 3
                y = self.game.pacman.curr_cell[1]
            elif self.game.pacman.curr_state == "right":
                x = self.game.pacman.curr_cell[0] + 3
                y = self.game.pacman.curr_cell[1]
            else:
                x = self.game.pacman.curr_cell[0]
                y = self.game.pacman.curr_cell[1]
        else:
            x = self.game.pacman.curr_cell[0]
            y = self.game.pacman.curr_cell[1]
        self.set_target((x, y))

    def visualize_path(self) -> None:
        """Draw the ghost's path and a directional arrow to the window.

        Draws the base path visualization, then overlays an arrow sprite
        pointing in the direction Pac-Man is currently facing, placed near
        Pinky's ambush target cell.
        """
        super().visualize_path()
        if (
            self.game.pacman.curr_state == "appear"
            or self.game.pacman.curr_state == "up"
        ):
            self.arrows["up"].draw_to_window(
                self.game.win_ptr, self.game.pacman.curr_cell[0] * 32,
                self.game.pacman.curr_cell[1] * 32 - 32
            )
        elif self.game.pacman.curr_state == "down":
            self.arrows["down"].draw_to_window(
                self.game.win_ptr, self.game.pacman.curr_cell[0] * 32,
                self.game.pacman.curr_cell[1] * 32 + 96
            )
        elif self.game.pacman.curr_state == "left":
            self.arrows["left"].draw_to_window(
                self.game.win_ptr, self.game.pacman.curr_cell[0] * 32 - 100,
                self.game.pacman.curr_cell[1] * 32 + 75
            )
        elif self.game.pacman.curr_state == "right":
            self.arrows["right"].draw_to_window(
                self.game.win_ptr, self.game.pacman.curr_cell[0] * 32,
                self.game.pacman.curr_cell[1] * 32 + 75
            )


class Blinky(Ghost):
    """Blinky ghost implementation."""

    def __init__(self, game: MLXApp) -> None:
        """Initialize Blinky with the given game instance.

        Args:
            game: The game instance to associate with this ghost.
        """
        super().__init__(game, (len(game.maze.grid[0]) - 2, 1), 3, 0x80FF0000)

        self._add_animation('up', game.am.get_animated_sprite('blinky_up'))
        self._add_animation('down', game.am.get_animated_sprite('blinky_down'))
        self._add_animation('left', game.am.get_animated_sprite('blinky_left'))
        self._add_animation(
            'right', game.am.get_animated_sprite('blinky_right')
        )
        self.animations['left'].play()

    def chase_mode(self) -> None:
        """Set Blinky's target to Pac-Man's current cell in chase mode."""
        self.set_target(self.game.pacman.curr_cell)


class Clyde(Ghost):
    """Clyde ghost implementation.

    Attributes:
        clyde_circle: green circle sprite used for visualizing Clyde's aggro
            range.
    """

    def __init__(self, game: MLXApp) -> None:
        """Initialize Clyde with the game instance and set initial state.

        Args:
            game: The MLXApp instance.
        """
        super().__init__(game, (1, len(game.maze.grid) - 2), 3, 0x8000FF00)
        self.target_cell = self.game.pacman.curr_cell

        self.curr_state = 'right'
        self._add_animation('up', game.am.get_animated_sprite('clyde_up'))
        self._add_animation('down', game.am.get_animated_sprite('clyde_down'))
        self._add_animation('left', game.am.get_animated_sprite('clyde_left'))
        self._add_animation(
            'right', game.am.get_animated_sprite('clyde_right'))
        self.animations['right'].play()

        self.circle = game.am.get_sprite('clyde_circle')
        self.drawable_path = Sprite.blank(
            game.maze.canvas.width, game.maze.canvas.height
        )

    def dist(self) -> float:
        """Calculate the euclidean distance to the player.

        Returns:
            float: distance to the player.
        """
        pac_x, pac_y = self.game.pacman.x, self.game.pacman.y
        return math.sqrt(
            (pac_x - self.x) ** 2 + (pac_y - self.y) ** 2
        )

    def chase_mode(self) -> None:
        """Clyde's chase mode behavior.

        When Clyde is within 150px radius of the player he will go to his home
        corner, otherwise he will chase the player.
        When the home corner is set, Clyde waits until he exceeds the
        threshold (320px) before going back to chase the player.

        The aggro circle is drawn at half alpha while Clyde is retreating to
        his corner, and restored to full alpha when he resumes chasing.
        """
        if self.dist() < 320 and self.target_cell == self.corner:
            return
        if self.dist() > 150:
            self.target_cell = self.game.pacman.curr_cell
            self.circle.pixels[self.circle.pixels > 0] |= 0xFF000000
        else:
            self.target_cell = self.corner
            self.circle.pixels[self.circle.pixels > 0] &= 0x7FFFFFFF

    def visualize_path(self) -> None:
        """Draw the ghost's path and aggro circle to the window."""
        super().visualize_path()
        self.circle.draw_to_window(
            self.game.win_ptr,
            self.game.pacman.x - 154,
            self.game.pacman.y - 154 + self.game.maze.y_offset
        )


class Inky(Ghost):
    def __init__(self, game: MLXApp) -> None:
        super().__init__(game, (len(game.maze.grid) - 2, len(game.maze.grid) - 2), 3, 0xA4CFEBFF)

        self._add_animation('up', game.am.get_animated_sprite('inky_up'))
        self._add_animation('down', game.am.get_animated_sprite('inky_down'))
        self._add_animation('left', game.am.get_animated_sprite('inky_left'))
        self._add_animation(
            'right', game.am.get_animated_sprite('inky_right')
        )
        self.animations['up'].play()

        self.arrows = {
            'up': game.am.get_sprite('inky_arrow_up'),
            'down': game.am.get_sprite('inky_arrow_down'),
            'left': game.am.get_sprite('inky_arrow_left'),
            'right': game.am.get_sprite('inky_arrow_right'),
        }
        self.arrow = self.arrows[self.curr_state]
        for arrow in self.arrows.values():
            arrow.pixels[:] &= 0x80FFFFFF

    def chase_mode(self) -> None:
        if self.game.pacman.curr_state == "down":
            x = self.game.pacman.curr_cell[0]
            y = self.game.pacman.curr_cell[1] - 2
        elif self.game.pacman.curr_state == "up":
            x = self.game.pacman.curr_cell[0]
            y = self.game.pacman.curr_cell[1] + 2
        elif self.game.pacman.curr_state == "right":
            x = self.game.pacman.curr_cell[0] - 2
            y = self.game.pacman.curr_cell[1]
        elif self.game.pacman.curr_state == "left":
            x = self.game.pacman.curr_cell[0] + 2
            y = self.game.pacman.curr_cell[1]
        else:
            x = self.game.pacman.curr_cell[0]
            y = self.game.pacman.curr_cell[1]
        self.set_target((x, y))

    def visualize_path(self) -> None:
        super().visualize_path()
        if (
            self.game.pacman.curr_state == "appear"
            or self.game.pacman.curr_state == "up"
        ):
            self.arrows["down"].draw_to_window(
                self.game.win_ptr, self.game.pacman.curr_cell[0] * 32,
                self.game.pacman.curr_cell[1] * 32 + 91
            )
        elif self.game.pacman.curr_state == "down":
            self.arrows["up"].draw_to_window(
                self.game.win_ptr, self.game.pacman.curr_cell[0] * 32,
                self.game.pacman.curr_cell[1] * 32 + 16
            )
        elif self.game.pacman.curr_state == "left":
            self.arrows["right"].draw_to_window(
                self.game.win_ptr, self.game.pacman.curr_cell[0] * 32 + 16,
                self.game.pacman.curr_cell[1] * 32 + 75
            )
        elif self.game.pacman.curr_state == "right":
            self.arrows["left"].draw_to_window(
                self.game.win_ptr, self.game.pacman.curr_cell[0] * 32 - 64,
                self.game.pacman.curr_cell[1] * 32 + 75
            )
