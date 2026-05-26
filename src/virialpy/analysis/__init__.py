"""Analysis and comparison utilities.

This package will compare calculated virial coefficients with experimental
datasets, compute residuals, metrics, and reusable diagnostic summaries.
"""

from virialpy.analysis.b2_metrics import calculate_b2_metrics, calculate_grouped_b2_metrics
from virialpy.analysis.monte_carlo_comparison import (
    compare_monte_carlo_with_integrators,
    summarize_monte_carlo_comparison,
)
from virialpy.analysis.multisystem import (
    best_b2_model_by_system,
    best_described_system,
    best_fit_potential_by_system,
    best_integrator_by_system,
    best_method_by_system,
    build_multisystem_summary_tables,
    compare_direct_partitioned_by_system,
    load_multisystem_metrics,
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
    "best_b2_model_by_system",
    "best_described_system",
    "best_fit_potential_by_system",
    "best_integrator_by_system",
    "best_method_by_system",
    "build_multisystem_summary_tables",
    "compare_monte_carlo_with_integrators",
    "compare_direct_partitioned_by_system",
    "create_b2_metrics_table",
    "create_fit_summary_table",
    "load_multisystem_metrics",
    "save_table_csv",
    "save_table_latex",
    "summarize_monte_carlo_comparison",
]
