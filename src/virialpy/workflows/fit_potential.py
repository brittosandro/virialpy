"""High-level workflow for fitting intermolecular potentials."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike

from virialpy.datasets import load_potential_data
from virialpy.fitting import FitResult, fit_potential_scipy
from virialpy.potentials import POTENTIALS


def run_fit_workflow(
    data_path: str | Path,
    potential_name: str,
    initial_guess: Sequence[float],
    parameter_names: list[str],
    r_column: str = "r",
    energy_column: str = "energy",
    bounds: tuple[ArrayLike | float, ArrayLike | float] = (-np.inf, np.inf),
) -> FitResult:
    """Load potential data, select a registered model, and fit it with SciPy.

    Parameters
    ----------
    data_path:
        Path to a CSV file containing potential-energy data.
    potential_name:
        Key of the potential in the registry. Built-in values are ``"lj"``,
        ``"ilj"``, and ``"ryd6"``.
    initial_guess:
        Initial parameter values passed to the SciPy fitter.
    parameter_names:
        Names corresponding to each fitted parameter.
    r_column:
        Name of the distance column in the input CSV.
    energy_column:
        Name of the energy column in the input CSV.
    bounds:
        Lower and upper parameter bounds passed to the SciPy fitter.

    Returns
    -------
    FitResult
        Backend-independent result of the potential fit.
    """
    if potential_name not in POTENTIALS:
        available = ", ".join(sorted(POTENTIALS))
        raise ValueError(
            f"Unknown potential_name '{potential_name}'. Available potentials: {available}"
        )

    data = load_potential_data(
        data_path,
        r_column=r_column,
        energy_column=energy_column,
    )
    potential_func = POTENTIALS[potential_name]

    return fit_potential_scipy(
        data=data,
        potential_func=potential_func,
        initial_guess=initial_guess,
        parameter_names=parameter_names,
        potential_name=potential_name,
        bounds=bounds,
    )

