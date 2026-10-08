"""Entry point script for launching the Pac-Man game."""

from mlx_wrapper import AssetManager, MLXApp, Sprite

from pacman.ghost import Blinky, Inky, Pinky, Clyde
from pacman.maze import Maze
from pacman.player import Player
from pacman.ghost import GhostState


class Game(MLXApp):
    def __init__(self, width, height):
        super().__init__((width * 2 + 1) * 32, (height * 2 + 1) * 32 + 99, "PAC-MAN")
        self.am = AssetManager("assets.xml")
        self.maze = Maze(self, width, height, 42, 4)
        
        self.pacman = Player(self)
        self.blinky = Blinky(self)
        self.inky = Inky(self)
        self.pinky = Pinky(self)
        self.clyde = Clyde(self)

    def update(self) -> None:
        self.pacman.update()

        self.blinky.update()
        self.inky.update()
        self.pinky.update()
        self.clyde.update()

        if self.blinky.curr_cell == self.pacman.curr_cell:
            self.blinky.state = GhostState.EATEN
        if self.inky.curr_cell == self.pacman.curr_cell:
            self.inky.state = GhostState.EATEN
        if self.pinky.curr_cell == self.pacman.curr_cell:
            self.pinky.state = GhostState.EATEN
        if self.clyde.curr_cell == self.pacman.curr_cell:
            self.clyde.state = GhostState.EATEN
            

        self.maze.draw()

        self.pacman.draw()
        self.blinky.draw()
        self.inky.draw()
        self.pinky.draw()
        self.clyde.draw()

def main() -> None:
    """Run the Pac-Man game."""
    Game(20, 25).start()


if __name__ == "__main__":
    main()
