### Problems to fix

- `Scene` allocates a full-window canvas and star field for every
  scene
- Ghosts each allocate a maze-sized `drawable_path` sprite
- `Maze.pacgum_canvas` is allocated in every `create_maze_sprite` call and never used
- `find_path` is unoptimized:
  - it copies the whole path per visited node. use a `parent` dict and rebuild the path once at the end
  - runs every frame for every ghost, and also from `at_tile_center`. only run when the target changes or at a tile center
- `MainMenu.update` gets `logo` and the font every frame

- might run into circular dependency problems (e.g.)`GamePlayScene` needs to push a `PauseMenu`
  (`menus.py` already imports `scenes.py`).
- make dependency passing consistent. Currently:
    `Maze(game, am, ...)`, `Keyboard(game, am, ...)`,
    `Player(maze, am, speed)`, `Ghost(player, am, maze, ...)`,
    `MovingEntity(am, maze, ...)`.
  - `am` is redundant when `game` is passed (`game.am`).
  - `Maze` only needs `game.height`: pass `window_height`
  - Entities can use `maze.am` instead of taking their own `am`.
- remove `Scene.get_config_attr(str)` use `self.game.config` directly
- Replace the literal `32` with one shared `CELL_SIZE` constant
- Ghost/entity duplication:
  - add a `_load_directional_animations(prefix)` helper for the repeated `up/down/left/right` blocks
  - `frightened_mode` repeats the random-cell pick and reachability check
    twice. Use a single loop
  - `Ghost.update` state `if/elif` and Pinky/Inky target and arrow `if/elif` chains can become dictionary lookups
- `self.move(dt)` instead of `super().move(dt)` in `Ghost.update` and `Player.update`
- `Ghost.state` (`GhostState`) vs `curr_state` confusingly named, rename to `animation_key`

- Clean up the `Scene` API:
  - `Menu.update` is a redundant abstract function
  - `draw(x, y)` parameters are unused by every scene
  - `set_game`/`get_game` are classmethods that ignore `cls`
  - `Scene.__init__` stores `self.game` while `get_game()` is available (PICK ONE)
- `Maze` still uses the global `random.seed(seed)`. use local `rng = random.Random(seed)` so ghost randomness isn't affected