"""YAML configuration loaders."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a non-empty YAML run configuration.

    Parameters
    ----------
    path:
        Path to a YAML file.

    Returns
    -------
    dict[str, Any]
        Parsed configuration dictionary.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML file: {config_path}") from exc

    if config is None:
        raise ValueError(f"Configuration file is empty: {config_path}")
    if not isinstance(config, dict):
        raise ValueError("Configuration root must be a mapping.")

    return config
