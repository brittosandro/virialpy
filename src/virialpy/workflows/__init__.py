"""End-to-end scientific workflows.

Workflow modules will combine datasets, fitting, integration, virial
calculation, analysis, and plotting into reproducible pipelines.
"""

from virialpy.workflows.fit_potential import run_fit_workflow
from virialpy.workflows.compare_potentials import (
    run_potential_comparison_workflow,
    summarize_fit_results,
)

__all__ = [
    "run_fit_workflow",
    "run_potential_comparison_workflow",
    "summarize_fit_results",
]

