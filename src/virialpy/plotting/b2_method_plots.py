"""Plots comparing direct and partitioned B(T) calculation methods."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from virialpy.plotting.style import set_plot_style


def _ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory for a figure path when needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Raise a clear error when required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


def _potential_label(value: str) -> str:
    """Return a compact display label for a potential."""
    labels = {
        "lj": "LJ",
        "ilj": "ILJ",
        "ryd6": "Ryd6",
        "Lennard-Jones": "LJ",
        "Improved Lennard-Jones": "ILJ",
        "Rydberg 6": "Ryd6",
    }
    return labels.get(value, value)


def _method_label(value: str) -> str:
    """Return a Portuguese display label for a calculation method."""
    labels = {
        "direct": "direto",
        "partitioned": "particionado",
    }
    return labels.get(value, value)


def _combined_label(potential: str, method: str) -> str:
    """Build a readable label for potential-method combinations."""
    return f"{_potential_label(str(potential))} | {_method_label(str(method))}"


def plot_b2_methods_vs_experiment(
    comparison_df: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B(T)$ / cm$^3$ mol$^{-1}$",
    dpi: int = 300,
) -> Figure:
    """Plot experimental B(T) and curves from direct and partitioned methods."""
    set_plot_style()
    _require_columns(comparison_df, ["temperature", "b2_exp", "b2_calc", "potential", "method"])

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    exp_data = comparison_df.loc[:, ["temperature", "b2_exp"]].drop_duplicates().sort_values(
        "temperature"
    )
    ax.scatter(
        exp_data["temperature"],
        exp_data["b2_exp"],
        label="Experimental",
        alpha=0.85,
        s=36,
        edgecolors="black",
        linewidths=0.45,
        zorder=3,
    )

    for (potential, method), group in comparison_df.groupby(["potential", "method"], dropna=False):
        ordered = group.sort_values("temperature")
        ax.plot(
            ordered["temperature"],
            ordered["b2_calc"],
            label=_combined_label(potential, method),
            zorder=2,
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    ax.minorticks_on()
    ax.grid(True, which="major")
    ax.grid(True, which="minor", alpha=0.25, linewidth=0.4)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig


def plot_b2_method_residuals(
    comparison_df: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B_{\mathrm{calc}} - B_{\mathrm{exp}}$ / cm$^3$ mol$^{-1}$",
    dpi: int = 300,
) -> Figure:
    """Plot residuals for direct and partitioned B(T) methods."""
    set_plot_style()
    _require_columns(comparison_df, ["temperature", "residual", "potential", "method"])

    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    for (potential, method), group in comparison_df.groupby(["potential", "method"], dropna=False):
        ordered = group.sort_values("temperature")
        ax.scatter(
            ordered["temperature"],
            ordered["residual"],
            label=_combined_label(potential, method),
            alpha=0.85,
            s=34,
            edgecolors="black",
            linewidths=0.45,
            zorder=3,
        )

    ax.axhline(0.0, linestyle="-", linewidth=1.1, color="0.25", zorder=2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    ax.minorticks_on()
    ax.grid(True, which="major")
    ax.grid(True, which="minor", alpha=0.25, linewidth=0.4)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig


def plot_b2_method_metrics(
    metrics_df: pd.DataFrame,
    metric: str = "rmse",
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str = "Modelo",
    dpi: int = 300,
) -> Figure:
    """Plot method-comparison metrics as horizontal bars."""
    set_plot_style()
    _require_columns(metrics_df, ["potential", "method", metric])

    data = metrics_df.sort_values(metric, ascending=True).copy()
    labels = [_combined_label(row.potential, row.method) for row in data.itertuples()]
    height = max(3.8, 0.42 * len(data) + 1.4)

    fig, ax = plt.subplots(figsize=(7.4, height))
    bars = ax.barh(labels, data[metric])
    ax.set_xlabel(xlabel if xlabel is not None else metric.upper())
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    if (data[metric] >= 0).all():
        ax.set_xlim(left=0.0)
    ax.invert_yaxis()
    ax.grid(True, axis="x", which="major")
    ax.grid(True, axis="x", which="minor", alpha=0.25, linewidth=0.4)
    ax.grid(False, axis="y")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    max_value = float(data[metric].max()) if len(data) else 0.0
    offset = 0.01 * max_value if max_value > 0 else 0.01
    for bar, value in zip(bars, data[metric], strict=True):
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2.0,
            f"{value:.4g}",
            va="center",
            ha="left",
            fontsize=9,
        )

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig


def plot_partitioned_contributions(
    partitioned_df: pd.DataFrame,
    potential: str,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$T$ / K",
    ylabel: str = r"Contribuição para $B(T)$ / cm$^3$ mol$^{-1}$",
    dpi: int = 300,
) -> Figure:
    """Plot B1, B2, B3, B4, and total contributions for one potential."""
    set_plot_style()
    _require_columns(partitioned_df, ["temperature", "potential", "b1", "b2", "b3", "b4", "b_total"])
    data = partitioned_df.loc[partitioned_df["potential"] == potential].sort_values("temperature")

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    labels = {
        "b1": "B1",
        "b2": "B2",
        "b3": "B3",
        "b4": "B4",
        "b_total": "Total",
    }
    for column, label in labels.items():
        ax.plot(data["temperature"], data[column], label=label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    ax.minorticks_on()
    ax.grid(True, which="major")
    ax.grid(True, which="minor", alpha=0.25, linewidth=0.4)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig
