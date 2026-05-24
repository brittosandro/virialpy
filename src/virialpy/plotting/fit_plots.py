"""Plots for fitted intermolecular potentials."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from virialpy.fitting import FitResult
from virialpy.plotting.style import set_plot_style


def _ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory for a figure path when needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def _require_fit_arrays(result: FitResult, require_fitted: bool = True) -> tuple[NDArray[np.float64], ...]:
    """Return required arrays or raise a clear error when they are absent."""
    if result.r_values is None:
        raise ValueError("FitResult must contain r_values for plotting.")
    if result.residuals is None:
        raise ValueError("FitResult must contain residuals for plotting.")

    arrays: list[NDArray[np.float64]] = [
        np.asarray(result.r_values, dtype=float),
        np.asarray(result.residuals, dtype=float),
    ]

    if require_fitted:
        if result.observed_values is None:
            raise ValueError("FitResult must contain observed_values for plotting.")
        if result.fitted_values is None:
            raise ValueError("FitResult must contain fitted_values for plotting.")
        arrays.extend(
            [
                np.asarray(result.observed_values, dtype=float),
                np.asarray(result.fitted_values, dtype=float),
            ]
        )

    return tuple(arrays)


def _metrics_text(result: FitResult) -> str:
    """Format core fit metrics for annotation."""
    return f"RMSE = {result.rmse:.6g}\nMAE = {result.mae:.6g}\nR$^2$ = {result.r2:.6g}"


def plot_fit_result(
    result: FitResult,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = "r",
    ylabel: str = "Energy",
    observed_label: str = "Observed",
    fitted_label: str = "Fitted",
    show_metrics: bool = True,
    dpi: int = 300,
) -> Figure:
    """Plot observed potential-energy data and the fitted model curve.

    Parameters
    ----------
    result:
        Fit result containing ``r_values``, ``observed_values``,
        ``fitted_values``, residuals, and metrics.
    output_path:
        Optional path where the figure is saved.
    title:
        Optional figure title.
    xlabel, ylabel:
        Axis labels.
    observed_label, fitted_label:
        Labels used in the legend.
    show_metrics:
        If ``True``, annotate the axes with RMSE, MAE, and R^2.
    dpi:
        Resolution used when saving the figure.

    Returns
    -------
    matplotlib.figure.Figure
        Created figure. The function does not call ``plt.show()``.
    """
    set_plot_style()
    r_values, _, observed_values, fitted_values = _require_fit_arrays(result)
    order = np.argsort(r_values)

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.scatter(
        r_values,
        observed_values,
        label=observed_label,
        alpha=0.82,
        s=34,
        edgecolors="black",
        linewidths=0.45,
        zorder=3,
    )
    ax.plot(r_values[order], fitted_values[order], label=fitted_label, zorder=2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title, pad=10)
    ax.legend()
    ax.minorticks_on()
    ax.grid(True, which="major")
    ax.grid(True, which="minor", alpha=0.25, linewidth=0.4)

    if show_metrics:
        ax.text(
            0.04,
            0.96,
            _metrics_text(result),
            transform=ax.transAxes,
            va="top",
            fontsize=10,
            bbox={
                "boxstyle": "round,pad=0.35",
                "facecolor": "white",
                "edgecolor": "0.75",
                "alpha": 0.92,
            },
        )

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig


def plot_fit_residuals(
    result: FitResult,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = "r",
    ylabel: str = "Residual",
    dpi: int = 300,
) -> Figure:
    """Plot fit residuals as a function of distance."""
    set_plot_style()
    r_values, residuals = _require_fit_arrays(result, require_fitted=False)

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.scatter(
        r_values,
        residuals,
        alpha=0.82,
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
    ax.minorticks_on()
    ax.grid(True, which="major")
    ax.grid(True, which="minor", alpha=0.25, linewidth=0.4)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig


def plot_fit_diagnostics(
    result: FitResult,
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = "r",
    ylabel: str = "Energy",
    dpi: int = 300,
) -> Figure:
    """Plot observed/fitted energies and residuals in stacked panels."""
    set_plot_style()
    r_values, residuals, observed_values, fitted_values = _require_fit_arrays(result)
    order = np.argsort(r_values)

    fig, (ax_fit, ax_residuals) = plt.subplots(
        nrows=2,
        ncols=1,
        sharex=True,
        figsize=(6.4, 5.4),
        gridspec_kw={"height_ratios": [3, 1]},
    )

    ax_fit.scatter(
        r_values,
        observed_values,
        label="Observed",
        alpha=0.82,
        s=34,
        edgecolors="black",
        linewidths=0.45,
        zorder=3,
    )
    ax_fit.plot(r_values[order], fitted_values[order], label="Fitted", zorder=2)
    ax_fit.set_ylabel(ylabel)
    ax_fit.legend()
    ax_fit.minorticks_on()
    ax_fit.grid(True, which="major")
    ax_fit.grid(True, which="minor", alpha=0.25, linewidth=0.4)

    ax_residuals.scatter(
        r_values,
        residuals,
        alpha=0.82,
        s=30,
        edgecolors="black",
        linewidths=0.45,
        zorder=3,
    )
    ax_residuals.axhline(0.0, linestyle="-", linewidth=1.1, color="0.25", zorder=2)
    ax_residuals.set_xlabel(xlabel)
    ax_residuals.set_ylabel(r"$E_{\mathrm{obs}} - E_{\mathrm{fit}}$")
    ax_residuals.minorticks_on()
    ax_residuals.grid(True, which="major")
    ax_residuals.grid(True, which="minor", alpha=0.25, linewidth=0.4)

    if title is not None:
        fig.suptitle(title, y=0.98, fontsize=14)

    fig.tight_layout(h_pad=1.0)

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig
