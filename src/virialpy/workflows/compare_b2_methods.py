"""Workflow for comparing direct and partitioned B(T) calculations."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from virialpy.analysis import calculate_grouped_b2_metrics


def _require_columns(data: pd.DataFrame, columns: list[str], dataset_name: str) -> None:
    """Raise a clear error when required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{dataset_name} is missing required column(s): {', '.join(missing)}")


def _save_csv(data: pd.DataFrame, path: str | Path) -> None:
    """Save CSV output after creating parent directories."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output, index=False)


def prepare_b2_method_comparison(
    direct_path: str | Path,
    partitioned_path: str | Path,
    experimental_path: str | Path,
    direct_integrator: str = "scipy_quad",
    temperature_column_exp: str = "Temperatura",
    b2_column_exp: str = "B(segundo coef. virial) [cm³/mol]",
    output_comparison_path: str | Path | None = None,
    output_metrics_path: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare direct-vs-partitioned B(T) comparison against experiment."""
    direct = pd.read_csv(direct_path)
    partitioned = pd.read_csv(partitioned_path)
    experimental = pd.read_csv(experimental_path)

    _require_columns(direct, ["temperature", "potential", "integrator", "b2"], "direct data")
    _require_columns(partitioned, ["temperature", "potential", "b_total"], "partitioned data")
    _require_columns(
        experimental,
        [temperature_column_exp, b2_column_exp],
        "experimental data",
    )

    direct_prepared = direct.loc[direct["integrator"] == direct_integrator].copy()
    direct_prepared["method"] = "direct"
    direct_prepared["b2_calc"] = direct_prepared["b2"]
    direct_columns = ["temperature", "potential", "method", "b2_calc"]
    if "potential_label" in direct_prepared.columns:
        direct_columns.append("potential_label")
    direct_prepared = direct_prepared.loc[:, direct_columns]

    partitioned_prepared = partitioned.copy()
    partitioned_prepared["method"] = "partitioned"
    partitioned_prepared["b2_calc"] = partitioned_prepared["b_total"]
    partitioned_prepared = partitioned_prepared.loc[
        :,
        ["temperature", "potential", "method", "b2_calc"],
    ]

    calculated = pd.concat([direct_prepared, partitioned_prepared], ignore_index=True)
    calculated["temperature"] = pd.to_numeric(calculated["temperature"], errors="raise")
    calculated["b2_calc"] = pd.to_numeric(calculated["b2_calc"], errors="raise")

    experimental = experimental.loc[:, [temperature_column_exp, b2_column_exp]].copy()
    experimental.columns = ["temperature", "b2_exp"]
    experimental["temperature"] = pd.to_numeric(experimental["temperature"], errors="raise")
    experimental["b2_exp"] = pd.to_numeric(experimental["b2_exp"], errors="raise")

    comparison = calculated.merge(experimental, on="temperature", how="inner")
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
        "potential",
        "method",
    ]
    remaining_columns = [column for column in comparison.columns if column not in front_columns]
    comparison = comparison.loc[:, [*front_columns, *remaining_columns]]

    metrics = calculate_grouped_b2_metrics(comparison, ["potential", "method"])

    if output_comparison_path is not None:
        _save_csv(comparison, output_comparison_path)
    if output_metrics_path is not None:
        _save_csv(metrics, output_metrics_path)

    return comparison, metrics

