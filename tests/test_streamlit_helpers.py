from io import BytesIO

import pandas as pd
import yaml

from app.helpers import (
    b2_results_exist,
    build_fit_residuals_dataframe,
    build_fitted_curves_dataframe,
    build_yaml_config,
    dataframe_from_csv_if_exists,
    existing_fitted_potentials,
    existing_integrators_in_b2_results,
    fit_results_exist,
    list_files_safe,
    paths_for_system,
    read_file_bytes,
    safe_system_name,
    save_uploaded_file,
    save_yaml_config,
    summarize_output_availability,
    unique_downloads,
    validation_results_exist,
    workflow_step_status,
)


def test_safe_system_name_normalizes_spaces() -> None:
    assert safe_system_name("Kr 2") == "kr_2"


def test_build_yaml_config_contains_required_sections() -> None:
    config = build_yaml_config(
        system_name="Kr 2",
        potential_data_path="data/raw/kr2/potential.csv",
        experimental_data_path="data/raw/kr2/experimental.csv",
        r_column="r",
        energy_column="energy",
        temperature_column="temperature",
        b2_column="b2",
        potentials=["lj"],
        integrators=["scipy_quad"],
        distance_unit="angstrom",
        energy_unit="kcal/mol",
        r_min=2.5,
        r_max=30.0,
        enable_partitioned=True,
        r1=3.0,
        r2=4.0,
        r3=14.0,
        r4=30.0,
        n_points_b2=6,
        n_points_b3=10,
        n_points_b4=24,
        run_fit=True,
        run_b2=True,
        run_validate=True,
        run_partitioned=True,
        run_method_comparison=True,
        run_monte_carlo_plots=True,
        run_final_outputs=True,
    )

    for section in ["system", "data", "models", "integrators", "units", "b2", "outputs", "run"]:
        assert section in config
    assert config["system"] == "kr_2"


def test_paths_for_system_returns_standard_directories() -> None:
    paths = paths_for_system("Kr 2")

    assert paths["raw_dir"].as_posix() == "data/raw/kr_2"
    assert paths["results_dir"].as_posix() == "data/results/kr_2_streamlit"
    assert paths["figures_dir"].as_posix() == "outputs/figures/kr_2_streamlit"
    assert paths["reports_dir"].as_posix() == "outputs/reports/kr_2_streamlit"


def test_fit_results_exist_detects_parameter_files(tmp_path) -> None:
    (tmp_path / "lj").mkdir()
    (tmp_path / "lj" / "fit_parameters.csv").write_text("parameter,value\n", encoding="utf-8")

    assert fit_results_exist(tmp_path, ["lj"])


def test_b2_results_exist_detects_results_file(tmp_path) -> None:
    (tmp_path / "b2_comparison_all.csv").write_text("temperature,b2\n", encoding="utf-8")

    assert b2_results_exist(tmp_path)


def test_validation_results_exist_detects_metrics_file(tmp_path) -> None:
    (tmp_path / "b2_experiment_metrics.csv").write_text("rmse\n", encoding="utf-8")

    assert validation_results_exist(tmp_path)


def test_workflow_step_status_returns_expected_labels() -> None:
    assert workflow_step_status(completed=True, ready=True) == "Completed"
    assert workflow_step_status(completed=False, ready=True) == "Ready"
    assert workflow_step_status(completed=False, ready=False) == "Pending"


def test_dataframe_from_csv_if_exists_reads_existing_file(tmp_path) -> None:
    path = tmp_path / "table.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")

    frame = dataframe_from_csv_if_exists(path)

    assert frame is not None
    assert list(frame.columns) == ["a", "b"]


def test_dataframe_from_csv_if_exists_returns_none_for_missing_file(tmp_path) -> None:
    assert dataframe_from_csv_if_exists(tmp_path / "missing.csv") is None


def test_list_files_safe_returns_empty_list_for_missing_directory(tmp_path) -> None:
    assert list_files_safe(tmp_path / "missing") == []


def test_existing_fitted_potentials_detects_parameter_files(tmp_path) -> None:
    (tmp_path / "lj").mkdir()
    (tmp_path / "ilj").mkdir()
    (tmp_path / "lj" / "fit_parameters.csv").write_text("potential,parameter,value\n", encoding="utf-8")

    assert existing_fitted_potentials(tmp_path) == ["lj"]


