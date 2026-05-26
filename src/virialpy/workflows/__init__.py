"""End-to-end scientific workflows.

Workflow modules will combine datasets, fitting, integration, virial
calculation, analysis, and plotting into reproducible pipelines.
"""

from virialpy.workflows.fit_potential import run_fit_workflow
from virialpy.workflows.compare_potentials import (
    run_potential_comparison_workflow,
    summarize_fit_results,
)
from virialpy.workflows.calculate_b2 import (
    load_parameters_from_csv,
    load_temperatures_from_csv,
    run_b2_workflow,
)
from virialpy.workflows.compare_b2 import (
    load_model_parameters_from_results,
    run_b2_comparison_workflow,
)
from virialpy.workflows.compare_b2_methods import prepare_b2_method_comparison
from virialpy.workflows.partitioned_b2 import run_partitioned_b2_workflow
from virialpy.workflows.multisystem import (
    run_multisystem_analysis,
    run_multisystem_comparison_workflow,
)
from virialpy.workflows.run_from_config import run_from_config
from virialpy.workflows.validate_b2 import validate_b2_against_experiment

__all__ = [
    "load_model_parameters_from_results",
    "load_parameters_from_csv",
    "load_temperatures_from_csv",
    "prepare_b2_method_comparison",
    "run_b2_comparison_workflow",
    "run_b2_workflow",
    "run_fit_workflow",
    "run_potential_comparison_workflow",
    "run_partitioned_b2_workflow",
    "run_multisystem_comparison_workflow",
    "run_multisystem_analysis",
    "run_from_config",
    "summarize_fit_results",
    "validate_b2_against_experiment",
]
