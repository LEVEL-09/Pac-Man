"""Entry point script for launching the Pac-Man game."""

from mlx_wrapper import AssetManager, MLXApp

from src.pacman.base import Scene
from src.pacman.menus import MainMenu


class Game(MLXApp):
    def __init__(self, width: int, height: int, title: str) -> None:
        super().__init__(width, height, title)
        self.am = AssetManager("./assets.xml")
        self._scene_stack = []
        self.push_scene(MainMenu(self))

    @property
    def _current_scene(self) -> Scene | None:
        return self._scene_stack[-1] if self._scene_stack else None

    def push_scene(self, scene: Scene) -> None:
        if self._current_scene:
            self._current_scene.unmount()

        self._scene_stack.append(scene)
        scene.mount()

    def pop_scene(self) -> None:
        if self._current_scene:
            self._current_scene.unmount()
            self._scene_stack.pop()
        if self._current_scene:
            self._current_scene.mount()
    
    def switch_scene(self, new_scene: Scene) -> None:
        if self._current_scene:
            self._current_scene.unmount()
            self._scene_stack.pop()
        self.push_scene(new_scene)

    def update(self) -> None:
        if self._current_scene:
            self._current_scene.update()
            self._current_scene.draw(0, 0)


if __name__ == "__main__":
    Game(800, 600, "Pac-Man").start()