def test_existing_integrators_in_b2_results_detects_integrators(tmp_path) -> None:
    (tmp_path / "b2_comparison_all.csv").write_text(
        "temperature,potential,integrator,b2\n100,lj,scipy_quad,-1\n100,lj,monte_carlo,-1.1\n",
        encoding="utf-8",
    )

    assert existing_integrators_in_b2_results(tmp_path) == ["monte_carlo", "scipy_quad"]


def test_build_fitted_curves_dataframe_returns_dataframe_with_parameters(tmp_path) -> None:
    (tmp_path / "lj").mkdir()
    (tmp_path / "lj" / "fit_parameters.csv").write_text(
        "potential,parameter,value\nlj,epsilon,1.0\nlj,sigma,3.0\n",
        encoding="utf-8",
    )
    potential_data = pd.DataFrame({"r": [3.0, 4.0, 5.0], "energy": [0.0, -0.5, -0.1]})

    curves = build_fitted_curves_dataframe(potential_data, tmp_path, ["lj"], n_points=10)

    assert not curves.empty
    assert set(curves.columns) == {"r", "energy_fit", "potential"}
    assert set(curves["potential"]) == {"lj"}


def test_build_fitted_curves_dataframe_ignores_missing_parameters(tmp_path) -> None:
    potential_data = pd.DataFrame({"r": [3.0, 4.0, 5.0], "energy": [0.0, -0.5, -0.1]})

    curves = build_fitted_curves_dataframe(potential_data, tmp_path, ["lj"], n_points=10)

    assert curves.empty


def test_build_fit_residuals_dataframe_combines_residual_files(tmp_path) -> None:
    (tmp_path / "lj").mkdir()
    (tmp_path / "ilj").mkdir()
    (tmp_path / "lj" / "fit_residuals.csv").write_text(
        "r,energy_observed,energy_fitted,residual\n3.0,-1.0,-0.9,-0.1\n",
        encoding="utf-8",
    )
    (tmp_path / "ilj" / "fit_residuals.csv").write_text(
        "r,energy_observed,energy_fitted,residual\n3.0,-1.0,-1.0,0.0\n",
        encoding="utf-8",
    )

    residuals = build_fit_residuals_dataframe(tmp_path, ["lj", "ilj"])

    assert residuals is not None
    assert set(residuals["potential"]) == {"lj", "ilj"}


def test_read_file_bytes_reads_existing_file(tmp_path) -> None:
    path = tmp_path / "file.txt"
    path.write_text("hello", encoding="utf-8")

    assert read_file_bytes(path) == b"hello"


def test_summarize_output_availability_detects_outputs(tmp_path) -> None:
    results_dir = tmp_path / "results"
    figures_dir = tmp_path / "figures"
    reports_dir = tmp_path / "reports"
    config_path = tmp_path / "config.yaml"
    (results_dir).mkdir()
    (figures_dir / "final").mkdir(parents=True)
    (reports_dir / "tables").mkdir(parents=True)
    (results_dir / "fit_comparison_metrics.csv").write_text("rmse\n", encoding="utf-8")
    (figures_dir / "final" / "final_b2_comparison.png").write_bytes(b"png")
    (reports_dir / "tables" / "fit_summary.csv").write_text("rmse\n", encoding="utf-8")
    config_path.write_text("system: test\n", encoding="utf-8")

    summary = summarize_output_availability(results_dir, figures_dir, reports_dir, config_path)

    assert summary["Fit results"]
    assert summary["Final figures"]
    assert summary["Final tables"]
    assert summary["YAML configuration"]


def test_unique_downloads_removes_duplicate_paths_preserving_order(tmp_path) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    downloads = [
        (first, "First", "text/csv"),
        (second, "Second", "text/csv"),
        (first, "First again", "text/csv"),
    ]

    unique = unique_downloads(downloads)

    assert [path for path, _, _ in unique] == [first, second]
    assert [label for _, label, _ in unique] == ["First", "Second"]


def test_save_yaml_config_creates_valid_yaml(tmp_path) -> None:
    config = {"system": "test", "outputs": {"results_dir": "results"}}
    path = save_yaml_config(config, tmp_path / "config.yaml")

    assert path.exists()
    assert yaml.safe_load(path.read_text(encoding="utf-8")) == config


def test_save_uploaded_file_creates_file(tmp_path) -> None:
    uploaded = BytesIO(b"a,b\n1,2\n")
    uploaded.name = "my file.csv"

    path = save_uploaded_file(uploaded, tmp_path)

    assert path.exists()
    assert path.name == "my_file.csv"
    assert path.read_bytes() == b"a,b\n1,2\n"
