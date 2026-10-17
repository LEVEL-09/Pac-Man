"""In-game menus, including the main menu and its buttons."""

import json
from enum import Enum, auto
from pathlib import Path

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
from pacman.menus import CheatFlags, MainMenu, PauseMenu
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

        self.heart = self.am.get_animated_sprite("heart")
        self.font = self.am.get_font("minecraft_large")
        self.heart.play()

        self.game_time = self.config.game_time
        self._frightened_timer = 0.

    def mount(self) -> None:
        """Mount the level scene."""
        self.game.bind_key(KEY_ESC, self._pause)
        self.game.bind_key(KEY_UP, self.player.move_up)
        self.game.bind_key(KEY_DOWN, self.player.move_down)
        self.game.bind_key(KEY_LEFT, self.player.move_left)
        self.game.bind_key(KEY_RIGHT, self.player.move_right)
        self._apply_cheats()

    def unmount(self) -> None:
        """Unmount the level scene."""
        self.game.unbind_key(KEY_ESC)
        self.game.unbind_key(KEY_UP)
        self.game.unbind_key(KEY_DOWN)
        self.game.unbind_key(KEY_LEFT)
        self.game.unbind_key(KEY_RIGHT)

    def _apply_cheats(self) -> None:
        """Apply cheat flags.

        `CheatFlags.x2_speed`: If the speed cheat flag is enabled, double
        the player's speed. Else, set the speed to the default value.

        `CheatFlags.invincibility`: If the invincibility cheat flag is enabled,
        lower the player's opacity. Else, set the opacity to the default value.
        """
        self.player.speed = self.player.speed * 2 if CheatFlags.x2_speed else 4
        for animation in self.player.animations.values():
            for frame in animation.frames:
                if CheatFlags.invincibility:
                    frame.pixels[frame.pixels > 0] &= 0xB0FFFFFF
                else:
                    frame.pixels[frame.pixels > 0] |= 0xFF000000

    def update(self) -> None:
        """Update the level scene."""
        self._phase_update[self._phase]()

    def _draw_hud(self) -> None:
        """Draw the HUD."""
        x_pad = 10
        y = 16
        self.font.draw_text(
            self.canvas,
            f"Level: {self._current_level + 1}",
            x_pad, y,
            cache=True,
            color=0xFFFFFFFF
        )
        self.font.draw_text(
            self.canvas,
            f"Score: {self.player_score}",
            (self.canvas.width - x_pad -
                self.font.measure_text(f"Score: {self.player_score}")),
            y,
            id='score',
            color=0xFFFFFFFF
        )
        y = self.maze.y_offset + (self.maze.height * 2 + 1) * 32 + 16
        self.heart.update(self.game.dt)
        if CheatFlags.inf_lives:
            self.font.draw_text(
                self.canvas,
                "∞",
                x_pad,
                y,
                color=0xFFFFFFFF
            )
            self.heart.blit(self.canvas, x_pad + 32, y)
        else:
            for i in range(self.player_lives):
                self.heart.blit(self.canvas, x_pad + i * 40, y)

        min, sec = divmod(self.game_time, 60)
        self.font.draw_text(
            self.canvas,
            f"{int(min):02}:{int(sec):02}",
            (self.canvas.width - x_pad -
                self.font.measure_text(f"{int(min):02}:{int(sec):02}")),
            y,
            id='timer',
            color=0xFFFFFFFF,
        )

    def draw(self) -> None:
        """Draw the level scene."""
        self.draw_background()
        self._draw_hud()
        super().draw()
        self.maze.draw()
        self.maze.path_canvas.fill(0)
        for ghost in self.ghosts:
            ghost.draw()
            if CheatFlags.visualize_path:
                ghost.draw_path()
        if CheatFlags.visualize_path:
            self.maze.path_canvas.draw_to_window(0, self.maze.y_offset)
        self.player.draw()

    def _update_starting(self) -> None:
        """Update the starting state."""
        if self.player.animations[self.player.animation_key].is_finished:
            self._phase = Phase.PLAYING

        self.player.update_animation(self.game.dt)
        for ghost in self.ghosts:
            ghost.update_animation(self.game.dt)

    def _update_playing(self) -> None:
        """Update the playing state."""
        self._update_frightened()
        self._handle_collisions()
        self._check_win()
        self._check_game_time()

        if (
            self._phase != Phase.PLAYING
            or self.game._current_scene is not self
        ):
            return

        self.player.update_animation(self.game.dt)
        self.player.move()
        for ghost in self.ghosts:
            ghost.update_animation(self.game.dt)
            ghost.update_state()
            ghost.move()

    def _update_dying(self) -> None:
        """Update the dying state."""
        if self.player.animations[self.player.animation_key].is_finished:
            for ghost in self.ghosts:
                ghost.reset()
            self.player.reset()
            self._phase = Phase.STARTING
        if self.player_lives == 0:
            self.game.switch_scene(EndScene(False, self.player_score))
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

    def _check_collisions(self) -> list[int]:
        """Check for collisions.

        Returns:
            list[int]: Indices of the ghosts that collided with Pac-Man.
        """
        return [
            i for i, ghost in enumerate(self.ghosts)
            if ghost.hitbox.detect_collision(
                ghost.x, ghost.y,
                self.player.hitbox,
                self.player.x, self.player.y
            )
        ]

    def _handle_collisions(self) -> None:
        """Handle collisions between the player and ghosts."""
        collided_indices = self._check_collisions()
        if not collided_indices:
            return

        collided_ghosts = [self.ghosts[i] for i in collided_indices]

        attacking_ghosts = any(
            g.state in (GhostState.CHASE, GhostState.SCATTER)
            for g in collided_ghosts
        )

        if attacking_ghosts and not CheatFlags.invincibility:
            self._phase = Phase.DYING
            self.player.die()
            if not CheatFlags.inf_lives:
                self.player_lives -= 1
            return

        for ghost in collided_ghosts:
            if ghost.state == GhostState.FRIGHTENED:
                ghost.state = GhostState.EATEN
                self.player_score += self.ghost_score

    def _check_game_time(self) -> None:
        """Check the timer. If the timer runs out, the game is over."""
        self.game_time -= self.game.dt

        if self.game_time <= 0:
            self.game_time = 0
            self.player_lives = 0
            self._phase = Phase.DYING
            self.game.switch_scene(EndScene(False, self.player_score))

    def _check_win(self) -> None:
        """Check for win."""
        if not self.maze.collectibles:
            if self._current_level == 9:
                self.game.switch_scene(EndScene(True, self.player_score))
            else:
                self._next_level()

    def _pause(self) -> None:
        """Pause the level scene."""
        self.game.push_scene(PauseMenu())

    def _next_level(self) -> None:
        """Go to the next level."""
        self._current_level += 1
        self._phase = Phase.STARTING
        self.game_time = self.config.game_time
        self.maze.create_maze_sprite(self._current_level)
        self.player.reset()
        for ghost in self.ghosts:
            ghost.reset()
        self.font.clear_cache()


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

    file_path = Path("highscores.json")

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
        self.keyboard = Keyboard(self.ctx, 0, 0, 10)
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
        if not self.keyboard.buffer.strip():
            return

        self.file_path.touch(exist_ok=True)
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            self.logger.warning(
                "highscores data is corrupted, resetting to empty"
            )
            data = {}
        except OSError:
            pass

        try:
            with open(self.file_path, 'w') as f:
                data[self.keyboard.buffer] = self.player_score
                json.dump(data, f, indent=4)
                self.logger.info("Score saved successfully")
        except OSError:
            self.logger.error("Failed to save score")

        self.game.switch_scene(MainMenu())

    def update(self) -> None:
        """Update the end scene."""
        self.draw_background()
        self.title.blit(
            self.canvas, (self.canvas.width - self.title.width) // 2, 50
        )
        self.keyboard.blit(self.canvas)
        text_center = (
            self.canvas.width - self.font.measure_text(
                f"Your score: {self.player_score}"
            )
        ) // 2
        self.font.draw_text(
            self.canvas,
            f"Your score: {self.player_score}",
            text_center,
            self.title.height + 150,
            cache=True,
            color=0xFFFFFF00
        )
        text_center = (
            self.canvas.width - self.font.measure_text("Type in your username")
        ) // 2
        self.font.draw_text(
            self.canvas,
            "Type in your username",
            text_center,
            self.keyboard.y - self.font.atlas.height - 100,
            cache=True,
            color=0xFFFFFFFF
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
                id='username',
                color=0xFFFFFFFF
            )


