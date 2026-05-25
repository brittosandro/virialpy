"""Analysis helpers for comparing Monte Carlo integration with references."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Raise a clear error when required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


def compare_monte_carlo_with_integrators(
    b2_results_path: str | Path,
    monte_carlo_name: str = "monte_carlo",
    reference_integrators: Sequence[str] | None = None,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Compare Monte Carlo B(T) results against other integrators."""
    data = pd.read_csv(b2_results_path)
    _require_columns(data, ["temperature", "potential", "integrator", "b2"])

    if monte_carlo_name not in set(data["integrator"]):
        raise ValueError(f"Monte Carlo integrator '{monte_carlo_name}' was not found.")

    if reference_integrators is None:
        reference_integrators = sorted(
            integrator for integrator in data["integrator"].unique() if integrator != monte_carlo_name
        )

    mc = data.loc[data["integrator"] == monte_carlo_name, ["temperature", "potential", "b2"]].rename(
        columns={"b2": "b2_monte_carlo"}
    )
    rows = []
    for reference_integrator in reference_integrators:
        reference = data.loc[
            data["integrator"] == reference_integrator,
            ["temperature", "potential", "b2"],
        ].rename(columns={"b2": "b2_reference"})
        merged = mc.merge(reference, on=["temperature", "potential"], how="inner")
        merged["reference_integrator"] = reference_integrator
        merged["difference"] = merged["b2_monte_carlo"] - merged["b2_reference"]
        merged["abs_difference"] = merged["difference"].abs()
        merged["percent_difference"] = np.where(
            merged["b2_reference"] != 0,
            (merged["difference"] / merged["b2_reference"]).abs() * 100.0,
            np.nan,
        )
        rows.append(merged)

    result = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    columns = [
        "temperature",
        "potential",
        "reference_integrator",
        "b2_monte_carlo",
        "b2_reference",
        "difference",
        "abs_difference",
        "percent_difference",
    ]
    result = result.loc[:, columns]

    if output_path is not None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output, index=False)

    return result


def summarize_monte_carlo_comparison(comparison_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize Monte Carlo differences by potential and reference integrator."""
    _require_columns(
        comparison_df,
        ["potential", "reference_integrator", "difference", "abs_difference", "percent_difference"],
    )
    rows = []
    for (potential, reference_integrator), group in comparison_df.groupby(
        ["potential", "reference_integrator"], dropna=False
    ):
        rows.append(
            {
                "potential": potential,
                "reference_integrator": reference_integrator,
                "mean_abs_difference": float(group["abs_difference"].mean()),
                "max_abs_difference": float(group["abs_difference"].max()),
                "rmse_difference": float(np.sqrt(np.mean(group["difference"] ** 2))),
                "mean_percent_difference": float(group["percent_difference"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("mean_abs_difference", ascending=True).reset_index(drop=True)

