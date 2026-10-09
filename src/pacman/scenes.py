"""In-game menus, including the main menu and its buttons."""

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
from pacman.ghost import Blinky, Clyde, Inky, Pinky
from pacman.maze import Maze
from pacman.player import Player
from pacman.ui import Keyboard


class GamePlayScene(Scene):
    """Game play scene."""

    def __init__(self) -> None:
        """Initialize the level scene.

        Args:
            game: Game instance.
        """
        super().__init__()
        self._current_level = 0
        self.score = 0
        self.maze = Maze(
            game=self.game,
            am=self.am,
            width=self.get_config_attr('maze_width'),
            height=self.get_config_attr('maze_height'),
            seed=42, levels_number=10
        )

        # self._next_level()
        self._spawn_player()
        self._spawn_ghosts()

    def mount(self) -> None:
        """Mount the level scene."""
        self.game.bind_key(KEY_ESC, self._pause)
        self.game.bind_key(KEY_UP, self.player.move_up)
        self.game.bind_key(KEY_DOWN, self.player.move_down)
        self.game.bind_key(KEY_LEFT, self.player.move_left)
        self.game.bind_key(KEY_RIGHT, self.player.move_right)

    def unmount(self) -> None:
        """Unmount the level scene."""
        self.game.unbind_key(KEY_ESC)
        self.game.unbind_key(KEY_UP)
        self.game.unbind_key(KEY_DOWN)
        self.game.unbind_key(KEY_LEFT)
        self.game.unbind_key(KEY_RIGHT)

    def _pause(self) -> None:
        """Pause the level scene."""
        # self.game.push_scene(PauseMenu(self.game))

    def _next_level(self) -> None:
        """Go to the next level."""
        self._current_level += 1
        self.maze.create_maze_sprite(self._current_level)

    def _spawn_player(self) -> None:
        """Spawn Pac-Man."""
        self.player = Player(self.maze, self.am, 4)

    def _spawn_ghosts(self) -> None:
        """Spawn ghosts."""
        self.ghosts = [
            Blinky(self.player, self.am, self.maze),
            Pinky(self.player, self.am, self.maze),
            Inky(self.player, self.am, self.maze),
            Clyde(self.player, self.am, self.maze)
        ]

    def _check_collisions(self) -> None:
        """Check for collisions."""

    def _check_win(self) -> None:
        """Check for win."""

    def update(self) -> None:
        """Update the level scene."""
        self.player.update(self.game.dt)
        for ghost in self.ghosts:
            ghost.update(self.game.dt)

    def _draw_hud(self) -> None:
        """Draw the HUD."""

    def draw(self, x: int, y: int) -> None:
        """Draw the level scene."""
        self.maze.draw()
        self.player.draw()
        for ghost in self.ghosts:
            ghost.draw()


class EndScene(Scene):
    """End scene for the game.

    Displays the game over or win screen and waits for the player
    to press Enter.

    Attributes:
        lost: Whether the player lost or won.
    """

    def __init__(self, lost: bool) -> None:
        """Initialize the end scene.

        Args:
            game: Game instance.
            lost: Whether the player lost or won.
        """
        super().__init__()
        self.font = self.am.get_font("kolostygra")
        if lost:
            self.title = self.am.get_sprite("win")
        else:
            self.title = self.am.get_sprite("game_over")
        self.keyboard = Keyboard(self.game, self.am, 0, 0, 30)
        self.keyboard.x = (self.game.width - self.keyboard.width) // 2
        self.keyboard.y = (self.game.height - self.title.height) // 2

    def mount(self) -> None:
        """Mount the end scene."""
        self.keyboard.mount()
        self.game.bind_key(KEY_ENTER, self._on_enter)

    def unmount(self) -> None:
        """Unmount the end scene."""
        self.keyboard.unmount()
        self.game.unbind_key(KEY_ENTER)

    def _on_enter(self) -> None:
        """Handle the Enter key press."""
        print("Enter pressed")

    def update(self) -> None:
        """Update the end scene."""
        self.draw_stars()
        self.title.blit(self.canvas, (self.canvas.width - self.title.width) // 2, 50)
        self.keyboard.blit(self.canvas)
        text_center = (
            self.canvas.width - self.font.measure_text(f"Your score: {1000}")
        ) // 2
        self.font.draw_text(
            self.canvas,
            f"Your score: {1000}",
            text_center,
            self.title.height + 150,
            0xFFFFFF00,
            cache=True,
        )
        text_center = (
            self.canvas.width - self.font.measure_text("Type in your username")
        ) // 2
        self.font.draw_text(
            self.canvas,
            "Type in your username:",
            text_center,
            self.keyboard.y - self.font.atlas.height - 100,
            0xFFFFFFFF,
            cache=True,
        )
        if self.keyboard.buffer:
            text_center = (
                self.canvas.width - self.font.measure_text(self.keyboard.buffer)
            ) // 2
            self.font.draw_text(
                self.canvas,
                self.keyboard.buffer,
                text_center,
                self.keyboard.y - self.font.atlas.height - 50,
                0xFFFFFFFF,
            )

    def draw(self, x: int, y: int) -> None:
        """Draw the end scene.

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        self.canvas.draw_to_window(0, 0)
