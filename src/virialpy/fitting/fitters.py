"""Fitting utilities for intermolecular potentials."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import curve_fit

from virialpy.fitting.results import FitResult


def _require_potential_columns(data: pd.DataFrame) -> None:
    """Raise a clear error when standardized potential columns are missing."""
    missing = [column for column in ["r", "energy"] if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


def _calculate_metrics(observed: NDArray[np.float64], fitted: NDArray[np.float64]) -> tuple[NDArray[np.float64], float, float, float]:
    """Calculate residuals, RMSE, MAE, and coefficient of determination."""
    residuals = observed - fitted
    rmse = float(np.sqrt(np.mean(residuals**2)))
    mae = float(np.mean(np.abs(residuals)))

    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((observed - np.mean(observed)) ** 2))
    r2 = 1.0 if ss_tot == 0.0 and ss_res == 0.0 else 1.0 - ss_res / ss_tot
    return residuals, rmse, mae, float(r2)


def fit_potential_scipy(
    data: pd.DataFrame,
    potential_func: Callable[..., float | NDArray[np.float64]],
    initial_guess: Sequence[float],
    parameter_names: list[str],
    potential_name: str = "custom",
    bounds: tuple[ArrayLike | float, ArrayLike | float] = (-np.inf, np.inf),
) -> FitResult:
    """Fit an intermolecular potential using ``scipy.optimize.curve_fit``.

    Parameters
    ----------
    data:
        Standardized potential dataset with columns ``r`` and ``energy``.
    potential_func:
        Callable with signature ``potential_func(r, *parameters)``.
    initial_guess:
        Initial parameter values passed to ``curve_fit``.
    parameter_names:
        Names corresponding to each fitted parameter.
    potential_name:
        Human-readable name stored in the returned ``FitResult``.
    bounds:
        Lower and upper parameter bounds passed to ``curve_fit``.

    Returns
    -------
    FitResult
        Backend-independent fit summary with fitted parameters, covariance,
        residuals, and basic regression metrics.
    """
    _require_potential_columns(data)

    if len(parameter_names) != len(initial_guess):
        raise ValueError(
            "The number of parameter_names must match the number of values in initial_guess."
        )

    r = pd.to_numeric(data["r"], errors="raise").to_numpy(dtype=float)
    observed = pd.to_numeric(data["energy"], errors="raise").to_numpy(dtype=float)

    fitted_values, covariance = curve_fit(
        potential_func,
        r,
        observed,
        p0=list(initial_guess),
        bounds=bounds,
        maxfev=200000,
    )

    predicted = np.asarray(potential_func(r, *fitted_values), dtype=float)
    residuals, rmse, mae, r2 = _calculate_metrics(observed, predicted)
    parameter_values = {
        name: float(value) for name, value in zip(parameter_names, fitted_values, strict=True)
    }

    return FitResult(
        potential_name=potential_name,
        parameter_names=list(parameter_names),
        parameter_values=parameter_values,
        covariance=covariance,
        residuals=residuals,
        rmse=rmse,
        mae=mae,
        r2=r2,
        success=True,
        message="Fit completed successfully using scipy.optimize.curve_fit.",
        r_values=r,
        observed_values=observed,
        fitted_values=predicted,
    )


def predict_potential(
    r: float | Sequence[float] | ArrayLike,
    potential_func: Callable[..., Any],
    parameters: dict[str, float],
) -> Any:
    """Predict potential-energy values from a parameter dictionary.

    Parameters
    ----------
    r:
        Distance value or values accepted by the potential function.
    potential_func:
        Callable potential model. It must accept ``r`` followed by keyword
        parameters matching ``parameters``.
    parameters:
        Mapping of parameter names to values.

    Returns
    -------
    Any
        Predicted energy values returned by ``potential_func``.
    """
    return potential_func(r, **parameters)
