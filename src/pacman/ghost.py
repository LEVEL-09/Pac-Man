from abc import ABC, abstractmethod
from enum import Enum, auto

from mlx_wrapper import AssetManager

from pacman.hitbox import Hitbox


class GhostState(Enum):
    SCATTER = auto()
    CHASE = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class Ghost(ABC):
    def __init__(
        self,
        corner: tuple[int, int],
        speed: float,
        asset_manager: AssetManager,
    ) -> None:
        self.hitbox = Hitbox(3, 4, 24, 24)
        self.position = corner
        self.corner = corner
        self.speed = speed
        self.state = GhostState.SCATTER
        self.asset_manager = asset_manager

    def scatter_mode(self, maze: list[list[int]]) -> None:
        pass

    @abstractmethod
    def chase_mode(self) -> None:
        pass

    def frightened_mode(self) -> None:
        pass

    def eaten_mode(self) -> None:
        pass

    def update(self, maze: list[list[int]]) -> None:
        if self.state == GhostState.SCATTER:
            self.scatter_mode(maze)
        elif self.state == GhostState.CHASE:
            self.chase_mode()
        elif self.state == GhostState.FRIGHTENED:
            self.frightened_mode()
        elif self.state == GhostState.EATEN:
            self.eaten_mode()
