from virialpy.datasets import load_potential_data
from virialpy.potentials import lennard_jones
from virialpy.potentials import improved_lennard_jones, rydberg6
from virialpy.fitting import fit_potential_scipy
from virialpy.io import save_fit_parameters, save_fit_metrics, save_fit_residuals

data = load_potential_data(
    "data/raw/ar2/ar2_cep_bsse.csv",
    r_column="r(angstrom)",
    energy_column="E_int_CP(kcal/mol)",
)

result = fit_potential_scipy(
    data=data,
    potential_func=lennard_jones,
    initial_guess=[0.25, 3.5],
    parameter_names=["epsilon", "sigma"],
    potential_name="Lennard-Jones",
)

save_fit_parameters(result, "data/results/ar2/fit_parameters_lj.csv")
save_fit_metrics(result, "data/results/ar2/fit_metrics_lj.csv")
save_fit_residuals(result, "data/results/ar2/fit_residuals_lj.csv")
