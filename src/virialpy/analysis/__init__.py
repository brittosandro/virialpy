"""Analysis and comparison utilities.

This package will compare calculated virial coefficients with experimental
datasets, compute residuals, metrics, and reusable diagnostic summaries.
"""

from virialpy.analysis.b2_metrics import calculate_b2_metrics, calculate_grouped_b2_metrics
from virialpy.analysis.tables import (
    create_b2_metrics_table,
    create_fit_summary_table,
    save_table_csv,
    save_table_latex,
)

__all__ = [
    "calculate_b2_metrics",
    "calculate_grouped_b2_metrics",
    "create_b2_metrics_table",
    "create_fit_summary_table",
    "save_table_csv",
    "save_table_latex",
]
