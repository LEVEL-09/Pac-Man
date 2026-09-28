from abc import ABC, abstractmethod


class Ghost(ABC):
    def __init__(self, respwn_direction: tuple[int, int]):
        self.respwn_direction = respwn_direction

    def scatter_mode(self) -> None:
        pass

    @abstractmethod
    def chase_mode(self) -> None:
        pass

    def frightened_mode(self) -> None:
        pass

    def eaten_mode(self) -> None:
        pass
