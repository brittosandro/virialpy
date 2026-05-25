import numpy as np
import pandas as pd
import yaml
from typer.testing import CliRunner

from virialpy.cli.main import app
from virialpy.potentials import lennard_jones


runner = CliRunner()


def test_cli_run_config_help_works() -> None:
    result = runner.invoke(app, ["run-config", "--help"])

    assert result.exit_code == 0


def test_cli_help_lists_run_config() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "run-config" in result.output


def test_cli_run_config_missing_file_returns_error(tmp_path) -> None:
    result = runner.invoke(app, ["run-config", str(tmp_path / "missing.yaml")])

    assert result.exit_code != 0


def test_cli_run_config_accepts_valid_minimal_yaml(tmp_path, monkeypatch) -> None:
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

    result = runner.invoke(app, ["run-config", str(config_path)])

    assert result.exit_code == 0, result.output
    assert (results_dir / "b2_experiment_metrics.csv").exists()
