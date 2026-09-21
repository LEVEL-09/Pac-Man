from mazegenerator import MazeGenerator
from mlx_wrapper import MLXApp, Sprite


class Maze:
    def __init__(
        self, mlx_app: MLXApp, width: int, height: int, seed: int
    ) -> None:
        self.mlx_app = mlx_app
        self.maze_generator = MazeGenerator(size=(width, height), seed=seed)

        self.canvas = Sprite.blank(mlx_app.mlx, mlx_app.mlx_ptr, width, height)
        print(self.maze_generator.maze)
