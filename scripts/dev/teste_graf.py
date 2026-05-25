from virialpy.workflows import run_fit_workflow
from virialpy.plotting import plot_fit_result, plot_fit_residuals, plot_fit_diagnostics

result = run_fit_workflow(
    data_path="data/raw/ar2/ar2_cep_bsse.csv",
    potential_name="lj",
    initial_guess=[0.25, 3.5],
    parameter_names=["epsilon", "sigma"],
    r_column="r(angstrom)",
    energy_column="E_int_CP(kcal/mol)",
    output_dir="data/results/ar2/lj",
)

plot_fit_result(
    result,
    output_path="outputs/figures/ar2/fit/lj_fit.png",
    title="Lennard-Jones fit for Ar2",
    xlabel="r (Å)",
    ylabel="E_int_CP (kcal/mol)",
)

plot_fit_residuals(
    result,
    output_path="outputs/figures/ar2/fit/lj_residuals.png",
    title="Lennard-Jones residuals for Ar2",
    xlabel="r (Å)",
    ylabel="Residual (kcal/mol)",
)

plot_fit_diagnostics(
    result,
    output_path="outputs/figures/ar2/fit/lj_diagnostics.png",
    title="Lennard-Jones fit diagnostics for Ar2",
    xlabel="r (Å)",
    ylabel="E_int_CP (kcal/mol)",
)
