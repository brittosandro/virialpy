"""Analysis and comparison utilities.

This package will compare calculated virial coefficients with experimental
datasets, compute residuals, metrics, and reusable diagnostic summaries.
"""

from virialpy.analysis.b2_metrics import calculate_b2_metrics, calculate_grouped_b2_metrics
from virialpy.analysis.monte_carlo_comparison import (
    compare_monte_carlo_with_integrators,
    summarize_monte_carlo_comparison,
)
from virialpy.analysis.tables import (
    create_b2_metrics_table,
    create_fit_summary_table,
    save_table_csv,
    save_table_latex,
)

__all__ = [
    "calculate_b2_metrics",
    "calculate_grouped_b2_metrics",
    "compare_monte_carlo_with_integrators",
    "create_b2_metrics_table",
    "create_fit_summary_table",
    "save_table_csv",
    "save_table_latex",
    "summarize_monte_carlo_comparison",
]
