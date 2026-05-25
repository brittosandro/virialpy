import numpy as np
import pandas as pd
from typer.testing import CliRunner

from virialpy.cli.main import app, create_integrators, _generate_general_monte_carlo_outputs
from virialpy.integrators import MonteCarloIntegrator
from virialpy.potentials import lennard_jones


runner = CliRunner()


def test_cli_run_help_works() -> None:
    result = runner.invoke(app, ["run", "--help"])

    assert result.exit_code == 0


def test_cli_run_fit_help_works() -> None:
    result = runner.invoke(app, ["run", "fit", "--help"])

    assert result.exit_code == 0


def test_cli_run_b2_help_works() -> None:
    result = runner.invoke(app, ["run", "b2", "--help"])

    assert result.exit_code == 0


def test_cli_run_validate_help_works() -> None:
    result = runner.invoke(app, ["run", "validate", "--help"])

    assert result.exit_code == 0


def test_cli_run_full_help_works() -> None:
    result = runner.invoke(app, ["run", "full", "--help"])

    assert result.exit_code == 0


def test_cli_run_fit_help_shows_potentials() -> None:
    result = runner.invoke(app, ["run", "fit", "--help"])

    assert result.exit_code == 0
    assert "--potentials" in result.output


def test_cli_run_b2_help_shows_integrators() -> None:
    result = runner.invoke(app, ["run", "b2", "--help"])

    assert result.exit_code == 0
    assert "--integrators" in result.output
    assert "monte_carlo" in result.output


def test_cli_run_full_help_shows_units() -> None:
    result = runner.invoke(app, ["run", "full", "--help"])

    assert result.exit_code == 0
    assert "--energy-unit" in result.output
    assert "--distance-unit" in result.output


def test_create_integrators_all_includes_monte_carlo() -> None:
    integrators = create_integrators(["all"])

    names = [item["name"] for item in integrators]
    assert names == ["scipy_quad", "gaussian", "simpson", "trapezoid", "monte_carlo"]
    monte_carlo = next(item for item in integrators if item["name"] == "monte_carlo")
    assert monte_carlo["label"] == "Monte Carlo"
    assert isinstance(monte_carlo["integrator"], MonteCarloIntegrator)


def test_create_integrators_monte_carlo_only() -> None:
    integrators = create_integrators(["monte_carlo"])

    assert len(integrators) == 1
    assert integrators[0]["name"] == "monte_carlo"
    assert integrators[0]["label"] == "Monte Carlo"
    assert isinstance(integrators[0]["integrator"], MonteCarloIntegrator)


def test_cli_run_full_with_all_integrators_writes_monte_carlo(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mplconfig"))
    potential_path = tmp_path / "potential.csv"
    experimental_path = tmp_path / "experimental.csv"
    results_dir = tmp_path / "results"
    figures_dir = tmp_path / "figures"
    reports_dir = tmp_path / "reports"

    r_values = np.linspace(3.0, 6.0, 12)
    energies = lennard_jones(r_values, epsilon=0.25, sigma=3.5)
    pd.DataFrame({"r": r_values, "energy": energies}).to_csv(potential_path, index=False)
    pd.DataFrame({"temperature": [150.0, 200.0], "b2": [-80.0, -45.0]}).to_csv(
        experimental_path,
        index=False,
    )

    result = runner.invoke(
        app,
        [
            "run",
            "full",
            "--system",
            "synthetic",
            "--potential-data",
            str(potential_path),
            "--experimental-data",
            str(experimental_path),
            "--potentials",
            "lj",
            "--integrators",
            "all",
            "--energy-unit",
            "kcal/mol",
            "--distance-unit",
            "angstrom",
            "--r-min",
            "2.5",
            "--r-max",
            "8.0",
            "--results-dir",
            str(results_dir),
            "--figures-dir",
            str(figures_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    b2_results = pd.read_csv(results_dir / "b2_comparison_all.csv")
    assert "monte_carlo" in set(b2_results["integrator"])


def test_generate_general_monte_carlo_outputs_creates_tables_and_figures(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mplconfig"))
    results_dir = tmp_path / "results"
    figures_dir = tmp_path / "figures"
    results_dir.mkdir()

    rows = []
    offsets = {
        "scipy_quad": 0.0,
        "gaussian": 0.1,
        "simpson": 0.2,
        "trapezoid": 0.3,
        "monte_carlo": 0.5,
    }
    for potential in ["lj", "ilj"]:
        base = -100.0 if potential == "lj" else -90.0
        for temperature in [100.0, 200.0]:
            for integrator, offset in offsets.items():
                rows.append(
                    {
                        "temperature": temperature,
                        "potential": potential,
                        "integrator": integrator,
                        "b2": base + 0.1 * temperature + offset,
                    }
                )
    pd.DataFrame(rows).to_csv(results_dir / "b2_comparison_all.csv", index=False)

    _generate_general_monte_carlo_outputs(
        system="synthetic",
        results_dir=results_dir,
        figures_dir=figures_dir,
    )

    assert (results_dir / "monte_carlo_comparison.csv").exists()
    assert (results_dir / "monte_carlo_comparison_summary.csv").exists()
    expected_figures = [
        "mc_vs_scipy_quad.png",
        "mc_vs_gaussian.png",
        "mc_vs_simpson.png",
        "mc_vs_trapezoid.png",
        "mc_diff_scipy_quad.png",
        "mc_diff_gaussian.png",
        "mc_diff_simpson.png",
        "mc_diff_trapezoid.png",
        "mc_summary_mean_abs_difference.png",
        "mc_summary_rmse_difference.png",
    ]
    for figure_name in expected_figures:
        assert (figures_dir / "monte_carlo" / figure_name).exists()
