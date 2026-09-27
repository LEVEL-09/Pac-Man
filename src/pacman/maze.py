import random

from mazegenerator import MazeGenerator
from mlx_wrapper import AssetManager, MLXApp, Sprite


class Maze:
    def __init__(
        self,
        mlx_app: MLXApp,
        width: int,
        height: int,
        seed: int,
        asset_manager: AssetManager,
        levels_number: int,
    ) -> None:
        self.mlx_app = mlx_app
        self.width = width
        self.height = height
        self.asset_manager = asset_manager
        self.maze_generator = MazeGenerator(size=(width, height))

        random.seed(seed)
        self.seeds = [
            random.randint(0, 2**32 - 1) for _ in range(levels_number)
        ]

    def create_sprites(self, level: int) -> Sprite:
        self.maze_generator.generate(seed=self.seeds[level])
        maze = self._convert_to_autotiled(self.maze_generator.maze)

        canvas = Sprite.blank(len(maze[0]) * 32, len(maze) * 32)

        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] != 0:
                    self.asset_manager.get_sprite(
                        f"wall{maze[y][x]:02d}"
                    ).blit(canvas, x * 32, y * 32)

        return canvas

    def draw(self, canvas: Sprite) -> None:
        y = (self.mlx_app.height - (self.height * 2 + 1) * 32) // 2
        canvas.draw_to_window(self.mlx_app.win_ptr, 0, y)

    def _convert_to_autotiled(self, maze: list[list[int]]) -> list[list[int]]:
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
