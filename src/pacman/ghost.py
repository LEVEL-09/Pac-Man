from abc import ABC, abstractmethod
from enum import Enum, auto


class GhostState(Enum):
    CHASE = auto()
    SCATTER = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class Ghost(ABC):
    def __init__(self, position: tuple[int, int], corner: tuple[int, int], speed: float):
        self.position = position
        self.corner = corner
        self.speed = speed
        self.is_edible = False
        self.state = True

    def scatter_mode(self) -> None:
        pass

    @abstractmethod
    def chase_mode(self) -> None:
        pass

    def frightened_mode(self) -> None:
        pass

    def eaten_mode(self) -> None:
        pass
