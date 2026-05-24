"""Calculate second virial coefficients for Ar2 using fitted LJ parameters."""

from __future__ import annotations

from virialpy.integrators import ScipyQuadIntegrator
from virialpy.workflows import load_parameters_from_csv, run_b2_workflow


def main() -> None:
    """Run the Ar2 LJ B(T) workflow example."""
    parameters = load_parameters_from_csv("data/results/ar2/lj/fit_parameters.csv")
    temperatures = [100, 150, 200, 250, 300, 350, 400]
    integrator = ScipyQuadIntegrator()

    result = run_b2_workflow(
        potential_name="lj",
        parameters=parameters,
        temperatures=temperatures,
        integrator=integrator,
        r_min=2.5,
        r_max=30.0,
        distance_unit="angstrom",
        energy_unit="kcal/mol",
        output_path="data/results/ar2/lj/b2_calculated.csv",
    )

    print(result)


if __name__ == "__main__":
    main()
