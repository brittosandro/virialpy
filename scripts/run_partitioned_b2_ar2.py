"""Calculate partitioned B(T) for Ar2 fitted potentials."""

from __future__ import annotations

import pandas as pd

from virialpy.integrators import GaussianQuadratureIntegrator
from virialpy.workflows import (
    load_parameters_from_csv,
    load_temperatures_from_csv,
    run_partitioned_b2_workflow,
)


def main() -> None:
    """Run the partitioned Ar2 B(T) workflow example."""
    models = [
        ("lj", "data/results/ar2/lj/fit_parameters.csv"),
        ("ilj", "data/results/ar2/ilj/fit_parameters.csv"),
        ("ryd6", "data/results/ar2/ryd6/fit_parameters.csv"),
    ]
    temperatures = load_temperatures_from_csv(
        "data/raw/ar2/b2_experimental.csv",
        temperature_column="Temperatura",
    )

    r1 = 3.052
    r2 = 3.7578
    r3 = 13.0391
    r4 = 30.0

    results = []
    for potential_name, parameter_path in models:
        parameters = load_parameters_from_csv(parameter_path)
        result = run_partitioned_b2_workflow(
            potential_name=potential_name,
            parameters=parameters,
            temperatures=temperatures,
            integrator_b2=GaussianQuadratureIntegrator(n_points=6),
            integrator_b3=GaussianQuadratureIntegrator(n_points=10),
            integrator_b4=GaussianQuadratureIntegrator(n_points=24),
            r1=r1,
            r2=r2,
            r3=r3,
            r4=r4,
            distance_unit="angstrom",
            energy_unit="kcal/mol",
            output_path=f"data/results/ar2/partitioned_b2_{potential_name}.csv",
        )
        results.append(result)

    comparison = pd.concat(results, ignore_index=True)
    comparison.to_csv("data/results/ar2/partitioned_b2_comparison.csv", index=False)

    print(comparison.head())


if __name__ == "__main__":
    main()

