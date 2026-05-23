"""CSV writers for fitting results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from virialpy.fitting import FitResult


def _ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory for an output path when needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def save_fit_parameters(result: FitResult, path: str | Path) -> None:
    """Save fitted parameter values to a CSV file.

    The output contains the columns ``potential``, ``parameter``, and
    ``value``.
    """
    output_path = _ensure_parent_directory(path)
    data = pd.DataFrame(
        [
            {
                "potential": result.potential_name,
                "parameter": parameter,
                "value": result.parameter_values[parameter],
            }
            for parameter in result.parameter_names
        ]
    )
    data.to_csv(output_path, index=False)


def save_fit_metrics(result: FitResult, path: str | Path) -> None:
    """Save fit metrics to a one-row CSV file."""
    output_path = _ensure_parent_directory(path)
    data = pd.DataFrame(
        [
            {
                "potential": result.potential_name,
                "rmse": result.rmse,
                "mae": result.mae,
                "r2": result.r2,
                "success": result.success,
                "message": result.message,
            }
        ]
    )
    data.to_csv(output_path, index=False)


def save_fit_residuals(result: FitResult, path: str | Path) -> None:
    """Save fitted values and residuals to a CSV file.

    Raises
    ------
    ValueError
        If the ``FitResult`` does not contain ``r_values``,
        ``observed_values``, or ``fitted_values``.
    """
    if result.r_values is None or result.observed_values is None or result.fitted_values is None:
        raise ValueError(
            "FitResult must contain r_values, observed_values, and fitted_values "
            "to save residuals."
        )

    output_path = _ensure_parent_directory(path)
    data = pd.DataFrame(
        {
            "r": result.r_values,
            "energy_observed": result.observed_values,
            "energy_fitted": result.fitted_values,
            "residual": result.residuals,
        }
    )
    data.to_csv(output_path, index=False)

