"""Plotting and visualization helpers.

Figures for potentials, fitted curves, virial coefficients, residuals, and
publication-ready outputs should be organized here.
"""

from virialpy.plotting.fit_plots import (
    plot_fit_diagnostics,
    plot_fit_residuals,
    plot_fit_result,
)
from virialpy.plotting.style import set_plot_style

__all__ = [
    "plot_fit_diagnostics",
    "plot_fit_residuals",
    "plot_fit_result",
    "set_plot_style",
]
