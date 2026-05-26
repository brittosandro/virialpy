"""Plots for comparing final metrics across molecular systems."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from virialpy.plotting.style import set_publication_style


def _ensure_parent_directory(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def _label(value: str) -> str:
    labels = {
        "lj": "LJ",
        "ilj": "ILJ",
        "ryd6": "Rydberg 6",
        "scipy_quad": "SciPy quad",
        "gaussian": "Gauss-Legendre",
        "simpson": "Simpson",
        "trapezoid": "Trapézio",
        "monte_carlo": "Monte Carlo",
        "direct": "direto",
        "partitioned": "particionado",
    }
    return labels.get(value, value)


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


def _barh(
    data: pd.DataFrame,
    label_column: str,
    metric: str,
    output_path: str | Path | None,
    title: str | None,
    xlabel: str,
    ylabel: str,
    dpi: int,
) -> Figure:
    set_publication_style()
    _require_columns(data, [label_column, metric])
    ordered = data.sort_values(metric, ascending=True).copy()
    height = max(3.8, 0.42 * len(ordered) + 1.4)
    fig, ax = plt.subplots(figsize=(7.6, height))
    bars = ax.barh(ordered[label_column], ordered[metric])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    if (ordered[metric] >= 0).all():
        ax.set_xlim(left=0.0)
    ax.invert_yaxis()
    ax.grid(True, axis="x", which="major")
    ax.grid(True, axis="x", which="minor", alpha=0.25, linewidth=0.4)
    ax.grid(False, axis="y")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    max_value = float(ordered[metric].max()) if len(ordered) else 0.0
    offset = 0.01 * max_value if max_value > 0 else 0.01
    for bar, value in zip(bars, ordered[metric], strict=True):
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2.0,
            f"{value:.4g}",
            va="center",
            fontsize=9,
        )
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)
    return fig


def plot_best_b2_model_by_system(
    best_b2_model: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    metric: str = "rmse",
    dpi: int = 400,
) -> Figure:
    """Plot the best potential-integrator combination for each system."""
    data = best_b2_model.copy()
    _require_columns(data, ["system", "potential", "integrator", metric])
    data["label"] = (
        data["system"].astype(str)
        + " | "
        + data["potential"].astype(str).map(_label)
        + " | "
        + data["integrator"].astype(str).map(_label)
    )
    return _barh(
        data,
        label_column="label",
        metric=metric,
        output_path=output_path,
        title=title,
        xlabel=r"RMSE / cm$^3$ mol$^{-1}$",
        ylabel="Sistema | modelo",
        dpi=dpi,
    )


def plot_best_integrator_by_system(
    best_integrator: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    dpi: int = 400,
) -> Figure:
    """Plot the best mean integrator for each system."""
    data = best_integrator.copy()
    _require_columns(data, ["system", "integrator", "mean_rmse"])
    data["label"] = data["system"].astype(str) + " | " + data["integrator"].astype(str).map(_label)
    return _barh(
        data,
        label_column="label",
        metric="mean_rmse",
        output_path=output_path,
        title=title,
        xlabel=r"RMSE médio / cm$^3$ mol$^{-1}$",
        ylabel="Sistema | integrador",
        dpi=dpi,
    )


def plot_direct_partitioned_comparison(
    direct_vs_partitioned: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    dpi: int = 400,
) -> Figure:
    """Plot direct-vs-partitioned mean RMSE for all systems."""
    set_publication_style()
    _require_columns(direct_vs_partitioned, ["system", "method", "mean_rmse"])
    data = direct_vs_partitioned.copy()
    data["method_label"] = data["method"].astype(str).map(_label)

    systems = list(data["system"].drop_duplicates())
    methods = list(data["method_label"].drop_duplicates())
    x = range(len(systems))
    width = 0.8 / max(len(methods), 1)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for index, method in enumerate(methods):
        values = []
        subset = data.loc[data["method_label"] == method]
        for system in systems:
            match = subset.loc[subset["system"] == system, "mean_rmse"]
            values.append(float(match.iloc[0]) if not match.empty else float("nan"))
        positions = [value + index * width - 0.4 + width / 2 for value in x]
        ax.bar(positions, values, width=width, label=method)

    ax.set_xticks(list(x))
    ax.set_xticklabels(systems)
    ax.set_ylabel(r"RMSE médio / cm$^3$ mol$^{-1}$")
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    ax.grid(True, axis="y", which="major")
    ax.grid(True, axis="y", which="minor", alpha=0.25, linewidth=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)
    return fig


def plot_system_ranking(
    system_ranking: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    dpi: int = 400,
) -> Figure:
    """Plot which system was best described by the best available B(T) model."""
    return plot_best_b2_model_by_system(
        system_ranking,
        output_path=output_path,
        title=title,
        metric="rmse",
        dpi=dpi,
    )
