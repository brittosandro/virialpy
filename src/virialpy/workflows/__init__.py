"""End-to-end scientific workflows.

Workflow modules will combine datasets, fitting, integration, virial
calculation, analysis, and plotting into reproducible pipelines.
"""

from virialpy.workflows.fit_potential import run_fit_workflow

__all__ = ["run_fit_workflow"]

