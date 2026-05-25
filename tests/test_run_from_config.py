import numpy as np
import pandas as pd
import yaml

from virialpy.potentials import lennard_jones
from virialpy.workflows import run_from_config


def test_run_from_config_generates_expected_outputs(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mplconfig"))
    potential_path = tmp_path / "potential.csv"
    experimental_path = tmp_path / "experimental.csv"
    results_dir = tmp_path / "results"
    figures_dir = tmp_path / "figures"
    reports_dir = tmp_path / "reports"
    config_path = tmp_path / "config.yaml"

    r_values = np.linspace(3.0, 6.0, 12)
    energies = lennard_jones(r_values, epsilon=0.25, sigma=3.5)
    pd.DataFrame({"r": r_values, "energy": energies}).to_csv(potential_path, index=False)
    pd.DataFrame({"temperature": [150.0, 200.0], "b2": [-80.0, -45.0]}).to_csv(
        experimental_path,
        index=False,
    )

    config = {
        "system": "synthetic",
        "data": {
            "potential_data": str(potential_path),
            "experimental_data": str(experimental_path),
            "r_column": "r",
            "energy_column": "energy",
            "temperature_column": "temperature",
            "b2_column": "b2",
        },
        "models": {"potentials": ["lj"]},
        "integrators": {"names": ["scipy_quad"]},
        "units": {"distance_unit": "angstrom", "energy_unit": "kcal/mol"},
        "b2": {"r_min": 2.5, "r_max": 8.0},
        "outputs": {
            "results_dir": str(results_dir),
            "figures_dir": str(figures_dir),
            "reports_dir": str(reports_dir),
        },
        "run": {"fit": True, "b2": True, "validate": True, "monte_carlo_plots": False},
    }
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    outputs = run_from_config(config_path)

    assert isinstance(outputs, dict)
    assert results_dir.exists()
    assert figures_dir.exists()
    assert reports_dir.exists()
    assert (results_dir / "fit_comparison_metrics.csv").exists()
    assert (results_dir / "b2_comparison_all.csv").exists()
    assert (results_dir / "b2_experiment_metrics.csv").exists()


def test_run_from_config_generates_optional_partitioned_method_and_final_outputs(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mplconfig"))
    potential_path = tmp_path / "potential.csv"
    experimental_path = tmp_path / "experimental.csv"
    results_dir = tmp_path / "results"
    figures_dir = tmp_path / "figures"
    reports_dir = tmp_path / "reports"
    config_path = tmp_path / "config.yaml"

    r_values = np.linspace(3.0, 6.0, 12)
    energies = lennard_jones(r_values, epsilon=0.25, sigma=3.5)
    pd.DataFrame({"r": r_values, "energy": energies}).to_csv(potential_path, index=False)
    pd.DataFrame({"temperature": [150.0, 200.0], "b2": [-80.0, -45.0]}).to_csv(
        experimental_path,
        index=False,
    )

    config = {
        "system": "synthetic",
        "data": {
            "potential_data": str(potential_path),
            "experimental_data": str(experimental_path),
            "r_column": "r",
            "energy_column": "energy",
            "temperature_column": "temperature",
            "b2_column": "b2",
        },
        "models": {"potentials": ["lj"]},
        "integrators": {"names": ["scipy_quad"]},
        "units": {"distance_unit": "angstrom", "energy_unit": "kcal/mol"},
        "b2": {"r_min": 2.5, "r_max": 8.0},
        "partitioned": {
            "enabled": True,
            "r1": 2.5,
            "r2": 3.2,
            "r3": 5.5,
            "r4": 8.0,
            "integrator_b2": {"name": "gaussian", "n_points": 6},
            "integrator_b3": {"name": "gaussian", "n_points": 8},
            "integrator_b4": {"name": "gaussian", "n_points": 10},
        },
        "outputs": {
            "results_dir": str(results_dir),
            "figures_dir": str(figures_dir),
            "reports_dir": str(reports_dir),
        },
        "run": {
            "fit": True,
            "b2": True,
            "validate": True,
            "partitioned": True,
            "method_comparison": True,
            "monte_carlo_plots": False,
            "final_outputs": True,
        },
    }
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    outputs = run_from_config(config_path)

    assert (results_dir / "partitioned_b2_comparison.csv").exists()
    assert (results_dir / "b2_method_experiment_metrics.csv").exists()
    assert (reports_dir / "tables").exists()
    assert "partitioned_comparison" in outputs
    assert "method_comparison" in outputs
    assert "final_tables_dir" in outputs
    assert "final_figures_dir" in outputs
