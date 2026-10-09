1. Branch: feature/gameplay-scene (DONE)
2. Move `asset_manager` to `Scene` base class for simplicity (DONE)
3. expose `get_config_attr` to `Scene` base class for easy access to config attributes (DONE)
```py
def get_config_attr(self, attr: str) -> Any:
    """Get a configuration attribute."""
    return getattr(self.game.config, attr)
```
4. Implement `GameplayScene` to manage the gameplay scene
5. Move `maze`, `ghosts`, `pacman` to `GameplayScene`
6. Refactor all entities to access `GameplayScene` instead of `Game`

```py
from mlx_wrapper import (
    KEY_DOWN,
    KEY_ENTER,
    KEY_ESC,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_UP,
    MLXApp,
)

from pacman.base import Scene
from pacman.ui import Keyboard
from pacman.maze import Maze
from src.pacman.ghost import Blinky, Clyde, Inky, Pinky
from src.pacman.player import Player


class GamePlayScene(Scene):
    """Game play scene."""

    def __init__(self, game: MLXApp) -> None:
        """Initialize the level scene.

        Args:
            game: Game instance.
        """
        super().__init__(game)

        self._current_level = 0
        self.score = 0
        self.maze = Maze(self.game, self.game.width, self.game.height, 42, 10)

        # self._next_level()
        self._spawn_pacman()
        self._spawn_ghosts()

    def mount(self) -> None:
        """Mount the level scene."""
        self.game.bind_key(KEY_ESC, self._pause)
        self.game.bind_key(KEY_UP, self.pacman.move_up)
        self.game.bind_key(KEY_DOWN, self.pacman.move_down)
        self.game.bind_key(KEY_LEFT, self.pacman.move_left)
        self.game.bind_key(KEY_RIGHT, self.pacman.move_right)

    def unmount(self) -> None:
        """Unmount the level scene."""
        self.game.unbind_key(KEY_ESC)
        self.game.unbind_key(KEY_UP)
        self.game.unbind_key(KEY_DOWN)
        self.game.unbind_key(KEY_LEFT)
        self.game.unbind_key(KEY_RIGHT)

    def _pause(self) -> None:
        """Pause the level scene."""
        # self.game.push_scene(PauseScene(self.game))

    def _next_level(self) -> None:
        """Go to the next level."""
        self._current_level += 1
        self.game.maze.create_maze_sprite(self._current_level)

    def _spawn_pacman(self) -> None:
        """Spawn Pac-Man."""
        self.pacman = Player(self.game)

    def _spawn_ghosts(self) -> None:
        """Spawn ghosts."""
        self.ghosts = [
            Blinky(self.game),
            Pinky(self.game),
            Inky(self.game),
            Clyde(self.game),
        ]

    def _check_collisions(self) -> None:
        """Check for collisions."""

    def _check_win(self) -> None:
        """Check for win."""

    def update(self) -> None:
        """Update the level scene."""
        self.pacman.update()
        for ghost in self.ghosts:
            ghost.update()

    def _draw_hud(self) -> None:
        """Draw the HUD."""

    def draw(self, x: int, y: int) -> None:
        """Draw the level scene."""
        self.maze.draw()
        self.pacman.draw()
        for ghost in self.game.ghosts:
            ghost.draw()
```