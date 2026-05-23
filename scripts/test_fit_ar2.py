from virialpy.datasets import load_potential_data
from virialpy.potentials import lennard_jones, improved_lennard_jones, rydberg6
from virialpy.fitting import fit_potential_scipy


data = load_potential_data(
    "data/raw/ar2/ar2_cep_bsse.csv",
    r_column="r(angstrom)",
    energy_column="E_int_CP(kcal/mol)",
)

models = [
    (
        "Lennard-Jones",
        lennard_jones,
        [0.25, 3.5],
        ["epsilon", "sigma"],
    ),
    (
        "Improved Lennard-Jones",
        improved_lennard_jones,
        [0.3, 3.8, 8.0],
        ["de", "req", "beta"],
    ),
    (
        "Rydberg6",
        rydberg6,
        [0.3, 3.8, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ["de", "re", "c1", "c2", "c3", "c4", "c5", "c6"],
    ),
]

for name, func, initial_guess, parameter_names in models:
    result = fit_potential_scipy(
        data=data,
        potential_func=func,
        initial_guess=initial_guess,
        parameter_names=parameter_names,
        potential_name=name,
    )

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)
    print("Success:", result.success)
    print("Message:", result.message)
    print("Parameters:", result.parameter_values)
    print("RMSE:", result.rmse)
    print("MAE:", result.mae)
    print("R2:", result.r2)
