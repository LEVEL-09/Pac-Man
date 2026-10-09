"""Pac-Man game scene manager."""

from mlx_wrapper import KEY_ESC, AssetManager, MLXApp

from pacman.base import Scene
from pacman.menus import MainMenu, PauseMenu


class Game(MLXApp):
    """Entry point for the Pac-Man game.

    Attributes:
        am: game's asset manager.

    """

    def __init__(self, width: int, height: int, title: str) -> None:
        """Initialize the game.

        Args:
            width: width of the game window.
            height: height of the game window.
            title: title of the game window.
        """
        super().__init__((width * 2 + 1) * 32, (height * 2 + 1) * 32 + 99, title)
        self.am = AssetManager("./assets.xml")
        self._scene_stack: list[Scene] = []
        self.push_scene(MainMenu(self))
        self.bind_key(KEY_ESC, lambda: self.push_scene(PauseMenu(self)))

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
            scene (Scene): The scene to push.
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
            new_scene (Scene): The scene to switch to.
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
        if self._current_scene:
            self._current_scene.update()
            self._current_scene.draw(0, 0)
