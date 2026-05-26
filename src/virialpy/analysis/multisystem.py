"""Utilities for comparing virialpy outputs across molecular systems."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def _read_metrics(path: Path, system: str, required_columns: list[str]) -> pd.DataFrame:
    """Read a metrics CSV and attach the system label."""
    if not path.exists():
        raise FileNotFoundError(f"Required metrics file not found: {path}")
    data = pd.read_csv(path)
    missing = [column for column in required_columns if column not in data.columns]
    if missing:
        raise ValueError(f"{path} is missing required column(s): {', '.join(missing)}")
    data = data.copy()
    data.insert(0, "system", system)
    return data


def load_multisystem_metrics(systems: list[dict[str, Any]]) -> dict[str, pd.DataFrame]:
    """Load fit, direct B(T), and method-comparison metrics for many systems."""
    fit_frames = []
    b2_frames = []
    method_frames = []

    for system_config in systems:
        system = str(system_config["system"])
        results_dir = Path(system_config["results_dir"])
        fit_frames.append(
            _read_metrics(
                results_dir / "fit_comparison_metrics.csv",
                system,
                ["model", "potential", "rmse", "mae", "r2"],
            )
        )
        b2_frames.append(
            _read_metrics(
                results_dir / "b2_experiment_metrics.csv",
                system,
                ["potential", "integrator", "mae", "rmse", "r2"],
            )
        )
        method_frames.append(
            _read_metrics(
                results_dir / "b2_method_experiment_metrics.csv",
                system,
                ["potential", "method", "mae", "rmse", "r2"],
            )
        )

    return {
        "fit_metrics": pd.concat(fit_frames, ignore_index=True),
        "b2_metrics": pd.concat(b2_frames, ignore_index=True),
        "method_metrics": pd.concat(method_frames, ignore_index=True),
    }


def best_fit_potential_by_system(fit_metrics: pd.DataFrame) -> pd.DataFrame:
    """Return the best fitted potential for each system by fit RMSE."""
    return (
        fit_metrics.sort_values(["system", "rmse"], ascending=[True, True])
        .groupby("system", as_index=False)
        .first()
        .loc[:, ["system", "model", "potential", "rmse", "mae", "r2"]]
    )


def best_b2_model_by_system(b2_metrics: pd.DataFrame) -> pd.DataFrame:
    """Return the best potential-integrator combination for each system."""
    return (
        b2_metrics.sort_values(["system", "rmse"], ascending=[True, True])
        .groupby("system", as_index=False)
        .first()
        .loc[:, ["system", "potential", "integrator", "mae", "rmse", "r2"]]
    )


def best_integrator_by_system(b2_metrics: pd.DataFrame) -> pd.DataFrame:
    """Rank integrators per system by mean B(T) RMSE over potentials."""
    summary = (
        b2_metrics.groupby(["system", "integrator"], as_index=False)
        .agg(mean_rmse=("rmse", "mean"), mean_mae=("mae", "mean"), mean_r2=("r2", "mean"))
        .sort_values(["system", "mean_rmse"], ascending=[True, True])
    )
    return summary.groupby("system", as_index=False).first()


def compare_direct_partitioned_by_system(method_metrics: pd.DataFrame) -> pd.DataFrame:
    """Compare direct and partitioned methods per system using mean metrics."""
    return (
        method_metrics.groupby(["system", "method"], as_index=False)
        .agg(mean_rmse=("rmse", "mean"), mean_mae=("mae", "mean"), mean_r2=("r2", "mean"))
        .sort_values(["system", "mean_rmse"], ascending=[True, True])
    )


def best_method_by_system(method_metrics: pd.DataFrame) -> pd.DataFrame:
    """Return the best direct/partitioned method per system by mean RMSE."""
    comparison = compare_direct_partitioned_by_system(method_metrics)
    return comparison.groupby("system", as_index=False).first()


def best_described_system(b2_metrics: pd.DataFrame) -> pd.DataFrame:
    """Rank systems by their best available B(T) RMSE."""
    best = best_b2_model_by_system(b2_metrics)
    return best.sort_values("rmse", ascending=True).reset_index(drop=True)


def build_multisystem_summary_tables(systems: list[dict[str, Any]]) -> dict[str, pd.DataFrame]:
    """Build all standard multi-system summary tables."""
    metrics = load_multisystem_metrics(systems)
    return {
        **metrics,
        "best_fit_potential": best_fit_potential_by_system(metrics["fit_metrics"]),
        "best_b2_model": best_b2_model_by_system(metrics["b2_metrics"]),
        "best_integrator": best_integrator_by_system(metrics["b2_metrics"]),
        "direct_vs_partitioned": compare_direct_partitioned_by_system(
            metrics["method_metrics"]
        ),
        "best_method": best_method_by_system(metrics["method_metrics"]),
        "system_ranking": best_described_system(metrics["b2_metrics"]),
    }
