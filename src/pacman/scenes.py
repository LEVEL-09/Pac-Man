"""In-game menus, including the main menu and its buttons."""

from enum import Enum, auto

from mlx_wrapper import (
    KEY_DOWN,
    KEY_ENTER,
    KEY_ESC,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_UP,
    Sprite,
)

from pacman.base import Scene
from pacman.ghost import Blinky, Clyde, Ghost, GhostState, Inky, Pinky
from pacman.maze import Maze, PacGumType
from pacman.player import Player
from pacman.ui import Keyboard


class Phase(Enum):
    """Represents the current phase of the game."""

    STARTING = auto()
    PLAYING = auto()
    DYING = auto()


class GamePlayScene(Scene):
    """Game play scene."""

    USE_STARFIELD = False

    def __init__(self) -> None:
        """Initialize the level scene."""
        super().__init__()
        self._current_level = 0
        self.player_lives = self.config.player_lives
        self.game_time = self.config.game_time
        self.pacgum_score = self.config.pacgum_score
        self.super_pacgum_score = self.config.super_pacgum_score
        self.ghost_score = self.config.ghost_score

        self.player_score = 0

        self.blank = Sprite.blank(32, 32)
        self.blank.fill(0xFF000000)

        self._phase = Phase.STARTING
        self._phase_update = {
            Phase.STARTING: self._update_starting,
            Phase.PLAYING: self._update_playing,
            Phase.DYING: self._update_dying
        }

        self.maze = Maze(
            self.game.height,
            self.am,
            self.config.maze_width,
            self.config.maze_height,
            self.config.maze_seed,
            10
        )
        self.player = Player(self.am, self.maze, 4, self._eat_pacgum)

        self.ghosts = [
            Blinky(self.am, self.maze, self.player),
            Pinky(self.am, self.maze, self.player),
            Inky(self.am, self.maze, self.player),
            Clyde(self.am, self.maze, self.player)
        ]

        self._elapsed = 0.
        self.timer = 0.
        self._frightened_timer = 0.

        self._set_timer(2)
        self._spawn_player()
        self._spawn_ghosts()

    def _set_timer(self, timer: float) -> None:
        """Set the timer.

        Args:
            timer: timer value
        """
        self.timer = timer

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

    def update(self) -> None:
        """Update the level scene."""
        self._phase_update[self._phase]()

    def _draw_hud(self) -> None:
        """Draw the HUD."""

    def draw(self) -> None:
        """Draw the level scene."""
        self.draw_background()
        super().draw()
        self.maze.draw()
        self.maze.path_canvas.fill(0)
        for ghost in self.ghosts:
            ghost.draw()
            # TODO: Check if cheat mode is enabled and draw path
            ghost.draw_path()
        self.maze.path_canvas.draw_to_window(0, self.maze.y_offset)
        self.player.draw()

    def _update_starting(self) -> None:
        """Update the starting state."""
        self._elapsed += self.game.dt
        if self._elapsed >= self.timer:
            self._elapsed = 0.
            self.set_timer(self.config.game_time)
            self._phase = Phase.PLAYING
        self.player.update_animation(self.game.dt)
        for ghost in self.ghosts:
            ghost.update_animation(self.game.dt)

    def _update_playing(self) -> None:
        """Update the playing state."""
        self._check_win()

        self.player.update_animation(self.game.dt)
        self.player.move()
        for ghost in self.ghosts:
            ghost.update_animation(self.game.dt)
            ghost.update_state()
            ghost.move()

        self._update_frightened()
        self._handle_collisions()

    def _update_dying(self) -> None:
        """Update the dying state."""
        if self.player.animations[self.player.animation_key].is_finished:
            for ghost in self.ghosts:
                ghost.reset()
            self.player.reset()
            self._phase = Phase.PLAYING
        self.player.update_animation(self.game.dt)

    def _eat_pacgum(self) -> None:
        """Eat a pacgum."""
        pacgum_type = self.maze.collectibles.pop(self.player.curr_cell, None)
        if pacgum_type is not None:
            if pacgum_type == PacGumType.SUPER:
                self.player_score += self.super_pacgum_score
                self._start_frightened()
            elif pacgum_type == PacGumType.REGULAR:
                self.player_score += self.pacgum_score
            self.blank.blit(
                self.maze.canvas,
                self.player.curr_cell[0] * 32,
                self.player.curr_cell[1] * 32
            )

    def _start_frightened(self) -> None:
        """Start the frightened state."""
        self._frightened_timer = Ghost.FRIGHTENED_DURATION
        for ghost in self.ghosts:
            if ghost.state in (GhostState.CHASE, GhostState.SCATTER):
                ghost.target_cell = ghost.curr_cell
                ghost.state = GhostState.FRIGHTENED

    def _update_frightened(self) -> None:
        """Update the frightened state."""
        if self._frightened_timer <= 0:
            return
        self._frightened_timer -= self.game.dt
        if self._frightened_timer <= 0:
            for ghost in self.ghosts:
                if ghost.state == GhostState.FRIGHTENED:
                    ghost.state = GhostState.CHASE

    def _check_collisions(self) -> int:
        """Check for collisions.

        Returns:
            int: Index of the ghost that collided with Pac-Man, or -1
                if no collision occurred.
        """
        for i, ghost in enumerate(self.ghosts):
            if ghost.hitbox.detect_collision(
                ghost.x, ghost.y,
                self.player.hitbox,
                self.player.x, self.player.y
            ):
                return i
        return -1

    def _handle_collisions(self) -> None:
        collided = self._check_collisions()
        if collided != -1:
            collided_ghost = self.ghosts[collided]
            if collided_ghost.state in (GhostState.CHASE, GhostState.SCATTER):
                self._phase = Phase.DYING
                self.player.die()
                self.player_lives -= 1
                if self.player_lives == 0:
                    self.game.switch_scene(EndScene(False, self.player_score))
            elif collided_ghost.state == GhostState.FRIGHTENED:
                collided_ghost.state = GhostState.EATEN
                self.player_score += self.ghost_score

    def _check_win(self) -> None:
        """Check for win."""
        if not self.maze.collectibles:
            if self._current_level == 9:
                self.game.switch_scene(EndScene(True, self.player_score))
            else:
                self._next_level()

    def _pause(self) -> None:
        """Pause the level scene."""
        # self.game.push_scene(PauseMenu(self.game))

    def _next_level(self) -> None:
        """Go to the next level."""
        self._current_level += 1
        self._phase = Phase.STARTING
        self._set_timer(2)
        self.maze.create_maze_sprite(self._current_level)
        self.player.reset()
        self._spawn_ghosts()

    def _spawn_player(self) -> None:
        """Spawn Pac-Man."""
        self.player = Player(self.am, self.maze, 4, self._eat_pacgum)

    def _spawn_ghosts(self) -> None:
        """Spawn ghosts."""
        self.ghosts = [
            Blinky(self.am, self.maze, self.player),
            Pinky(self.am, self.maze, self.player),
            Inky(self.am, self.maze, self.player),
            Clyde(self.am, self.maze, self.player)
        ]


