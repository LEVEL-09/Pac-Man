from mazegenerator import MazeGenerator
from mlx_wrapper import MLXApp, Sprite


class Maze:
    def __init__(self, mlx_app: MLXApp, width: int, height: int, seed: int) -> None:
        self.mlx_app = mlx_app
        self.maze_generator = MazeGenerator(size=(width, height), seed=100)
        self.maze = self._convert_to_autotiled(self.maze_generator.maze)
        self.y = (self.mlx_app.height - len(self.maze) * 32) // 2
        self.images = []

        for img in range(1, 16):
            self.images.append(Sprite.from_file(f"assets/walls/wall{img:02d}.png"))

        self.canvas = Sprite.blank(len(self.maze[0]) * 32, len(self.maze) * 32)
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] == 1:
                    self.images[3].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 2:
                    self.images[0].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 3:
                    self.images[6].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 4:
                    self.images[2].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 5:
                    self.images[4].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 6:
                    self.images[9].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 7:
                    self.images[12].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 8:
                    self.images[1].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 9:
                    self.images[7].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 10:
                    self.images[5].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 11:
                    self.images[11].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 12:
                    self.images[8].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 13:
                    self.images[10].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 14:
                    self.images[13].blit(self.canvas, x * 32, y * 32)
                elif self.maze[y][x] == 15:
                    self.images[14].blit(self.canvas, x * 32, y * 32)

                

    def draw(self):
        self.canvas.draw_to_window(self.mlx_app.win_ptr, 0, self.y)

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
