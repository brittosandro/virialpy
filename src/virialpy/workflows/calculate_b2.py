"""High-level workflow for second virial coefficient calculations."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from virialpy.potentials import POTENTIALS
from virialpy.virial import second_virial_coefficient


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Raise a clear error when required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


def load_parameters_from_csv(path: str | Path) -> dict[str, float]:
    """Load fitted potential parameters from a CSV created by virialpy.

    The input CSV must contain the columns ``potential``, ``parameter``, and
    ``value``. The returned dictionary maps parameter names to float values.
    """
    data = pd.read_csv(path)
    _require_columns(data, ["potential", "parameter", "value"])

    parameters = {}
    for _, row in data.iterrows():
        parameters[str(row["parameter"])] = float(row["value"])
    return parameters


def load_temperatures_from_csv(
    path: str | Path,
    temperature_column: str = "temperature",
) -> list[float]:
    """Load positive temperatures from a CSV file.

    Missing values are removed after numeric conversion. A clear error is
    raised when the requested column is absent or any remaining temperature is
    non-positive.
    """
    data = pd.read_csv(path)
    _require_columns(data, [temperature_column])

    temperatures = pd.to_numeric(data[temperature_column], errors="coerce").dropna()
    if (temperatures <= 0).any():
        raise ValueError("temperatures must be positive.")
    return temperatures.astype(float).tolist()


def run_b2_workflow(
    potential_name: str,
    parameters: dict[str, float],
    temperatures: Iterable[float] | np.ndarray | pd.Series,
    integrator,
    r_min: float,
    r_max: float,
    distance_unit: str = "angstrom",
    energy_unit: str = "kelvin",
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Calculate ``B(T)`` for a registered potential over many temperatures.

    Parameters
    ----------
    potential_name:
        Registry key for the potential. Built-in keys include ``"lj"``,
        ``"ilj"``, and ``"ryd6"``.
    parameters:
        Potential parameter dictionary.
    temperatures:
        Iterable of absolute temperatures in Kelvin.
    integrator:
        Numerical integrator with an ``integrate`` method.
    r_min, r_max:
        Integration bounds.
    distance_unit:
        Distance unit for the integration coordinate.
    energy_unit:
        Energy unit returned by the potential. Supported values are
        ``"kelvin"``, ``"kcal/mol"``, ``"kj/mol"``, ``"ev"``, and ``"mev"``.
    output_path:
        Optional CSV output path.

    Returns
    -------
    pandas.DataFrame
        Table with temperature, calculated ``B(T)``, integration error, model
        metadata, and integration bounds.
    """
    if potential_name not in POTENTIALS:
        available = ", ".join(sorted(POTENTIALS))
        raise ValueError(
            f"Unknown potential_name '{potential_name}'. Available potentials: {available}"
        )

    potential_func = POTENTIALS[potential_name]
    temperature_values = pd.to_numeric(pd.Series(temperatures), errors="raise").astype(float)

    rows = []
    for temperature in temperature_values:
        b2_value, integration_error = second_virial_coefficient(
            temperature=float(temperature),
            potential_func=potential_func,
            parameters=parameters,
            integrator=integrator,
            r_min=r_min,
            r_max=r_max,
            distance_unit=distance_unit,
            energy_unit=energy_unit,
        )
        rows.append(
            {
                "temperature": float(temperature),
                "b2": b2_value,
                "integration_error": integration_error,
                "potential": potential_name,
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
            "b2",
            "integration_error",
            "potential",
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
