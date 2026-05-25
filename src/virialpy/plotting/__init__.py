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
from virialpy.plotting.b2_plots import (
    plot_b2_comparison,
    plot_b2_metrics,
    plot_b2_residuals,
)
from virialpy.plotting.b2_method_plots import (
    plot_b2_method_metrics,
    plot_b2_method_residuals,
    plot_b2_methods_vs_experiment,
    plot_partitioned_contributions,
)
from virialpy.plotting.final_b2_plots import (
    plot_final_b2_comparison,
    plot_final_b2_residuals,
    plot_final_method_comparison,
    plot_final_metric_ranking,
)
from virialpy.plotting.style import set_plot_style, set_publication_style

__all__ = [
    "plot_b2_comparison",
    "plot_b2_method_metrics",
    "plot_b2_method_residuals",
    "plot_b2_methods_vs_experiment",
    "plot_b2_metrics",
    "plot_b2_residuals",
    "plot_comparison_diagnostics",
    "plot_fit_diagnostics",
    "plot_fit_residuals",
    "plot_fit_result",
    "plot_final_b2_comparison",
    "plot_final_b2_residuals",
    "plot_final_method_comparison",
    "plot_final_metric_ranking",
    "plot_multiple_fits",
    "plot_multiple_residuals",
    "plot_partitioned_contributions",
    "set_plot_style",
    "set_publication_style",
]
