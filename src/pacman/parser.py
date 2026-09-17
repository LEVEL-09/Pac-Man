import argparse
import logging
import os
from pathlib import Path

import commentjson

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/pacman.log",
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

DEFAULTS = {
    "game": {"level_max_time": 90},
    "score": {"pacgum": 10, "super_pacgum": 50, "ghost": 20},
    "maze": {"seed": 42, "width": 20, "height": 20},
    "player": {"lives": 3},
}

RANGES = {
    "game": {"level_max_time": (30, 500)},
    "score": {"pacgum": (5, 100), "super_pacgum": (5, 100), "ghost": (5, 100)},
    "maze": {"width": (10, 50), "height": (10, 50)},
    "player": {"lives": (1, 10)},
}


def parse_args() -> Path:
    parser = argparse.ArgumentParser()

    parser.add_argument("config", help="path to config file")

    args = parser.parse_args()
    config_path = Path(args.config)
    if config_path.suffix != ".json":
        raise ValueError("config file must be a JSON file")
    return config_path


class Config:
    def __init__(self) -> None:
        self._file_path = parse_args()
        self._data = self.load()
        self.validate(self._data)

        self.game_time = self._data["game"]["level_max_time"]
        self.pacgum_score = self._data["score"]["pacgum"]
        self.super_pacgum_score = self._data["score"]["super_pacgum"]
        self.ghost_score = self._data["score"]["ghost"]
        self.maze_seed = self._data["maze"]["seed"]
        self.maze_width = self._data["maze"]["width"]
        self.maze_height = self._data["maze"]["height"]
        self.player_lives = self._data["player"]["lives"]

    def load(self) -> dict:
        with open(self._file_path, "r") as f:
            return commentjson.load(f)

    def validate(self, data: dict) -> None:
        logger = logging.getLogger()

        for section, section_defaults in DEFAULTS.items():
            if section not in data:
                logger.warning(
                    "Missing '%s' section. Using default values.", section
                )
                data[section] = dict(section_defaults)
                continue

            value = data[section]

            if not isinstance(value, dict):
                logger.warning(
                    "Invalid value for %s. Using default value.", section
                )
                data[section] = dict(section_defaults)
                continue

            self._validate_section(logger, section, value, section_defaults)

    def _validate_section(
        self, logger: logging.Logger, section: str, value: dict, defaults: dict
    ) -> None:
        for key, default in defaults.items():
            if key not in value:
                logger.warning(
                    "Missing '%s' in '%s'. Using default value: %s.",
                    key,
                    section,
                    default,
                )
                value[key] = default
                continue

            raw = value[key]

            if not isinstance(raw, int):
                logger.warning(
                    "Invalid value for '%s' in '%s'. Using default value: %s.",
                    key,
                    section,
                    default,
                )
                value[key] = default
                continue

            if section == "maze" and key == "seed":
                if raw < 0:
                    logger.warning(
                        "Invalid value for 'seed' in 'maze'. Must be a positive "
                        "number. Using default value: %s.",
                        default,
                    )
                    value[key] = default
                continue

            low, high = RANGES[section][key]
            if raw < low or raw > high:
                clamped = max(low, min(high, raw))
                logger.warning(
                    "Value for '%s' in '%s' out of range (%s-%s). Clamping to %s.",
                    key,
                    section,
                    low,
                    high,
                    clamped,
                )
                value[key] = clamped
