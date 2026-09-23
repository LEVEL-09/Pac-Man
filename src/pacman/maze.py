from mazegenerator import MazeGenerator
from mlx_wrapper import MLXApp, Sprite


class Maze:
    def __init__(
        self, mlx_app: MLXApp, width: int, height: int, seed: int
    ) -> None:
        self.mlx_app = mlx_app
        self.maze_generator = MazeGenerator(size=(width, height), seed=seed) # NOTE: very slow
        self.x = height
        self.y = (self.mlx_app.height - self.x) // 2

        self.canvas = Sprite.blank(width, height)
        self.canvas.fill(0xFFFFFFFF)

    def draw(self):
        self.canvas.draw_to_window(self.mlx_app.win_ptr, 0, self.y)
