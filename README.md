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

The highscore system stores player names and scores in a local `highscores.json` file. When a run ends, the player is asked to type in a username and the score is saved together with the associated name. The leaderboard is then loaded and sorted in descending order, which means the best results always appear first.

This approach was chosen because it keeps the project lightweight, dependency-free, and fully compatible with the constraints of the 42 curriculum. Instead of relying on a full backend or online service, the game uses a simple JSON-based persistence mechanism that is easy to validate, easy to debug, and easy to extend if more features are needed later.

The leaderboard is intentionally simple but robust: invalid records are ignored, empty names are discarded, and corrupted or missing files are handled gracefully without crashing the game. This makes the feature resilient while still preserving the classic arcade loop of "play, finish, enter name, replay to beat your rank".

# Maze Generation

Maze generation is handled through the external `A-Maze-ing` package, integrated through the `MazeGenerator` class. Each level is created from a deterministic seed derived from the base configuration value, allowing a reproducible sequence of mazes while still keeping every level distinct.

The workflow is as follows:

1. a base seed is loaded from the config file;
2. a list of per-level seeds is derived from that base value;
3. each maze is generated using the corresponding seed;
4. the raw maze layout is converted from wall bitmasks into an autotiled grid;
5. wall tiles are rendered as a single composed sprite using the project assets;
6. empty cells are checked for reachability and collectible pellets are placed at valid open positions.

# Implementation

The implementation follows a clean object-oriented structure centered around the game loop, scene management, and gameplay entities.

At the highest level, the `Game` class inherits from the custom `MLXApp` wrapper and owns the active scene stack. Each scene extends the `Scene` base class and manages its own drawing, input bindings, and lifecycle. This design makes the menu system, gameplay loop, pause state, instructions screen, and end-of-game states easy to separate while keeping a single consistent application flow.

Core gameplay entities are represented by dedicated classes:

- `MovingEntity` base class for all the game's moving entities: Pac-Man and Ghosts
- `Player(MovingEntity)` encapsulates Pac-Man's movement callbacks, animation states, and collision logic;
- `Ghost(MovingEntity)` is an abstract base class shared by all enemy types; subclasses like `Blinky(Ghost)`, `Pinky(Ghost)`, `Inky(Ghost)`, and `Clyde(Ghost)` implement different AI strategies and target selection behaviors;
- `Maze` handles generation, autotiling, render composition, pellet placement, and collectible tracking;
- `Config` loads and validates JSON configuration options, clamping invalid values and providing safe defaults.

The project also uses a shared `GameContext` manager to expose the active game instance, asset manager, logger, and configuration to all scenes and entities. This avoids global state clutter while maintaining consistent access across the codebase.

Rendering is handled through `mlx_wrapper` and sprite/animation assets stored in the `assets/` directory. Collision detection is performed through hitboxes, while movement logic is driven by tile-based direction and pathfinding. The result is a modular code structure that balances readability, extensibility, and gameplay correctness.

# General Software Architecture

The architecture follows a layered, scene-driven model with a shared application context.

- `pac-man.py` acts as the entry point and starts the game;
- `src/pacman/game.py` initializes the application, creates the asset manager, and manages the scene stack;
- `src/pacman/base.py` defines the shared `GameContext`, `Scene`, and `MovingEntity` abstractions;
- `src/pacman/parser.py` handles command-line config loading and validation;
- `src/pacman/maze.py` generates and renders levels;
- `src/pacman/player.py` defines Pac-Man's behaviour and animations;
- `src/pacman/ghost.py` contains the ghost AI system and state machines;
- `src/pacman/scenes.py` contains the menu, gameplay, pause, instruction, and leaderboard scenes;
- `src/pacman/menus.py` provides the interactive menu widgets and cheat system;
- `src/pacman/ui.py` contains the keyboard and text input utilities used by the game;`
- `src/pacman/error_handler.py` centralizes error handling and runtime safety.

The overall relationship between these components is straightforward: the `Game` owns the current scene, the current scene owns the canvas to which it draws everything and the entities, and those entities interact through the `Maze` and shared context. This keeps the system decoupled enough to support future additions—new scenes, enemy AI patterns, or different gameplay modes—without rewriting the core loop.

# Project Management

The project was managed with a milestone-based workflow aimed at keeping each feature clearly separated and testable. We organized the work around core gameplay features, rendering and asset integration, maze generation, AI behavior, configuration handling, and release packaging. This allowed the team to progress iteratively while staying focused on the main game loop and the 42 project constraints.

The project planning materials and task tracking notes are kept in the dedicated project management directory:

- [Project Management](project-management/)
