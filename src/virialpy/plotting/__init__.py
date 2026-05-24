"""Plotting and visualization helpers.

Figures for potentials, fitted curves, virial coefficients, residuals, and
publication-ready outputs should be organized here.
"""

from virialpy.plotting.fit_plots import (
    plot_fit_diagnostics,
    plot_fit_residuals,
    plot_fit_result,
)
from virialpy.plotting.comparison_plots import (
    plot_comparison_diagnostics,
    plot_multiple_fits,
    plot_multiple_residuals,
)
from virialpy.plotting.style import set_plot_style

__all__ = [
    "plot_comparison_diagnostics",
    "plot_fit_diagnostics",
    "plot_fit_residuals",
    "plot_fit_result",
    "plot_multiple_fits",
    "plot_multiple_residuals",
    "set_plot_style",
]
