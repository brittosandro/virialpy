"""Compare B(T) for Ar2 across potentials and numerical integrators."""

from __future__ import annotations

from virialpy.integrators import (
    GaussianQuadratureIntegrator,
    ScipyQuadIntegrator,
    SimpsonIntegrator,
    TrapezoidIntegrator,
)
from virialpy.workflows import (
    load_model_parameters_from_results,
    load_temperatures_from_csv,
    run_b2_comparison_workflow,
)


def main() -> None:
    """Run the Ar2 B(T) comparison workflow example."""
    models = load_model_parameters_from_results(
        "data/results/ar2",
        [
            {"name": "lj", "label": "Lennard-Jones"},
            {"name": "ilj", "label": "Improved Lennard-Jones"},
            {"name": "ryd6", "label": "Rydberg 6"},
        ],
    )
    temperatures = load_temperatures_from_csv(
        "data/raw/ar2/b2_experimental.csv",
        temperature_column="Temperatura",
    )
    integrators = [
        {
            "name": "scipy_quad",
            "label": "SciPy quad",
            "integrator": ScipyQuadIntegrator(),
        },
        {
            "name": "gaussian",
            "label": "Gauss-Legendre",
            "integrator": GaussianQuadratureIntegrator(n_points=128),
        },
        {
            "name": "simpson",
            "label": "Simpson",
            "integrator": SimpsonIntegrator(n_points=20001),
        },
        {
            "name": "trapezoid",
            "label": "Trapezoid",
            "integrator": TrapezoidIntegrator(n_points=20000),
        },
    ]

    result = run_b2_comparison_workflow(
        models=models,
        temperatures=temperatures,
        integrators=integrators,
        r_min=2.5,
        r_max=30.0,
        distance_unit="angstrom",
        energy_unit="kcal/mol",
        output_path="data/results/ar2/b2_comparison_all.csv",
    )

    print(result)


if __name__ == "__main__":
    main()
