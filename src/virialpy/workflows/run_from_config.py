"""Run general workflows from a YAML configuration file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from virialpy.config import load_config, validate_run_config


def run_from_config(config_path: str | Path) -> dict[str, str]:
    """Execute the general workflow described by a YAML configuration file."""
    from virialpy.cli.main import (
        _generate_general_monte_carlo_outputs,
        _run_general_b2,
        _run_general_fit,
        _run_general_validate,
    )

    config = load_config(config_path)
    validate_run_config(config)

    system = str(config["system"])
    data = config["data"]
    models = config["models"]
    integrators = config["integrators"]
    units = config["units"]
    b2 = config["b2"]
    outputs = config["outputs"]
    run = config["run"]

    results_dir = Path(outputs["results_dir"])
    figures_dir = Path(outputs["figures_dir"])
    reports_dir = Path(outputs["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)

    generated = {
        "results_dir": str(results_dir),
        "figures_dir": str(figures_dir),
        "reports_dir": str(reports_dir),
        "fit_metrics": str(results_dir / "fit_comparison_metrics.csv"),
        "b2_comparison": str(results_dir / "b2_comparison_all.csv"),
        "b2_experiment_metrics": str(results_dir / "b2_experiment_metrics.csv"),
    }

    if run["fit"]:
        _run_general_fit(
            system=system,
            potential_data=Path(data["potential_data"]),
            r_column=str(data["r_column"]),
            energy_column=str(data["energy_column"]),
            potentials=[str(potential) for potential in models["potentials"]],
            output_dir=results_dir,
        )

    if run["b2"]:
        _run_general_b2(
            system=system,
            experimental_data=Path(data["experimental_data"]),
            temperature_column=str(data["temperature_column"]),
            potentials=[str(potential) for potential in models["potentials"]],
            integrators=[str(name) for name in integrators["names"]],
            results_dir=results_dir,
            energy_unit=str(units["energy_unit"]),
            distance_unit=str(units["distance_unit"]),
            r_min=float(b2["r_min"]),
            r_max=float(b2["r_max"]),
        )

    monte_carlo_plots = bool(run.get("monte_carlo_plots", True))
    if run["validate"]:
        _run_general_validate(
            system=system,
            experimental_data=Path(data["experimental_data"]),
            temperature_column=str(data["temperature_column"]),
            b2_column=str(data["b2_column"]),
            results_dir=results_dir,
            figures_dir=figures_dir,
            generate_monte_carlo_plots=monte_carlo_plots,
        )
    elif monte_carlo_plots and run["b2"]:
        _generate_general_monte_carlo_outputs(
            system=system,
            results_dir=results_dir,
            figures_dir=figures_dir,
        )

    return generated
