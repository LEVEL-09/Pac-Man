from mlx_wrapper import *
from pacman.maze import Maze

KEY_LEFT = 0xFF51
KEY_UP = 0xFF52
KEY_RIGHT = 0xFF53
KEY_DOWN = 0xFF54
KEY_ENTER = 0xFF0D


class Hitbox:
    def __init__(self, x_offset: int, y_offset: int, width: int, height: int) -> None:
        self.xo = x_offset
        self.yo = y_offset
        self.w = width
        self.h = height

    def detect_collision(self, x: int, y: int, other: "Hitbox", other_x: int, other_y: int) -> bool:
        l = x + self.xo
        r = l + self.w
        t = y + self.yo
        b = t + self.h

        return not (
            l > other_x + other.xo + other.w
            or r < other_x + other.xo
            or b < other_y + other.yo
            or t > other_y + other.yo + other.h
        )


class Pacman:
    def __init__(self, game: Game, y_offset: int) -> None:
        self.game = game
        self.maze_grid = game.maze.maze
        self.gw = len(self.maze_grid[0]) - 1
        self.gh = len(self.maze_grid) - 1
        maze_width = self.gw // 2
        maze_height = self.gh // 2

        self.curr_cell = (
            maze_width - (maze_width % 2 == 0),
            maze_height - (maze_height % 2 == 0)
        )
        self.x = self.curr_cell[0] * 32
        self.y = self.curr_cell[1] * 32
        self.y_offset = y_offset
        self.speed = 5
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

        self.curr_state = 'appear'
        self.animations = {
            'up': game.am.get_animated_sprite("pac_up"),
            'down': game.am.get_animated_sprite("pac_down"),
            'left': game.am.get_animated_sprite("pac_left"),
            'right': game.am.get_animated_sprite("pac_right"),
            'death': game.am.get_animated_sprite("pac_death"),
            'appear': game.am.get_animated_sprite("pac_appear"),
        }
        self.animations['up'].loop_mode = LoopMode.PINGPONG
        self.animations['down'].loop_mode = LoopMode.PINGPONG
        self.animations['left'].loop_mode = LoopMode.PINGPONG
        self.animations['right'].loop_mode = LoopMode.PINGPONG
        self.animations['appear'].loop_mode = LoopMode.ONCE
        self.animations['death'].loop_mode = LoopMode.ONCE
        self.animations[self.curr_state].play()

        game.bind_key(KEY_UP, self.move_up)
        game.bind_key(KEY_DOWN, self.move_down)
        game.bind_key(KEY_LEFT, self.move_left)
        game.bind_key(KEY_RIGHT, self.move_right)

        self.appeared = False

    def _is_walkable(self, gx: int, gy: int) -> bool:
        if gx < 0 or gx >= self.gw or gy < 0 or gy >= self.gh:
            return False
        return self.maze_grid[gy][gx] == 0

    def _update_direction(self, new_dx: int, new_dy: int) -> None:
        old_state = self.curr_state
        self.dx = new_dx
        self.dy = new_dy

        if self.dx == 1: self.curr_state = 'right'
        elif self.dx == -1: self.curr_state = 'left'
        elif self.dy == 1: self.curr_state = 'down'
        elif self.dy == -1: self.curr_state = 'up'

        if old_state != self.curr_state:
            self.animations[self.curr_state].play()

    def update(self) -> None:
        if (self.dx != 0 and self.next_dx == -self.dx) or (self.dy != 0 and self.next_dy == -self.dy):
            self._update_direction(self.next_dx, self.next_dy)

        remaining_steps = self.speed
        while remaining_steps > 0:
            if self.x % 32 == 0 and self.y % 32 == 0:
                self.curr_cell = (self.x // 32, self.y // 32)
                if (self.next_dx != 0 or self.next_dy != 0
                    and self._is_walkable(
                        self.curr_cell[0] + self.next_dx,
                        self.curr_cell[1] + self.next_dy
                    )
                ):
                    self._update_direction(self.next_dx, self.next_dy)
                if not self._is_walkable(
                    self.curr_cell[0] + self.dx, self.curr_cell[1] + self.dy
                ):
                    self.animations[self.curr_state].stop()
                    break
            if self.dx == 0 and self.dy == 0:
                break

            self.x += self.dx
            self.y += self.dy
            remaining_steps -= 1

        if not self.appeared or self.dx == 0 and self.dy == 0:
            self.animations[self.curr_state].update(self.game.dt)

    def move_up(self) -> None:
        self.next_dx, self.next_dy = 0, -1

    def move_down(self) -> None:
        self.next_dx, self.next_dy = 0, 1

    def move_left(self) -> None:
        self.next_dx, self.next_dy = -1, 0

    def move_right(self) -> None:
        self.next_dx, self.next_dy = 1, 0

    def draw(self, target: Sprite) -> None:
        self.animations[self.curr_state].blit(
            target, self.x, self.y + self.y_offset
        )


class Game(MLXApp):
    def __init__(self, width: int, height: int, title: str) -> None:
        win_w, win_h = (
            (width * 2 + 1) * 32,
            (height * 2 + 1) * 32 + 50 * 2
        )
        super().__init__(win_w, win_h, title)
        self.main = Sprite.blank(win_w, win_h)
        self.am = AssetManager("./assets.xml")
        self.maze = Maze(self, 12, 12, 4, self.am, 10)
        self.maze.create_sprite(2)
        self.pacman = Pacman(self, self.maze.y_offset)

    def update(self) -> None:
        self.main.fill(0xFF000000)
        self.pacman.update()

        self.maze.draw(self.main)
        self.pacman.draw(self.main)

        self.main.draw_to_window(self.win_ptr, 0, 0)

if __name__ == "__main__":
    game = Game(12, 12, "Test")
    game.start()
