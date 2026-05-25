"""Analysis and comparison utilities.

This package will compare calculated virial coefficients with experimental
datasets, compute residuals, metrics, and reusable diagnostic summaries.
"""

from virialpy.analysis.b2_metrics import calculate_b2_metrics, calculate_grouped_b2_metrics

__all__ = [
    "calculate_b2_metrics",
    "calculate_grouped_b2_metrics",
]

