from mazegenerator import MazeGenerator
from mlx import Mlx
from mlx_wrapper import MLXApp, Sprite


class Maze:
    def __init__(
        self, mlx: Mlx, mlx_ptr: int, seed: int, width: int, height: int
    ) -> None:
        self.maze = MazeGenerator((width, height), seed=seed)
        Sprite.blank(mlx, mlx_ptr, 64 * width, 64 * height)


if __name__ == "__main__":
    app = MLXApp(20, 20, "PAC-MAN")
    maze = Maze(app.mlx, app.mlx_ptr, 42, 20, 20)
