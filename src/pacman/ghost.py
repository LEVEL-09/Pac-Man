from abc import ABC, abstractmethod
from collections import deque
from enum import Enum, auto

from mlx_wrapper import MLXApp, Sprite

from pacman.base import MovingEntity
from pacman.hitbox import Hitbox


class GhostState(Enum):
    SCATTER = auto()
    CHASE = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class Ghost(ABC, MovingEntity):
    def __init__(
        self,
        game: MLXApp,
        corner: tuple[int, int],
        speed: int,
        path_color: int,
    ) -> None:
        super().__init__(game, corner, speed)
        self.hitbox = Hitbox(3, 4, 24, 24)
        self.state = GhostState.CHASE
        self.target_cell: tuple[int, int]
        self.path: list[tuple[int, int]]
        self.path_color = path_color
        self.drawable_path = Sprite.blank(
            game.maze.canvas.width, game.maze.canvas.height
        )

    def at_tile_center(self) -> None:
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
        visited: set = set(self.curr_cell)

        if self.dx != 0 or self.dy != 0:
            visited.add((
                self.curr_cell[0] - self.dx,
                self.curr_cell[1] - self.dy,
            ))

        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        q = deque([(self.curr_cell, [self.curr_cell])])

        while q:
            curr, path = q.popleft()

            if curr == self.target_cell:
                self.path = path[1:]
                return

            for dx, dy in directions:
                next_x, next_y = curr[0] + dx, curr[1] + dy
                if (
                    self._is_walkable(next_x, next_y)
                    and (next_x, next_y) not in visited
                ):
                    visited.add((next_x, next_y))
                    q.append(((next_x, next_y), path + [(next_x, next_y)]))

    def set_target(self, target: tuple[int, int]) -> None:
        self.target = target

    def visualize_path(self) -> None:
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
        pass

    @abstractmethod
    def chase_mode(self) -> None:
        pass

    def frightened_mode(self) -> None:
        pass

    def eaten_mode(self) -> None:
        pass

    def update(self) -> None:
        if self.state == GhostState.CHASE:
            self.chase_mode()
        elif self.state == GhostState.SCATTER:
            self.scatter_mode()
        elif self.state == GhostState.FRIGHTENED:
            self.frightened_mode()
        elif self.state == GhostState.EATEN:
            self.eaten_mode()

        super().move()
