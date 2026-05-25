"""Workflow for partitioned second virial coefficient calculations."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from virialpy.potentials import POTENTIALS
from virialpy.virial import partitioned_second_virial_coefficient


def run_partitioned_b2_workflow(
    potential_name: str,
    parameters: dict[str, float],
    temperatures: Iterable[float] | np.ndarray | pd.Series,
    integrator_b2,
    integrator_b3,
    integrator_b4,
    r1: float,
    r2: float,
    r3: float,
    r4: float,
    distance_unit: str = "angstrom",
    energy_unit: str = "kcal/mol",
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Calculate partitioned B(T) values for a registered potential."""
    if potential_name not in POTENTIALS:
        available = ", ".join(sorted(POTENTIALS))
        raise ValueError(
            f"Unknown potential_name '{potential_name}'. Available potentials: {available}"
        )

    temperature_values = pd.to_numeric(pd.Series(temperatures), errors="raise").astype(float)
    potential_func = POTENTIALS[potential_name]
    rows = []

    for temperature in temperature_values:
        result = partitioned_second_virial_coefficient(
            temperature=float(temperature),
            potential_func=potential_func,
            parameters=parameters,
            integrator_b2=integrator_b2,
            integrator_b3=integrator_b3,
            integrator_b4=integrator_b4,
            r1=r1,
            r2=r2,
            r3=r3,
            r4=r4,
            distance_unit=distance_unit,
            energy_unit=energy_unit,
        )
        result["potential"] = potential_name
        rows.append(result)

    columns = [
        "temperature",
        "b1",
        "b2",
        "b3",
        "b4",
        "b_total",
        "error_b2",
        "error_b3",
        "error_b4",
        "potential",
        "distance_unit",
        "energy_unit",
        "r1",
        "r2",
        "r3",
        "r4",
    ]
    data = pd.DataFrame(rows, columns=columns)

    if output_path is not None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output, index=False)

    return data

