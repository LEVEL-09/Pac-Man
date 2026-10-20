*This project has been created as part of the 42 curriculum by mkhoubaz, abouzkra.*

# Pac-Man

## Description

This project is a modern, object-oriented recreation of the classic 1980 arcade game **Pac-Man**. The objective of the game is to navigate Pac-Man through a series of randomly generated mazes, eating Pacgums while avoiding ghosts or hunting them when empowered by a Super-Pacgum.

#### Key Features
- **Custom Configuration**: Fully configurable game parameters via a JSON config file.
- **Maze Generation**: Integration with the external `A-Maze-ing` package to construct mazes dynamically.
- **Robust Gameplay and UI**: Multi-level progression with a dynamic HUD, highscore tracking, pause menu, cheat menu...
- **Deployment**: Packaged and released as a one file binary on the Itch.io platform.

## Instructions

#### Prerequisites
- Python 3.14 or higher
- `uv` package manager 0.12.0 or higher

#### Installation
Install the dependencies:
```bash
make install
# or
make
```
#### Running the game
To launch the game with config file:
```bash
make run config.json
# or
uv run python3 pac-man.py config.json
```

#### Debug mode
Run the game using python's debugger (`pdb`):
```bash
make debug
# or
uv run python3 -m pdb pac-man.py config.json
```
#### Linting the project
Run linters (`flake8`) and static type checking (`mypy`):
```bash
make lint
# for strict linting
make lint-strict
```

#### Cleanup
Remove temporary files, bytecode caches and type checking files:
```bash
make clean
```

#### Build the executable
Run the packaging script with the spec file at root:
```bash
make build
```

# Resources

- [Original Pac-Man game](https://pacman.live/play.html)
- [Scene Manager Architecture for Game States](https://grasp.study/modules/3e9be1c5-0e3b-49d1-b874-5669f37777e8/lessons/f705e5c2-cb4e-405d-b4c4-b86343625592)
- [Animated Dark Night Sky](https://1bestcsharp.blogspot.com/2024/10/python-dark-night-sky-animation-using-tkinter.html)
- [Autotiling Technique](https://excaliburjs.com/blog/Autotiling%20Technique/)
- [Pac-Man Ghost AI Explained (Video)](https://www.youtube.com/watch?v=ataGotQ7ir8)
- [MiniLibX public repo](https://github.com/42school/mlx_CLXV)
- [MiniLibX documenation](https://harm-smits.github.io/42docs/libs/minilibx/getting_started.html)
- [PyInstaller documentation](https://pyinstaller.org/en/stable/)

# Configuration

The game accepts a JSON config file supporting single-line and C-style comments. Invalid or missing key values gracefully fall back to default parameters without crashing.

### `game`
| Key | Default | Description | Range |
| :--- | :--- | :--- | :--- |
| `level_max_time` | `150` | Time limit in seconds allowed to complete each level. | 150 -> 300 |

### `score`
| Key | Default | Description | Range |
| :--- | :--- | :--- | :--- |
| `pacgum` | `10` | Points awarded to the player for eating a standard pacgum. | 5 -> 100 |
| `super_pacgum` | `50` | Points awarded for eating a super-pacgum (power pellet). | 5 -> 100 |
| `ghost` | `25` | Points awarded for eating an edible ghost.* | 5 -> 100 |

### `maze`
| Key | Default | Description | Range |
| :--- | :--- | :--- | :--- |
| `seed` | `42` | Random seed used for generating the first level's maze. | ___ |
| `width` | `15` | Width of the generated level maze. | 15 -> 25 |
| `height` | `15` | Height of the generated level maze. | 15 -> 25 |

### `player`
| Key | Default | Description | Range |
| :--- | :--- | :--- | :--- |
| `lives` | `3` | Initial number of lives the player starts the game with. | 1 -> 10 |

# HighScore

# Maze Generation

# Implementation

# General Software Architecture

# Project Management
