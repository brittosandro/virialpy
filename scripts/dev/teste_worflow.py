from virialpy.workflows import run_fit_workflow

result = run_fit_workflow(
    data_path="data/raw/ar2/ar2_cep_bsse.csv",
    potential_name="lj",
    initial_guess=[0.25, 3.5],
    parameter_names=["epsilon", "sigma"],
    r_column="r(angstrom)",
    energy_column="E_int_CP(kcal/mol)",
    output_dir="data/results/ar2/lj",
)

print(result.success)
print(result.parameter_values)
print(result.rmse)
print(result.mae)
print(result.r2)
