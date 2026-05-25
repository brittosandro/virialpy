"""Workflow for validating calculated B2 values against experiment."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from virialpy.analysis import calculate_grouped_b2_metrics


def _require_columns(data: pd.DataFrame, columns: Sequence[str], dataset_name: str) -> None:
    """Raise a clear error when required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{dataset_name} is missing required column(s): {', '.join(missing)}")


def _save_csv(data: pd.DataFrame, path: str | Path) -> None:
    """Save a DataFrame to CSV after creating parent directories."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output, index=False)


def validate_b2_against_experiment(
    calculated_path: str | Path,
    experimental_path: str | Path,
    temperature_column_exp: str = "temperature",
    b2_column_exp: str = "b2",
    group_columns: Sequence[str] = ("potential", "integrator"),
    output_comparison_path: str | Path | None = None,
    output_metrics_path: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare calculated B2 values with experimental data.

    The calculated CSV must contain ``temperature``, ``b2``, ``potential``,
    and ``integrator``. The experimental CSV is read using configurable
    temperature and B2 column names.
    """
    calculated = pd.read_csv(calculated_path)
    experimental = pd.read_csv(experimental_path)

    calculated_required = ["temperature", "b2", "potential", "integrator"]
    _require_columns(calculated, calculated_required, "calculated data")
    _require_columns(experimental, [temperature_column_exp, b2_column_exp], "experimental data")

    calculated = calculated.copy()
    experimental = experimental.loc[:, [temperature_column_exp, b2_column_exp]].copy()
    calculated["temperature"] = pd.to_numeric(calculated["temperature"], errors="raise")
    calculated["b2"] = pd.to_numeric(calculated["b2"], errors="raise")
    experimental.columns = ["temperature", "b2_exp"]
    experimental["temperature"] = pd.to_numeric(experimental["temperature"], errors="raise")
    experimental["b2_exp"] = pd.to_numeric(experimental["b2_exp"], errors="raise")

    comparison = calculated.rename(columns={"b2": "b2_calc"}).merge(
        experimental,
        on="temperature",
        how="inner",
    )
    comparison["residual"] = comparison["b2_calc"] - comparison["b2_exp"]
    comparison["abs_error"] = comparison["residual"].abs()
    comparison["percent_error"] = np.where(
        comparison["b2_exp"] != 0,
        (comparison["residual"] / comparison["b2_exp"]).abs() * 100.0,
        np.nan,
    )

    front_columns = [
        "temperature",
        "b2_exp",
        "b2_calc",
        "residual",
        "abs_error",
        "percent_error",
    ]
    remaining_columns = [column for column in comparison.columns if column not in front_columns]
    comparison = comparison.loc[:, [*front_columns, *remaining_columns]]

    metrics = calculate_grouped_b2_metrics(comparison, group_columns)

    if output_comparison_path is not None:
        _save_csv(comparison, output_comparison_path)
    if output_metrics_path is not None:
        _save_csv(metrics, output_metrics_path)

    return comparison, metrics