class HighscoreScene(Scene):
    """Show the top ten saved scores and allow returning to the main menu."""

    file_path = Path("highscores.json")

    def __init__(self) -> None:
        """Initialize the title, font, and saved leaderboard."""
        super().__init__()
        self.title = self.am.get_sprite("title")
        self.font = self.am.get_font("kolostygra_large")
        self.leaderboard = self._load_highscore()

    def mount(self) -> None:
        """Bind Escape to return to the main menu."""
        self.game.bind_key(KEY_ESC, lambda: self.game.switch_scene(MainMenu()))

    def unmount(self) -> None:
        """Remove the Escape key binding when leaving the scene."""
        self.game.unbind_key(KEY_ESC)

    def _validate_leaderboard(
        self,
        pairs: list[tuple[str, int]]
    ) -> dict[str, int]:
        leaderboard = dict(sorted(pairs, key=lambda x: x[1], reverse=True))
        leaderboard = {k: v for k, v in leaderboard.items()
                       if v >= 0 and k.strip()}

        return leaderboard

    def _load_highscore(self) -> dict[str, int]:
        if not self.file_path.exists():
            self.logger.warning(f"Highscore file not found: {self.file_path}")
            return {}

        try:
            with open(self.file_path, 'r') as f:
                self.leaderboard = json.load(
                    f,
                    object_pairs_hook=self._validate_leaderboard,
                )
        except (json.JSONDecodeError, OSError):
            self.logger.warning(f"Failed to load highscore: {self.file_path}")
            self.leaderboard = {}
        return self.leaderboard

    def _draw_leaderboard_entry(
        self,
        rank: str,
        name: str,
        score: str,
        y: int,
        color: bool = False
    ) -> None:
        col_width = self.canvas.width // 3
        self.font.draw_text(
            self.canvas,
            rank,
            (col_width - self.font.measure_text(rank)) // 2,
            y + self.title.height + 150,
            color=0xFFFFFFFF if color else 0xFFFFFF00,
            cache=True
        )

        self.font.draw_text(
            self.canvas,
            name,
            (self.canvas.width - self.font.measure_text(name)) // 2,
            y + self.title.height + 150,
            color=0xFFFFFFFF if color else 0xFFFFFF00,
            cache=True
        )

        self.font.draw_text(
            self.canvas,
            score,
            ((col_width * 5) - self.font.measure_text(score)) // 2,
            y + self.title.height + 150,
            color=0xFFFFFFFF if color else 0xFFFFFF00,
            cache=True
        )

    def _draw_leaderboard(self) -> None:
        y_pad = 20
        self._draw_leaderboard_entry("RANK", "NAME", "SCORE", y_pad, False)
        y = (self.font.atlas.height + y_pad) * 2
        for rank, (name, score) in enumerate(self.leaderboard.items(), 1):
            if rank > 10:
                break
            self._draw_leaderboard_entry(str(rank), name, str(score), y, True)
            y += self.font.atlas.height + y_pad

    def update(self) -> None:
        """Draw the background, title, and top ten leaderboard entries."""
        self.draw_background()
        self.title.blit(
            self.canvas, (self.canvas.width - self.title.width) // 2, 50
        )
        self._draw_leaderboard()


class InstructionsScene(Scene):
    """Instructions scene."""

    def __init__(self) -> None:
        """Initialize the instructions scene."""
        super().__init__()
        self.instructions_img = self.am.get_sprite("instructions")

    def mount(self) -> None:
        """Mount the instructions scene."""
        self.game.bind_key(KEY_ESC, self.game.pop_scene)

    def unmount(self) -> None:
        """Unmount the instructions scene."""
        self.game.unbind_key(KEY_ESC)

    def update(self) -> None:
        """Draw the background and instructions image."""
        self.draw_background()

    def draw(self) -> None:
        """Draw the instructions image."""
        super().draw()
        self.instructions_img.draw_to_window(
            (self.canvas.width - self.instructions_img.width) // 2,
            (self.canvas.height - self.instructions_img.height) // 2
        )
