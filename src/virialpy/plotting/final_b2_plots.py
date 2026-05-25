"""Final publication-ready B(T) figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from virialpy.plotting.style import set_publication_style


def _ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory for a figure path when needed."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Raise a clear error when required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


def _label(value: str) -> str:
    """Return readable labels for known potentials, integrators, and methods."""
    labels = {
        "lj": "LJ",
        "ilj": "ILJ",
        "ryd6": "Rydberg 6",
        "scipy_quad": "SciPy quad",
        "gaussian": "Gauss-Legendre",
        "simpson": "Simpson",
        "trapezoid": "Trapézio",
        "direct": "direto",
        "partitioned": "particionado",
    }
    return labels.get(value, value)


def _metric_model_labels(data: pd.DataFrame) -> list[str]:
    """Build labels from potential, integrator, and/or method columns."""
    label_columns = [column for column in ["potential", "integrator", "method"] if column in data.columns]
    if not label_columns:
        return [str(index) for index in data.index]

    labels = []
    for row in data.itertuples():
        parts = [_label(str(getattr(row, column))) for column in label_columns]
        labels.append(" | ".join(parts))
    return labels


def _finish_axes(ax) -> None:
    """Apply consistent grid and tick styling."""
    ax.minorticks_on()
    ax.grid(True, which="major")
    ax.grid(True, which="minor", alpha=0.25, linewidth=0.4)


def plot_final_b2_comparison(
    comparison_df: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    integrator: str = "scipy_quad",
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B_2(T)$ / cm$^3$ mol$^{-1}$",
    dpi: int = 400,
) -> Figure:
    """Plot final calculated-vs-experimental B(T) comparison."""
    set_publication_style()
    data = comparison_df.copy()
    if "integrator" in data.columns:
        data = data.loc[data["integrator"] == integrator].copy()
    _require_columns(data, ["temperature", "b2_exp", "b2_calc", "potential"])

    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    exp_data = data.loc[:, ["temperature", "b2_exp"]].drop_duplicates().sort_values("temperature")
    ax.scatter(
        exp_data["temperature"],
        exp_data["b2_exp"],
        label="Experimental",
        alpha=0.9,
        s=38,
        edgecolors="black",
        linewidths=0.45,
        zorder=3,
    )
    for potential, group in data.groupby("potential", dropna=False):
        ordered = group.sort_values("temperature")
        ax.plot(ordered["temperature"], ordered["b2_calc"], label=_label(str(potential)), zorder=2)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    _finish_axes(ax)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)
    return fig


def plot_final_b2_residuals(
    comparison_df: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    integrator: str = "scipy_quad",
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B_{2,\mathrm{calc}} - B_{2,\mathrm{exp}}$ / cm$^3$ mol$^{-1}$",
    dpi: int = 400,
) -> Figure:
    """Plot final B(T) residuals by potential."""
    set_publication_style()
    data = comparison_df.copy()
    if "integrator" in data.columns:
        data = data.loc[data["integrator"] == integrator].copy()
    _require_columns(data, ["temperature", "residual", "potential"])

    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    for potential, group in data.groupby("potential", dropna=False):
        ordered = group.sort_values("temperature")
        ax.scatter(
            ordered["temperature"],
            ordered["residual"],
            label=_label(str(potential)),
            alpha=0.9,
            s=34,
            edgecolors="black",
            linewidths=0.45,
            zorder=3,
        )

    ax.axhline(0.0, color="0.25", linewidth=1.1, zorder=2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    _finish_axes(ax)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)
    return fig


def plot_final_metric_ranking(
    metrics_df: pd.DataFrame,
    metric: str = "rmse",
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str = "Modelo",
    dpi: int = 400,
) -> Figure:
    """Plot a final horizontal ranking of a B(T) error metric."""
    set_publication_style()
    _require_columns(metrics_df, [metric])
    data = metrics_df.sort_values(metric, ascending=True).copy()
    labels = _metric_model_labels(data)
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


def plot_final_method_comparison(
    method_comparison_df: pd.DataFrame,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$T$ / K",
    ylabel: str = r"$B_2(T)$ / cm$^3$ mol$^{-1}$",
    dpi: int = 400,
) -> Figure:
    """Plot final direct-vs-partitioned method comparison."""
    set_publication_style()
    _require_columns(method_comparison_df, ["temperature", "b2_exp", "b2_calc", "potential", "method"])

    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    exp_data = method_comparison_df.loc[:, ["temperature", "b2_exp"]].drop_duplicates().sort_values(
        "temperature"
    )
    ax.scatter(
        exp_data["temperature"],
        exp_data["b2_exp"],
        label="Experimental",
        alpha=0.9,
        s=38,
        edgecolors="black",
        linewidths=0.45,
        zorder=3,
    )
    for (potential, method), group in method_comparison_df.groupby(["potential", "method"], dropna=False):
        ordered = group.sort_values("temperature")
        ax.plot(
            ordered["temperature"],
            ordered["b2_calc"],
            label=f"{_label(str(potential))} | {_label(str(method))}",
            zorder=2,
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    _finish_axes(ax)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)
    return fig

