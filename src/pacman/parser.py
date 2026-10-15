"""Command-line argument parsing and JSON configuration handling.

This module exposes the :class:`Config` class, which loads a JSON
configuration file supplied via the command line, validates its
contents against expected defaults and value ranges, and exposes the
resulting settings as attributes for use by the rest of the game.
"""

import argparse
import logging
import os
from pathlib import Path
from typing import Any

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
    "score": {"pacgum": 10, "super_pacgum": 50, "ghost": 25},
    "maze": {"seed": 42, "width": 20, "height": 20},
    "player": {"lives": 3},
}

RANGES = {
    "game": {"level_max_time": (30, 500)},
    "score": {"pacgum": (5, 100), "super_pacgum": (5, 100), "ghost": (5, 100)},
    "maze": {"width": (15, 25), "height": (15, 25)},
    "player": {"lives": (1, 10)},
}


class Config:
    """Loads, validates, and exposes the game's configuration.

    On instantiation, the configuration file path is taken from the
    command line, its contents are loaded and validated against
    :data:`DEFAULTS` and :data:`RANGES`, and the resulting values are
    exposed as instance attributes (e.g. ``game_time``,
    ``pacgum_score``, ``maze_seed``, etc.).
    """

    logger = logging.getLogger()

    def __init__(self) -> None:
        """Parse arguments, load the config file, and validate it."""
        self._file_path = Config._parse_args()
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

    @staticmethod
    def _parse_args() -> Path:
        """Parse command-line arguments and return the config file path.

        Returns:
            The path to the JSON configuration file passed on the command
            line.

        Raises:
            ValueError: If the given path does not have a ``.json``
                extension.
        """
        parser = argparse.ArgumentParser()

        parser.add_argument("config", help="path to config file")

        args = parser.parse_args()
        config_path = Path(args.config)
        if config_path.suffix != ".json":
            raise ValueError("config file must be a JSON file")
        return config_path

    def load(self) -> dict[Any, Any]:
        """Load and parse the JSON configuration file.

        Returns:
            The parsed configuration as a dictionary.

        Raises:
            TypeError: If the file's top-level JSON value is not an
                object.
            OSError: If the file cannot be opened or read.
            ValueError: If the file's contents are not valid JSON.
        """
        try:
            with open(self._file_path, "r") as f:
                data: Any = commentjson.load(f)

                if not isinstance(data, dict):
                    raise TypeError(
                        f"Configuration file {self._file_path} "
                        "must contain a JSON object"
                    )
                return data

        except OSError as e:
            raise OSError(
                f"Error loading file {self._file_path}:\n\t{e.strerror}"
            )

        except commentjson.JSONLibraryException as e:
            raise ValueError(
                f"Error parsing JSON file {self._file_path}"
            ) from e

    def validate(self, data: dict[Any, Any]) -> None:
        """Validate all configuration sections in place.

        Any missing or invalid section is replaced with its default
        values from :data:`DEFAULTS`. Valid sections are further
        checked key-by-key via :meth:`_validate_section`.

        Args:
            data: The configuration dictionary to validate and
                mutate in place.
        """
        for section, section_defaults in DEFAULTS.items():
            if section not in data:
                self.logger.warning(
                    "Missing '%s' section. Using default values.", section
                )
                data[section] = dict(section_defaults)
                continue

            value = data[section]

            if not isinstance(value, dict):
                self.logger.warning(
                    "Invalid value for %s. Using default value.", section
                )
                data[section] = dict(section_defaults)
                continue

            self._validate_section(section, value, section_defaults)

    def _validate_section(
        self, section: str, value: dict[Any, Any], defaults: dict[Any, Any]
    ) -> None:
        """Validate and clamp the keys of a single config section.

        Missing or non-integer keys are replaced with their default
        value. The ``maze.seed`` key is required to be non-negative.
        All other keys are clamped to the bounds defined in
        :data:`RANGES`. Warnings are logged for any correction made.

        Args:
            section: The name of the configuration section (e.g.
                ``"maze"``).
            value: The section's dictionary of values, mutated in
                place.
            defaults: The default values for this section.
        """
        for key, default in defaults.items():
            if key not in value:
                self.logger.warning(
                    "Missing '%s' in '%s'. Using default value: %s.",
                    key,
                    section,
                    default,
                )
                value[key] = default
                continue

            raw = value[key]

            if not isinstance(raw, int):
                self.logger.warning(
                    "Invalid value for '%s' in '%s'. Using default value: %s.",
                    key,
                    section,
                    default,
                )
                value[key] = default
                continue

            if section == "maze" and key == "seed":
                if raw < 0:
                    self.logger.warning(
                        "Invalid value for 'seed' in 'maze'. Must be a "
                        "positive number. Using default value: %s.",
                        default,
                    )
                    value[key] = default
                else:
                    self.logger.info(
                        "Value for 'seed' in 'maze' set to %s.",
                        raw,
                    )
                continue

            low, high = RANGES[section][key]
            if raw < low or raw > high:
                clamped = max(low, min(high, raw))
                self.logger.warning(
                    "Value for '%s' in '%s' out of range (%s-%s). "
                    "Clamping to %s.",
                    key,
                    section,
                    low,
                    high,
                    clamped,
                )
                value[key] = clamped

            self.logger.info(
                "Value for '%s' in '%s' set to %s.",
                key,
                section,
                value[key],
            )
