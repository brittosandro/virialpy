"""Workflow for fitting and comparing multiple intermolecular potentials."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from virialpy.datasets import load_potential_data
from virialpy.fitting import FitResult, fit_potential_scipy
from virialpy.io import save_fit_metrics, save_fit_parameters, save_fit_residuals
from virialpy.plotting import plot_fit_diagnostics, plot_fit_residuals, plot_fit_result
from virialpy.potentials import POTENTIALS


def summarize_fit_results(results: dict[str, FitResult]) -> pd.DataFrame:
    """Summarize fit metrics for multiple fitted potential models.

    Parameters
    ----------
    results:
        Mapping from model short name to ``FitResult``.

    Returns
    -------
    pandas.DataFrame
        Table with columns ``model``, ``potential``, ``rmse``, ``mae``, ``r2``,
        and ``success``, sorted by increasing RMSE.
    """
    summary = pd.DataFrame(
        [
            {
                "model": model_name,
                "potential": result.potential_name,
                "rmse": result.rmse,
                "mae": result.mae,
                "r2": result.r2,
                "success": result.success,
            }
            for model_name, result in results.items()
        ]
    )
    return summary.sort_values("rmse", ascending=True).reset_index(drop=True)


def run_potential_comparison_workflow(
    data_path: str | Path,
    models: list[dict[str, Any]],
    r_column: str = "r",
    energy_column: str = "energy",
    results_dir: str | Path | None = None,
    figures_dir: str | Path | None = None,
) -> dict[str, FitResult]:
    """Fit multiple registered potentials to one dataset and compare them.

    Parameters
    ----------
    data_path:
        Path to the CSV file containing potential-energy data.
    models:
        List of model dictionaries. Each dictionary must contain ``name``,
        ``initial_guess``, ``parameter_names``, and ``label``. ``bounds`` is
        optional and defaults to unconstrained fitting.
    r_column, energy_column:
        Input CSV column names used by ``load_potential_data``.
    results_dir:
        Optional base directory for per-model CSV outputs and the comparison
        metrics table.
    figures_dir:
        Optional directory for per-model fit, residual, and diagnostic figures.

    Returns
    -------
    dict[str, FitResult]
        Mapping from model short name to fit result.
    """
    data = load_potential_data(data_path, r_column=r_column, energy_column=energy_column)
    results: dict[str, FitResult] = {}

    for model in models:
        model_name = model["name"]
        if model_name not in POTENTIALS:
            available = ", ".join(sorted(POTENTIALS))
            raise ValueError(
                f"Unknown potential name '{model_name}'. Available potentials: {available}"
            )

        result = fit_potential_scipy(
            data=data,
            potential_func=POTENTIALS[model_name],
            initial_guess=model["initial_guess"],
            parameter_names=model["parameter_names"],
            potential_name=model_name,
            bounds=model.get("bounds", (-np.inf, np.inf)),
        )
        results[model_name] = result

        label = model.get("label", model_name)

        if results_dir is not None:
            model_results_dir = Path(results_dir) / model_name
            save_fit_parameters(result, model_results_dir / "fit_parameters.csv")
            save_fit_metrics(result, model_results_dir / "fit_metrics.csv")
            save_fit_residuals(result, model_results_dir / "fit_residuals.csv")

        if figures_dir is not None:
            figure_path = Path(figures_dir)
            plot_fit_result(
                result,
                output_path=figure_path / f"{model_name}_fit.png",
                title=f"Fit for {label}",
            )
            plot_fit_residuals(
                result,
                output_path=figure_path / f"{model_name}_residuals.png",
                title=f"Residuals for {label}",
            )
            plot_fit_diagnostics(
                result,
                output_path=figure_path / f"{model_name}_diagnostics.png",
                title=f"Fit diagnostics for {label}",
            )

    if results_dir is not None:
        summary_path = Path(results_dir) / "fit_comparison_metrics.csv"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summarize_fit_results(results).to_csv(summary_path, index=False)

    return results

