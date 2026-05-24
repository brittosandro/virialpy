"""Comparison plots for multiple fitted intermolecular potentials."""

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


def _require_results(results: dict[str, FitResult]) -> None:
    """Raise a clear error if no fit results are available."""
    if not results:
        raise ValueError("At least one FitResult is required for comparison plotting.")


def _require_fit_arrays(model_name: str, result: FitResult) -> tuple[NDArray[np.float64], ...]:
    """Return required arrays for one model or raise a clear error."""
    if result.r_values is None:
        raise ValueError(f"FitResult for model '{model_name}' must contain r_values.")
    if result.observed_values is None:
        raise ValueError(f"FitResult for model '{model_name}' must contain observed_values.")
    if result.fitted_values is None:
        raise ValueError(f"FitResult for model '{model_name}' must contain fitted_values.")
    if result.residuals is None:
        raise ValueError(f"FitResult for model '{model_name}' must contain residuals.")

    return (
        np.asarray(result.r_values, dtype=float),
        np.asarray(result.observed_values, dtype=float),
        np.asarray(result.fitted_values, dtype=float),
        np.asarray(result.residuals, dtype=float),
    )


def _curve_label(model_name: str, result: FitResult, show_metrics: bool = False) -> str:
    """Build the legend label for a fitted model."""
    label = _display_model_name(result.potential_name or model_name)
    if show_metrics:
        label = f"{label} (RMSE={result.rmse:.4g}, MAE={result.mae:.4g}, R$^2$={result.r2:.4g})"
    return label


def _display_model_name(model_name: str) -> str:
    """Return a publication-friendly label for known model short names."""
    labels = {
        "lj": "LJ",
        "ilj": "ILJ",
        "ryd6": "Ryd6",
    }
    return labels.get(model_name, model_name)


def plot_multiple_fits(
    results: dict[str, FitResult],
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$r$ / $\AA$",
    ylabel: str = r"$E_{\mathrm_{int}}^{\mathrm{CP}} (kcal mol$^{-1})$",
    observed_label: str = "Observed",
    show_metrics: bool = False,
    dpi: int = 300,
) -> Figure:
    """Plot observed data and multiple fitted potential curves.

    Parameters
    ----------
    results:
        Mapping from model short names to ``FitResult`` objects.
    output_path:
        Optional path where the figure is saved.
    title:
        Optional figure title.
    xlabel, ylabel:
        Axis labels using Matplotlib mathtext by default.
    observed_label:
        Label for the observed data points, plotted once.
    show_metrics:
        If ``True``, append RMSE, MAE, and R^2 to each fitted-curve label.
    dpi:
        Resolution used when saving the figure.

    Returns
    -------
    matplotlib.figure.Figure
        Created figure. The function does not call ``plt.show()``.
    """
    set_plot_style()
    _require_results(results)

    first_model_name, first_result = next(iter(results.items()))
    r_observed, observed_values, _, _ = _require_fit_arrays(first_model_name, first_result)

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.scatter(
        r_observed,
        observed_values,
        label=observed_label,
        alpha=0.82,
        s=34,
        edgecolors="black",
        linewidths=0.45,
        zorder=3,
    )

    for model_name, result in results.items():
        r_values, _, fitted_values, _ = _require_fit_arrays(model_name, result)
        order = np.argsort(r_values)
        ax.plot(
            r_values[order],
            fitted_values[order],
            label=_curve_label(model_name, result, show_metrics=show_metrics),
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


def plot_multiple_residuals(
    results: dict[str, FitResult],
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$r$ / $\AA$",
    ylabel: str = r"$E_{\mathrm{obs}} - E_{\mathrm{fit}} (kcal mol$^{-1})$",
    dpi: int = 300,
) -> Figure:
    """Plot residuals for multiple fitted potential models."""
    set_plot_style()
    _require_results(results)

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for model_name, result in results.items():
        r_values, _, _, residuals = _require_fit_arrays(model_name, result)
        ax.scatter(
            r_values,
            residuals,
            label=_display_model_name(result.potential_name or model_name),
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
    ax.legend()
    ax.minorticks_on()
    ax.grid(True, which="major")
    ax.grid(True, which="minor", alpha=0.25, linewidth=0.4)
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig


def plot_comparison_diagnostics(
    results: dict[str, FitResult],
    output_path: str | Path | None = None,
    title: str | None = None,
    xlabel: str = r"$r$ / $\AA$",
    ylabel: str = r"$E_{\mathrm{int}}^{\mathrm{CP}} (kcal mol$^{-1})$",
    residual_ylabel: str = r"$E_{\mathrm{obs}} - E_{\mathrm{fit}} (kcal mol$^{-1})$",
    dpi: int = 300,
) -> Figure:
    """Plot observed/fitted curves and residuals for multiple models."""
    set_plot_style()
    _require_results(results)

    first_model_name, first_result = next(iter(results.items()))
    r_observed, observed_values, _, _ = _require_fit_arrays(first_model_name, first_result)

    fig, (ax_fit, ax_residuals) = plt.subplots(
        nrows=2,
        ncols=1,
        sharex=True,
        figsize=(6.6, 5.6),
        gridspec_kw={"height_ratios": [3, 1]},
    )

    ax_fit.scatter(
        r_observed,
        observed_values,
        label="Observed",
        alpha=0.82,
        s=34,
        edgecolors="black",
        linewidths=0.45,
        zorder=3,
    )

    for model_name, result in results.items():
        r_values, _, fitted_values, residuals = _require_fit_arrays(model_name, result)
        order = np.argsort(r_values)
        label = _display_model_name(result.potential_name or model_name)
        ax_fit.plot(r_values[order], fitted_values[order], label=label, zorder=2)
        ax_residuals.scatter(
            r_values,
            residuals,
            label=label,
            alpha=0.82,
            s=30,
            edgecolors="black",
            linewidths=0.45,
            zorder=3,
        )

    ax_fit.set_ylabel(ylabel)
    ax_fit.legend()
    ax_fit.minorticks_on()
    ax_fit.grid(True, which="major")
    ax_fit.grid(True, which="minor", alpha=0.25, linewidth=0.4)

    ax_residuals.axhline(0.0, linestyle="-", linewidth=1.1, color="0.25", zorder=2)
    ax_residuals.set_xlabel(xlabel)
    ax_residuals.set_ylabel(residual_ylabel)
    ax_residuals.legend()
    ax_residuals.minorticks_on()
    ax_residuals.grid(True, which="major")
    ax_residuals.grid(True, which="minor", alpha=0.25, linewidth=0.4)

    if title is not None:
        fig.suptitle(title, y=0.98, fontsize=14)

    fig.tight_layout(h_pad=1.0)

    if output_path is not None:
        fig.savefig(_ensure_parent_directory(output_path), dpi=dpi)

    return fig
