"""Plots for B2 validation against experimental data."""

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


def _filter_integrator(data: pd.DataFrame, integrator: str | None) -> pd.DataFrame:
    """Filter a comparison table by integrator when requested."""
    if integrator is None:
        return data
    if "integrator" not in data.columns:
        raise ValueError("comparison_df must contain an 'integrator' column.")
    return data.loc[data["integrator"] == integrator].copy()


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Raise a clear error when required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


def _display_short_name(value: str) -> str:
    """Return a compact publication-friendly label for known short names."""
    labels = {
        "lj": "LJ",
        "ilj": "ILJ",
        "ryd6": "Ryd6",
        "Lennard-Jones": "LJ",
        "Improved Lennard-Jones": "ILJ",
        "Rydberg 6": "Ryd6",
        "scipy_quad": "SciPy quad",
        "gaussian": "Gauss-Legendre",
        "simpson": "Simpson",
        "trapezoid": "Trapezoid",
    }
    return labels.get(value, value)


def _metric_labels(data: pd.DataFrame) -> pd.Series:
    """Build readable model labels for a metrics table."""
    potential_source = "potential_label" if "potential_label" in data.columns else "potential"
    integrator_source = "integrator_label" if "integrator_label" in data.columns else "integrator"

    if potential_source in data.columns and integrator_source in data.columns:
        return data[potential_source].astype(str).map(_display_short_name) + " | " + data[
            integrator_source
        ].astype(str).map(_display_short_name)
    if potential_source in data.columns:
        return data[potential_source].astype(str).map(_display_short_name)
    return pd.Series(data.index.astype(str), index=data.index)


def plot_b2_comparison(
    comparison_df: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B(T)$ / cm$^3$ mol$^{-1}$",
    group_column: str = "potential",
    integrator: str | None = None,
    dpi: int = 300,
) -> Figure:
    """Plot experimental and calculated B2 curves."""
    set_plot_style()
    data = _filter_integrator(comparison_df, integrator)
    _require_columns(data, ["temperature", "b2_exp", "b2_calc", group_column])

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    exp_data = data.loc[:, ["temperature", "b2_exp"]].drop_duplicates().sort_values("temperature")
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

    for group_name, group in data.groupby(group_column, dropna=False):
        ordered = group.sort_values("temperature")
        ax.plot(
            ordered["temperature"],
            ordered["b2_calc"],
            label=_display_short_name(str(group_name)),
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


def plot_b2_residuals(
    comparison_df: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B_{\mathrm{calc}} - B_{\mathrm{exp}}$ / cm$^3$ mol$^{-1}$",
    group_column: str = "potential",
    integrator: str | None = None,
    dpi: int = 300,
) -> Figure:
    """Plot B2 residuals against temperature."""
    set_plot_style()
    data = _filter_integrator(comparison_df, integrator)
    _require_columns(data, ["temperature", "residual", group_column])

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for group_name, group in data.groupby(group_column, dropna=False):
        ordered = group.sort_values("temperature")
        ax.scatter(
            ordered["temperature"],
            ordered["residual"],
            label=_display_short_name(str(group_name)),
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


def plot_b2_metrics(
    metrics_df: pd.DataFrame,
    metric: str = "rmse",
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = "Metric value",
    ylabel: str | None = "Model",
    dpi: int = 300,
) -> Figure:
    """Plot grouped B2 validation metrics as a horizontal bar chart."""
    set_plot_style()
    _require_columns(metrics_df, [metric])

    data = metrics_df.sort_values(metric, ascending=True).copy()
    labels = _metric_labels(data)
    height = max(3.8, 0.42 * len(data) + 1.4)

    fig, ax = plt.subplots(figsize=(7.4, height))
    bars = ax.barh(labels, data[metric])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel if ylabel is not None else "")
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
