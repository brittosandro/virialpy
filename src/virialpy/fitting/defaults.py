"""Default fitting settings for built-in intermolecular potentials."""

from __future__ import annotations

from typing import Any


def get_default_fit_settings(potential_name: str) -> dict[str, Any]:
    """Return default parameter names and initial guesses for a potential.

    Parameters
    ----------
    potential_name:
        Short potential name. Supported values are ``"lj"``, ``"ilj"``, and
        ``"ryd6"``.

    Returns
    -------
    dict[str, Any]
        Dictionary containing ``parameter_names`` and ``initial_guess``.

    Raises
    ------
    ValueError
        If the potential name is not supported.
    """
    defaults: dict[str, dict[str, Any]] = {
        "lj": {
            "parameter_names": ["epsilon", "sigma"],
            "initial_guess": [0.25, 3.5],
        },
        "ilj": {
            "parameter_names": ["de", "req", "beta"],
            "initial_guess": [0.25, 3.8, 8.0],
        },
        "ryd6": {
            "parameter_names": ["de", "re", "c1", "c2", "c3", "c4", "c5", "c6"],
            "initial_guess": [0.25, 3.8, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        },
    }

    if potential_name not in defaults:
        available = ", ".join(sorted(defaults))
        raise ValueError(
            f"Unsupported potential '{potential_name}'. Available defaults: {available}"
        )

    settings = defaults[potential_name]
    return {
        "parameter_names": list(settings["parameter_names"]),
        "initial_guess": list(settings["initial_guess"]),
    }
