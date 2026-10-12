"""Maze generation, autotiling, and rendering for the Pac-Man game.

This module exposes the `Maze` class, which wraps a
`~mazegenerator.MazeGenerator` to procedurally generate a maze
per level, converts the generated maze into an autotiled wall layout,
and renders it to the game window as a single composed sprite.
"""

import random
from enum import Enum, auto

from mazegenerator import MazeGenerator
from mlx_wrapper import AssetManager, Sprite


class PacGumType(Enum):
    """Types of Pac-Gum collectibles available in the maze."""

    REGULAR = auto()
    SUPER = auto()


class Maze:
    """Generates, autotiles, and renders the game's maze.

    Each level uses its own deterministic seed (derived from a single
    top-level seed) so that mazes are reproducible across runs while
    still differing from level to level.

    Attributes:
        mlx_app: The running MLX application/window used for
            rendering.
        width: The maze width, in cells.
        height: The maze height, in cells.
        maze_generator: Generates the raw maze layout for each level.
        seeds: Per-level seeds derived from the top-level seed.
        pacgum_sprite: The sprite for regular pacgum.
        spacgum_sprite: The sprite for super pacgum.
        collectibles: A dictionary of collectible positions and types.
    """

    def __init__(
        self,
        win_height: int,
        am: AssetManager,
        width: int,
        height: int,
        seed: int,
        levels_number: int
    ) -> None:
        """Initialize the maze generator and derive per-level seeds.

        Args:
            win_height: Height of the window.
            am: Asset manager instance.
            width: The maze width, in cells.
            height: The maze height, in cells.
            seed: The top-level seed used to deterministically derive
                one seed per level.
            levels_number: The number of levels to generate seeds for.
        """
        self.am = am
        self.width = width
        self.height = height
        self.y_offset = (win_height - (self.height * 2 + 1) * 32) // 2
        self.maze_generator = MazeGenerator(size=(width, height))

        random.seed(seed)
        self.seeds = [
            random.randint(0, 2**32 - 1) for _ in range(levels_number)
        ]

        self.pacgum_sprite = self.am.get_sprite('pacgum')
        self.spacgum_sprite = self.am.get_sprite('spacgum')
        self.create_maze_sprite(0)

        self.collectibles: dict[tuple[int, int], PacGumType]

        self.path_canvas = Sprite.blank(
            self.canvas.width, self.canvas.height
        )

    def create_maze_sprite(self, level: int) -> None:
        """Generate a level's maze and compose it into a single sprite.

        Generates the raw maze for the given level using its
        corresponding seed, converts it into an autotiled wall layout,
        and blits each non-empty wall tile onto a blank canvas sprite.
        Generates collectible positions and types for the maze.

        Args:
            level: The zero-based index of the level to generate.
        """
        self.maze_generator.generate(seed=self.seeds[level])
        self.grid = self._convert_to_autotiled(self.maze_generator.maze)

        self.canvas = Sprite.blank(len(self.grid[0]) * 32, len(self.grid) * 32)
        self.canvas.fill(0xFF000000)
        self.collectibles = {}

        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                if self.grid[y][x] != 0:
                    self.am.get_sprite(
                        f"wall{self.grid[y][x]:02d}"
                    ).blit(self.canvas, x * 32, y * 32)
                else:
                    is_corner = (x, y) in [
                        (1, 1), (len(self.grid[0]) - 2, 1),
                        (1, len(self.grid) - 2),
                        (len(self.grid[0]) - 2, len(self.grid) - 2)
                    ]
                    is_reachable = any(
                        self.grid[y + dy][x + dx] == 0
                        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]
                    )
                    if is_reachable:
                        if is_corner:
                            self.spacgum_sprite.blit(
                                self.canvas, x * 32, y * 32)
                            self.collectibles[(x, y)] = PacGumType.SUPER
                        else:
                            self.pacgum_sprite.blit(
                                self.canvas, x * 32, y * 32)
                            self.collectibles[(x, y)] = PacGumType.REGULAR

    def draw(self) -> None:
        """Draw the composed maze sprite centered in the window."""
        self.canvas.draw_to_window(0, self.y_offset)

    def _convert_to_autotiled(self, maze: list[list[int]]) -> list[list[int]]:
        """Convert a raw wall-bitmask maze into an autotiled grid.

        The input maze is a grid of cells where each value is a
        bitmask of the walls present on that cell's north, east,
        south, and west sides. This is expanded into a grid twice the
        size in each dimension, where corner cells encode which
        cardinal directions have a wall (as a 4-bit mask: 1=north,
        2=east, 4=south, 8=west) and the cells between corners are
        marked to indicate whether a wall segment connects them.

        Args:
            maze: The raw maze as a grid of per-cell wall bitmasks.

        Returns:
            The autotiled grid, with dimensions
            ``(2 * len(maze) + 1) x (2 * len(maze[0]) + 1)``, or an
            empty list if the input maze is empty.
        """
        if not maze or not maze[0]:
            return []

        h = len(maze)
        w = len(maze[0])

        res = [[0] * (2 * w + 1) for _ in range(2 * h + 1)]

        for i in range(h + 1):
            for j in range(w + 1):
                n_wall = (i > 0 and j < w and bool(maze[i - 1][j] & 8)) or (
                    i > 0 and j > 0 and bool(maze[i - 1][j - 1] & 2)
                )
                e_wall = (j < w and i < h and bool(maze[i][j] & 1)) or (
                    j < w and i > 0 and bool(maze[i - 1][j] & 4)
                )
                s_wall = (i < h and j < w and bool(maze[i][j] & 8)) or (
                    i < h and j > 0 and bool(maze[i][j - 1] & 2)
                )
                w_wall = (j > 0 and i < h and bool(maze[i][j - 1] & 1)) or (
                    j > 0 and i > 0 and bool(maze[i - 1][j - 1] & 4)
                )

                res[2 * i][2 * j] = (
                    (1 if n_wall else 0)
                    | (2 if e_wall else 0)
                    | (4 if s_wall else 0)
                    | (8 if w_wall else 0)
                )

                if j < w and e_wall:
                    res[2 * i][2 * j + 1] = 10

                if i < h and s_wall:
                    res[2 * i + 1][2 * j] = 5

        return res