class EndScene(Scene):
    """End scene for the game.

    Displays the game over or win screen and waits for the player
    to press Enter.

    Attributes:
        won: Whether the player won or lost.
        player_score: Player's score.
        font: Font used for text.
        title: Sprite used for the win or game over title.
        keyboard: Keyboard used to wait for the player to press Enter.
    """

    def __init__(self, won: bool, player_score: int) -> None:
        """Initialize the end scene.

        Args:
            won: Whether the player won or lost.
            player_score: The player's score.
        """
        super().__init__()
        self.player_score = player_score
        self.font = self.am.get_font("kolostygra")
        if won:
            self.title = self.am.get_sprite("win")
        else:
            self.title = self.am.get_sprite("game_over")
        self.keyboard = Keyboard(self.ctx, 0, 0, 30)
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
        self.draw_background()
        self.title.blit(
            self.canvas, (self.canvas.width - self.title.width) // 2, 50
        )
        self.keyboard.blit(self.canvas)
        text_center = (
            self.canvas.width - self.font.measure_text(f"Your score: {1000}")
        ) // 2
        self.font.draw_text(
            self.canvas,
            f"Your score: {self.player_score}",
            text_center,
            self.title.height + 150,
            0xFFFFFF00,
            cache=True
        )
        text_center = (
            self.canvas.width - self.font.measure_text("Type in your username")
        ) // 2
        self.font.draw_text(
            self.canvas,
            "Type in your username",
            text_center,
            self.keyboard.y - self.font.atlas.height - 100,
            0xFFFFFFFF,
            cache=True
        )
        if self.keyboard.buffer:
            text_center = (
                self.canvas.width -
                self.font.measure_text(self.keyboard.buffer)
            ) // 2
            self.font.draw_text(
                self.canvas,
                self.keyboard.buffer,
                text_center,
                self.keyboard.y - self.font.atlas.height - 50,
                0xFFFFFFFF
            )
