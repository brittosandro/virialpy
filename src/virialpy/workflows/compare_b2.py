"""Workflow for comparing B(T) across potentials and integrators."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from virialpy.potentials import POTENTIALS
from virialpy.virial import second_virial_coefficient
from virialpy.workflows.calculate_b2 import load_parameters_from_csv


def load_model_parameters_from_results(
    results_base_dir: str | Path,
    models: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Load fitted parameters for multiple models from result subdirectories.

    Parameters
    ----------
    results_base_dir:
        Base directory containing one subdirectory per model.
    models:
        Model descriptors with ``name`` and ``label`` entries.

    Returns
    -------
    list[dict[str, Any]]
        Model descriptors enriched with a ``parameters`` dictionary.
    """
    base_dir = Path(results_base_dir)
    loaded_models = []

    for model in models:
        model_name = model["name"]
        parameter_path = base_dir / model_name / "fit_parameters.csv"
        if not parameter_path.exists():
            raise FileNotFoundError(f"Parameter file not found: {parameter_path}")

        loaded_models.append(
            {
                "name": model_name,
                "label": model["label"],
                "parameters": load_parameters_from_csv(parameter_path),
            }
        )

    return loaded_models


def run_b2_comparison_workflow(
    models: list[dict[str, Any]],
    temperatures: Iterable[float] | np.ndarray | pd.Series,
    integrators: list[dict[str, Any]],
    r_min: float,
    r_max: float,
    distance_unit: str = "angstrom",
    energy_unit: str = "kcal/mol",
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Calculate B(T) for all model, integrator, and temperature combinations.

    Parameters
    ----------
    models:
        Potential model descriptors with ``name``, ``parameters``, and
        ``label`` entries.
    temperatures:
        Iterable of absolute temperatures in Kelvin.
    integrators:
        Integrator descriptors with ``name``, ``integrator``, and ``label``
        entries.
    r_min, r_max:
        Integration bounds.
    distance_unit:
        Distance unit for the integration coordinate.
    energy_unit:
        Energy unit returned by all potential functions.
    output_path:
        Optional CSV output path.

    Returns
    -------
    pandas.DataFrame
        Long-form comparison table.
    """
    temperature_values = pd.to_numeric(pd.Series(temperatures), errors="raise").astype(float)
    rows = []

    for model in models:
        potential_name = model["name"]
        if potential_name not in POTENTIALS:
            available = ", ".join(sorted(POTENTIALS))
            raise ValueError(
                f"Unknown potential_name '{potential_name}'. Available potentials: {available}"
            )

        potential_func = POTENTIALS[potential_name]

        for integrator_config in integrators:
            for temperature in temperature_values:
                b2_value, integration_error = second_virial_coefficient(
                    temperature=float(temperature),
                    potential_func=potential_func,
                    parameters=model["parameters"],
                    integrator=integrator_config["integrator"],
                    r_min=r_min,
                    r_max=r_max,
                    distance_unit=distance_unit,
                    energy_unit=energy_unit,
                )
                rows.append(
                    {
                        "temperature": float(temperature),
                        "potential": potential_name,
                        "potential_label": model["label"],
                        "integrator": integrator_config["name"],
                        "integrator_label": integrator_config["label"],
                        "b2": b2_value,
                        "integration_error": integration_error,
                        "distance_unit": distance_unit,
                        "energy_unit": energy_unit,
                        "r_min": r_min,
                        "r_max": r_max,
                    }
                )

    result = pd.DataFrame(
        rows,
        columns=[
            "temperature",
            "potential",
            "potential_label",
            "integrator",
            "integrator_label",
            "b2",
            "integration_error",
            "distance_unit",
            "energy_unit",
            "r_min",
            "r_max",
        ],
    )

    if output_path is not None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output, index=False)

    return result

