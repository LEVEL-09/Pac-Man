"""Maze generation, autotiling, and rendering for the Pac-Man game.

This module exposes the :class:`Maze` class, which wraps a
:class:`~mazegenerator.MazeGenerator` to procedurally generate a maze
per level, converts the generated maze into an autotiled wall layout,
and renders it to the game window as a single composed sprite.
"""

import random

from mazegenerator import MazeGenerator
from mlx_wrapper import AssetManager, MLXApp, Sprite


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
        asset_manager: Provides access to wall sprites by name.
        maze_generator: Generates the raw maze layout for each level.
        seeds: Per-level seeds derived from the top-level seed.
    """

    def __init__(
        self,
        mlx_app: MLXApp,
        width: int,
        height: int,
        seed: int,
        asset_manager: AssetManager,
        levels_number: int,
    ) -> None:
        """Initialize the maze generator and derive per-level seeds.

        Args:
            mlx_app: The running MLX application/window used for
                rendering.
            width: The maze width, in cells.
            height: The maze height, in cells.
            seed: The top-level seed used to deterministically derive
                one seed per level.
            asset_manager: Provides access to wall sprites by name.
            levels_number: The number of levels to generate seeds for.
        """
        self.mlx_app = mlx_app
        self.width = width
        self.height = height
        self.y_offset = (self.mlx_app.height - (self.height * 2 + 1) * 32) // 2
        self.asset_manager = asset_manager
        self.maze_generator = MazeGenerator(size=(width, height))

        random.seed(seed)
        self.seeds = [
            random.randint(0, 2**32 - 1) for _ in range(levels_number)
        ]
        self.canvas: Sprite = self.create_sprite(0)

    def create_sprite(self, level: int) -> Sprite:
        """Generate a level's maze and compose it into a single sprite.

        Generates the raw maze for the given level using its
        corresponding seed, converts it into an autotiled wall layout,
        and blits each non-empty wall tile onto a blank canvas sprite.

        Args:
            level: The zero-based index of the level to generate.

        Returns:
            A sprite containing the fully composed maze, ready to be
            drawn to the window.
        """
        self.maze_generator.generate(seed=self.seeds[level])
        self.maze = self._convert_to_autotiled(self.maze_generator.maze)

        canvas = Sprite.blank(len(self.maze[0]) * 32, len(self.maze) * 32)

        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] != 0:
                    self.asset_manager.get_sprite(
                        f"wall{self.maze[y][x]:02d}"
                    ).blit(canvas, x * 32, y * 32)

        self.canvas = canvas

    def draw(self, target: Sprite) -> None:
        """Draw the composed maze sprite centered in the window.

        Args:
            target: Target sprite to draw the maze on.
        """
        if self.canvas:
            self.canvas.blit(target, 0, self.y_offset)

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
