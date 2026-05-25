"""Plots for comparing Monte Carlo and deterministic integrators."""

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


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


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
    }
    return labels.get(value, value)


def _finish(ax) -> None:
    ax.minorticks_on()
    ax.grid(True, which="major")
    ax.grid(True, which="minor", alpha=0.25, linewidth=0.4)


def plot_monte_carlo_vs_reference(
    comparison_df: pd.DataFrame,
    reference_integrator: str,
    potential: str | None = None,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B_2(T)$ / cm$^3$ mol$^{-1}$",
    dpi: int = 400,
) -> Figure:
    """Plot Monte Carlo and reference B(T) curves."""
    set_publication_style()
    _require_columns(comparison_df, ["temperature", "potential", "reference_integrator", "b2_monte_carlo", "b2_reference"])
    data = comparison_df.loc[comparison_df["reference_integrator"] == reference_integrator].copy()
    if potential is not None:
        data = data.loc[data["potential"] == potential].copy()

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    for potential_name, group in data.groupby("potential", dropna=False):
        ordered = group.sort_values("temperature")
        base = _label(str(potential_name))
        ax.plot(ordered["temperature"], ordered["b2_monte_carlo"], label=f"{base} | Monte Carlo")
        ax.plot(ordered["temperature"], ordered["b2_reference"], label=f"{base} | {_label(reference_integrator)}")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    _finish(ax)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)
    return fig


def plot_monte_carlo_difference(
    comparison_df: pd.DataFrame,
    reference_integrator: str,
    potential: str | None = None,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B_{2,\mathrm{MC}} - B_{2,\mathrm{ref}}$ / cm$^3$ mol$^{-1}$",
    dpi: int = 400,
) -> Figure:
    """Plot Monte Carlo minus reference differences."""
    set_publication_style()
    _require_columns(comparison_df, ["temperature", "potential", "reference_integrator", "difference"])
    data = comparison_df.loc[comparison_df["reference_integrator"] == reference_integrator].copy()
    if potential is not None:
        data = data.loc[data["potential"] == potential].copy()

    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    for potential_name, group in data.groupby("potential", dropna=False):
        ordered = group.sort_values("temperature")
        ax.plot(ordered["temperature"], ordered["difference"], label=_label(str(potential_name)))
    ax.axhline(0.0, color="0.25", linewidth=1.1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    _finish(ax)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)
    return fig


def plot_monte_carlo_summary_metrics(
    summary_df: pd.DataFrame,
    metric: str = "mean_abs_difference",
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str = "Modelo",
    dpi: int = 400,
) -> Figure:
    """Plot Monte Carlo comparison summary metrics."""
    set_publication_style()
    _require_columns(summary_df, ["potential", "reference_integrator", metric])
    data = summary_df.sort_values(metric, ascending=True).copy()
    labels = [_label(row.potential) + " | " + _label(row.reference_integrator) for row in data.itertuples()]
    height = max(3.8, 0.42 * len(data) + 1.4)

    fig, ax = plt.subplots(figsize=(7.6, height))
    bars = ax.barh(labels, data[metric])
    ax.set_xlabel(xlabel if xlabel is not None else metric)
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
        ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2, f"{value:.4g}", va="center", fontsize=9)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)
    return fig

