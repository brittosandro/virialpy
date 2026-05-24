"""High-level workflow for fitting intermolecular potentials."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike

from virialpy.datasets import load_potential_data
from virialpy.fitting import FitResult, fit_potential_scipy
from virialpy.io import save_fit_metrics, save_fit_parameters, save_fit_residuals
from virialpy.potentials import POTENTIALS


def run_fit_workflow(
    data_path: str | Path,
    potential_name: str,
    initial_guess: Sequence[float],
    parameter_names: list[str],
    r_column: str = "r",
    energy_column: str = "energy",
    bounds: tuple[ArrayLike | float, ArrayLike | float] = (-np.inf, np.inf),
    output_dir: str | Path | None = None,
) -> FitResult:
    """Load potential data, select a registered model, fit it, and optionally save results.

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
    output_dir:
        Optional directory where ``fit_parameters.csv``, ``fit_metrics.csv``,
        and ``fit_residuals.csv`` are saved. When ``None``, no files are
        written.

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

    result = fit_potential_scipy(
        data=data,
        potential_func=potential_func,
        initial_guess=initial_guess,
        parameter_names=parameter_names,
        potential_name=potential_name,
        bounds=bounds,
    )

    if output_dir is not None:
        output_path = Path(output_dir)
        save_fit_parameters(result, output_path / "fit_parameters.csv")
        save_fit_metrics(result, output_path / "fit_metrics.csv")
        save_fit_residuals(result, output_path / "fit_residuals.csv")

    return result
