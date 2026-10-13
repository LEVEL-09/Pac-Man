"""Pac-Man game scene manager."""

from mlx_wrapper import AssetManager, MLXApp

from pacman.base import GameContext, Scene
from pacman.menus import MainMenu
from pacman.parser import Config


class Game(MLXApp):
    """Entry point for the Pac-Man game.

    Attributes:
        config: game parsed configuration from the config file.
        am: AssetManager instance.

    """

    def __init__(self) -> None:
        """Initialize the game."""
        config = Config()
        super().__init__(
            (config.maze_width * 2 + 1) * 32,
            (config.maze_height * 2 + 1) * 32 + 64 * 2,
            "Pac-Man",
        )
        am = AssetManager("./assets.xml")
        GameContext.set_context(GameContext(self, am, config))

        # Scene stack
        self._scene_stack: list[Scene] = []
        self.push_scene(MainMenu())

    @property
    def _current_scene(self) -> Scene | None:
        """Get the current scene.

        Returns:
            Scene | None: The current scene, or None if no scene is active.
        """
        return self._scene_stack[-1] if self._scene_stack else None

    def push_scene(self, scene: Scene) -> None:
        """Push a scene onto the stack.

        Args:
            scene: The scene to push.
        """
        if self._current_scene:
            self._current_scene.unmount()

        self._scene_stack.append(scene)
        scene.mount()

    def pop_scene(self) -> None:
        """Pop the current scene from the stack."""
        if self._current_scene:
            self._current_scene.unmount()
            self._scene_stack.pop()
        if self._current_scene:
            self._current_scene.mount()

    def switch_scene(self, new_scene: Scene) -> None:
        """Switch to a new scene completely replacing the current one.

        Args:
            new_scene: The scene to switch to.
        """
        if self._current_scene:
            self._current_scene.unmount()
            self._scene_stack.pop()
        self.push_scene(new_scene)

    def swap_scene(self) -> None:
        """Swap the two top scenes in the stack."""
        if self._current_scene:
            self._current_scene.unmount()
            tmp = self._current_scene
            self._scene_stack[-1] = self._scene_stack[-2]
            self._scene_stack[-2] = tmp
            self._current_scene.mount()

    def update(self) -> None:
        """Update the current scene."""
        print(self.dt)
        if self._current_scene:
            self._current_scene.update()
            self._current_scene.draw()
