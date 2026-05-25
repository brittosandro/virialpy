"""Command-line interface for virialpy."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer

from virialpy.fitting import get_default_fit_settings
from virialpy.integrators import (
    GaussianQuadratureIntegrator,
    MonteCarloIntegrator,
    ScipyQuadIntegrator,
    SimpsonIntegrator,
    TrapezoidIntegrator,
)


app = typer.Typer(help="Scientific tools for virial coefficient workflows.")
ar2_app = typer.Typer(help="Run reproducible Ar2 workflows.")
run_app = typer.Typer(help="Run general workflows from user-provided paths.")
app.add_typer(ar2_app, name="ar2")
app.add_typer(run_app, name="run")


POTENTIAL_LABELS = {
    "lj": "LJ",
    "ilj": "ILJ",
    "ryd6": "Ryd6",
}

INTEGRATOR_LABELS = {
    "scipy_quad": "SciPy quad",
    "gaussian": "Gauss-Legendre",
    "simpson": "Simpson",
    "trapezoid": "Trapezoid",
    "monte_carlo": "Monte Carlo",
}


def _run_script(script_name: str, description: str) -> None:
    """Run a project script from the repository root."""
    repo_root = Path.cwd()
    script_path = repo_root / "scripts" / script_name
    if not script_path.exists():
        raise typer.BadParameter(f"Script not found: {script_path}")

    typer.echo(f"Starting: {description}")
    try:
        subprocess.run([sys.executable, str(script_path)], cwd=repo_root, check=True)
    except subprocess.CalledProcessError as exc:
        raise typer.Exit(code=exc.returncode) from exc
    typer.echo(f"Finished: {description}")


def normalize_potentials(potentials: list[str]) -> list[str]:
    """Normalize potential names accepted by the general CLI."""
    supported = ["lj", "ilj", "ryd6"]
    requested = potentials or ["all"]
    expanded: list[str] = []

    for potential in requested:
        normalized = potential.lower()
        if normalized == "all":
            candidates = supported
        elif normalized in supported:
            candidates = [normalized]
        else:
            available = ", ".join([*supported, "all"])
            raise ValueError(
                f"Invalid potential '{potential}'. Available options: {available}"
            )

        for candidate in candidates:
            if candidate not in expanded:
                expanded.append(candidate)

    return expanded


def create_integrators(names: list[str]) -> list[dict[str, object]]:
    """Create integrator descriptors accepted by B(T) comparison workflows."""
    supported = ["scipy_quad", "gaussian", "simpson", "trapezoid", "monte_carlo"]
    requested = names or ["all"]
    expanded: list[str] = []

    for name in requested:
        normalized = name.lower()
        if normalized == "all":
            candidates = supported
        elif normalized in supported:
            candidates = [normalized]
        else:
            available = ", ".join([*supported, "all"])
            raise ValueError(
                f"Invalid integrator '{name}'. Available options: {available}"
            )

        for candidate in candidates:
            if candidate not in expanded:
                expanded.append(candidate)

    factories = {
        "scipy_quad": lambda: ScipyQuadIntegrator(),
        "gaussian": lambda: GaussianQuadratureIntegrator(n_points=128),
        "simpson": lambda: SimpsonIntegrator(n_points=20001),
        "trapezoid": lambda: TrapezoidIntegrator(n_points=20000),
        "monte_carlo": lambda: MonteCarloIntegrator(n_samples=200000, random_state=42),
    }

    return [
        {
            "name": name,
            "label": INTEGRATOR_LABELS[name],
            "integrator": factories[name](),
        }
        for name in expanded
    ]


def _model_configs(potentials: list[str]) -> list[dict[str, object]]:
    """Build model dictionaries for fitting workflows."""
    models = []
    for potential in potentials:
        settings = get_default_fit_settings(potential)
        models.append(
            {
                "name": potential,
                "label": POTENTIAL_LABELS[potential],
                "initial_guess": settings["initial_guess"],
                "parameter_names": settings["parameter_names"],
            }
        )
    return models


def _model_references(potentials: list[str]) -> list[dict[str, str]]:
    """Build model references for loading fitted parameters."""
    return [
        {
            "name": potential,
            "label": POTENTIAL_LABELS[potential],
        }
        for potential in potentials
    ]


def _abort(error: Exception) -> None:
    """Print a short CLI error and exit."""
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=1)


def _run_general_fit(
    system: str,
    potential_data: Path,
    r_column: str,
    energy_column: str,
    potentials: list[str],
    output_dir: Path,
) -> None:
    """Fit selected potentials and save per-model results."""
    from virialpy.workflows.compare_potentials import (
        run_potential_comparison_workflow,
        summarize_fit_results,
    )

    potential_names = normalize_potentials(potentials)
    typer.echo(f"[{system}] Fitting potentials: {', '.join(potential_names)}")
    results = run_potential_comparison_workflow(
        data_path=potential_data,
        models=_model_configs(potential_names),
        r_column=r_column,
        energy_column=energy_column,
        results_dir=output_dir,
    )
    summary_path = output_dir / "fit_comparison_metrics.csv"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summarize_fit_results(results).to_csv(summary_path, index=False)
    typer.echo(f"[{system}] Fit results saved to {output_dir}")


def _run_general_b2(
    system: str,
    experimental_data: Path,
    temperature_column: str,
    potentials: list[str],
    integrators: list[str],
    results_dir: Path,
    energy_unit: str,
    distance_unit: str,
    r_min: float,
    r_max: float,
) -> None:
    """Calculate B(T) for selected potentials and integrators."""
    from virialpy.workflows.calculate_b2 import load_temperatures_from_csv
    from virialpy.workflows.compare_b2 import (
        load_model_parameters_from_results,
        run_b2_comparison_workflow,
    )

    potential_names = normalize_potentials(potentials)
    integrator_configs = create_integrators(integrators)
    typer.echo(
        f"[{system}] Calculating B(T) for {len(potential_names)} potentials and "
        f"{len(integrator_configs)} integrators"
    )
    temperatures = load_temperatures_from_csv(
        experimental_data,
        temperature_column=temperature_column,
    )
    models = load_model_parameters_from_results(
        results_dir,
        _model_references(potential_names),
    )
    output_path = results_dir / "b2_comparison_all.csv"
    run_b2_comparison_workflow(
        models=models,
        temperatures=temperatures,
        integrators=integrator_configs,
        r_min=r_min,
        r_max=r_max,
        distance_unit=distance_unit,
        energy_unit=energy_unit,
        output_path=output_path,
    )
    typer.echo(f"[{system}] B(T) results saved to {output_path}")


def _run_general_validate(
    system: str,
    experimental_data: Path,
    temperature_column: str,
    b2_column: str,
    results_dir: Path,
    figures_dir: Path,
) -> None:
    """Validate calculated B(T) values and generate standard figures."""
    from virialpy.plotting import plot_b2_comparison, plot_b2_metrics, plot_b2_residuals
    from virialpy.workflows.validate_b2 import validate_b2_against_experiment

    typer.echo(f"[{system}] Validating calculated B(T) against experiment")
    comparison_path = results_dir / "b2_experiment_comparison.csv"
    metrics_path = results_dir / "b2_experiment_metrics.csv"
    comparison, metrics = validate_b2_against_experiment(
        calculated_path=results_dir / "b2_comparison_all.csv",
        experimental_path=experimental_data,
        temperature_column_exp=temperature_column,
        b2_column_exp=b2_column,
        group_columns=("potential", "integrator"),
        output_comparison_path=comparison_path,
        output_metrics_path=metrics_path,
    )

    b2_figures_dir = figures_dir / "b2"
    plot_b2_comparison(
        comparison,
        output_path=b2_figures_dir / "b2_comparison_scipy_quad.png",
        title=rf"Comparison between calculated and experimental $B(T)$ for {system}",
        integrator="scipy_quad",
    )
    plot_b2_residuals(
        comparison,
        output_path=b2_figures_dir / "b2_residuals_scipy_quad.png",
        title=rf"$B(T)$ residuals for {system}",
        integrator="scipy_quad",
    )
    plot_b2_metrics(
        metrics,
        metric="rmse",
        output_path=b2_figures_dir / "b2_rmse_metrics.png",
        title=rf"RMSE of $B(T)$ models for {system}",
        xlabel=r"Error / cm$^3$ mol$^{-1}$",
        ylabel="Model",
    )
    plot_b2_metrics(
        metrics,
        metric="mae",
        output_path=b2_figures_dir / "b2_mae_metrics.png",
        title=rf"MAE of $B(T)$ models for {system}",
        xlabel=r"Error / cm$^3$ mol$^{-1}$",
        ylabel="Model",
    )
    typer.echo(f"[{system}] Validation tables saved to {results_dir}")
    typer.echo(f"[{system}] Validation figures saved to {b2_figures_dir}")
    _generate_general_monte_carlo_outputs(
        system=system,
        results_dir=results_dir,
        figures_dir=figures_dir,
    )


def _generate_general_monte_carlo_outputs(
    system: str,
    results_dir: Path,
    figures_dir: Path,
) -> None:
    """Generate Monte Carlo comparison tables and figures when MC data exists."""
    import matplotlib.pyplot as plt
    import pandas as pd

    from virialpy.analysis import (
        compare_monte_carlo_with_integrators,
        summarize_monte_carlo_comparison,
    )
    from virialpy.plotting import (
        plot_monte_carlo_difference,
        plot_monte_carlo_summary_metrics,
        plot_monte_carlo_vs_reference,
    )

    b2_results_path = results_dir / "b2_comparison_all.csv"
    if not b2_results_path.exists():
        return

    b2_results = pd.read_csv(b2_results_path, usecols=["integrator"])
    if "monte_carlo" not in set(b2_results["integrator"]):
        return

    reference_order = ["scipy_quad", "gaussian", "simpson", "trapezoid"]
    available_integrators = set(b2_results["integrator"])
    reference_integrators = [
        integrator for integrator in reference_order if integrator in available_integrators
    ]
    if not reference_integrators:
        return

    typer.echo(f"[{system}] Generating Monte Carlo comparison figures")
    comparison_path = results_dir / "monte_carlo_comparison.csv"
    summary_path = results_dir / "monte_carlo_comparison_summary.csv"
    comparison = compare_monte_carlo_with_integrators(
        b2_results_path=b2_results_path,
        reference_integrators=reference_integrators,
        output_path=comparison_path,
    )
    summary = summarize_monte_carlo_comparison(comparison)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)

    mc_figures_dir = figures_dir / "monte_carlo"
    for reference_integrator in reference_integrators:
        fig = plot_monte_carlo_vs_reference(
            comparison,
            reference_integrator=reference_integrator,
            output_path=mc_figures_dir / f"mc_vs_{reference_integrator}.png",
            title=rf"Monte Carlo vs {reference_integrator} for {system}",
            xlabel=r"$T$ / K",
            ylabel=r"$B_2(T)$ / cm$^3$ mol$^{-1}$",
        )
        plt.close(fig)
        fig = plot_monte_carlo_difference(
            comparison,
            reference_integrator=reference_integrator,
            output_path=mc_figures_dir / f"mc_diff_{reference_integrator}.png",
            title=rf"Monte Carlo difference vs {reference_integrator} for {system}",
            xlabel=r"$T$ / K",
            ylabel=r"$B_{2,\mathrm{MC}} - B_{2,\mathrm{ref}}$ / cm$^3$ mol$^{-1}$",
        )
        plt.close(fig)

    fig = plot_monte_carlo_summary_metrics(
        summary,
        metric="mean_abs_difference",
        output_path=mc_figures_dir / "mc_summary_mean_abs_difference.png",
        title=rf"Mean absolute Monte Carlo differences for {system}",
        xlabel=r"Difference / cm$^3$ mol$^{-1}$",
        ylabel="Model",
    )
    plt.close(fig)
    fig = plot_monte_carlo_summary_metrics(
        summary,
        metric="rmse_difference",
        output_path=mc_figures_dir / "mc_summary_rmse_difference.png",
        title=rf"RMSE Monte Carlo differences for {system}",
        xlabel=r"Difference / cm$^3$ mol$^{-1}$",
        ylabel="Model",
    )
    plt.close(fig)
    typer.echo(f"[{system}] Monte Carlo comparison figures saved to {mc_figures_dir}")


@ar2_app.command()
def fit() -> None:
    """Fit and compare Ar2 intermolecular potentials."""
    _run_script("run_compare_potentials_ar2.py", "Ar2 potential fitting")


@ar2_app.command()
def b2() -> None:
    """Calculate direct B(T) values for Ar2 potentials and integrators."""
    _run_script("run_b2_comparison_ar2.py", "Ar2 direct B(T) comparison")


@ar2_app.command()
def validate() -> None:
    """Validate calculated Ar2 B(T) values against experiment."""
    _run_script("run_b2_validation_ar2.py", "Ar2 B(T) experimental validation")


@ar2_app.command()
def partitioned() -> None:
    """Calculate partitioned B(T) values for Ar2."""
    _run_script("run_partitioned_b2_ar2.py", "Ar2 partitioned B(T)")


@ar2_app.command()
def methods() -> None:
    """Compare direct and partitioned Ar2 B(T) methods."""
    _run_script("run_b2_method_comparison_ar2.py", "Ar2 B(T) method comparison")


@ar2_app.command("monte-carlo")
def monte_carlo() -> None:
    """Compare Monte Carlo integration with other Ar2 integrators."""
    _run_script("run_monte_carlo_comparison_ar2.py", "Ar2 Monte Carlo comparison")


@ar2_app.command()
def figures() -> None:
    """Generate final Ar2 figures and report tables."""
    _run_script("gerar_figuras_tabelas_finais_ar2.py", "Ar2 final figures and tables")


@ar2_app.command("full-pipeline")
def full_pipeline() -> None:
    """Run the complete reproducible Ar2 pipeline."""
    _run_script("run_ar2_full_pipeline.py", "Ar2 full pipeline")


@run_app.command("fit")
def run_fit(
    system: Annotated[str, typer.Option("--system", help="Molecular system label.")],
    potential_data: Annotated[
        Path,
        typer.Option("--potential-data", exists=True, file_okay=True, dir_okay=False),
    ],
    r_column: Annotated[str, typer.Option("--r-column")] = "r",
    energy_column: Annotated[str, typer.Option("--energy-column")] = "energy",
    potentials: Annotated[
        list[str],
        typer.Option("--potentials", help="Potential name: lj, ilj, ryd6, or all."),
    ] = ["all"],
    output_dir: Annotated[Path, typer.Option("--output-dir")] = Path("data/results"),
) -> None:
    """Fit one or more registered potentials to U(r) data."""
    try:
        _run_general_fit(
            system=system,
            potential_data=potential_data,
            r_column=r_column,
            energy_column=energy_column,
            potentials=potentials,
            output_dir=output_dir,
        )
    except Exception as exc:
        _abort(exc)


@run_app.command("b2")
def run_b2(
    system: Annotated[str, typer.Option("--system", help="Molecular system label.")],
    experimental_data: Annotated[
        Path,
        typer.Option("--experimental-data", exists=True, file_okay=True, dir_okay=False),
    ],
    temperature_column: Annotated[str, typer.Option("--temperature-column")] = "temperature",
    potentials: Annotated[
        list[str],
        typer.Option("--potentials", help="Potential name: lj, ilj, ryd6, or all."),
    ] = ["all"],
    integrators: Annotated[
        list[str],
        typer.Option(
            "--integrators",
            help="Integrator name: scipy_quad, gaussian, simpson, trapezoid, monte_carlo, or all.",
        ),
    ] = ["all"],
    results_dir: Annotated[Path, typer.Option("--results-dir")] = Path("data/results"),
    energy_unit: Annotated[str, typer.Option("--energy-unit")] = "kelvin",
    distance_unit: Annotated[str, typer.Option("--distance-unit")] = "angstrom",
    r_min: Annotated[float, typer.Option("--r-min")] = 0.0,
    r_max: Annotated[float, typer.Option("--r-max")] = 30.0,
) -> None:
    """Calculate B(T) for selected fitted potentials and integrators."""
    try:
        _run_general_b2(
            system=system,
            experimental_data=experimental_data,
            temperature_column=temperature_column,
            potentials=potentials,
            integrators=integrators,
            results_dir=results_dir,
            energy_unit=energy_unit,
            distance_unit=distance_unit,
            r_min=r_min,
            r_max=r_max,
        )
    except Exception as exc:
        _abort(exc)


@run_app.command("validate")
def run_validate(
    system: Annotated[str, typer.Option("--system", help="Molecular system label.")],
    experimental_data: Annotated[
        Path,
        typer.Option("--experimental-data", exists=True, file_okay=True, dir_okay=False),
    ],
    temperature_column: Annotated[str, typer.Option("--temperature-column")] = "temperature",
    b2_column: Annotated[str, typer.Option("--b2-column")] = "b2",
    results_dir: Annotated[Path, typer.Option("--results-dir")] = Path("data/results"),
    figures_dir: Annotated[Path, typer.Option("--figures-dir")] = Path("outputs/figures"),
) -> None:
    """Validate calculated B(T) values against experimental data."""
    try:
        _run_general_validate(
            system=system,
            experimental_data=experimental_data,
            temperature_column=temperature_column,
            b2_column=b2_column,
            results_dir=results_dir,
            figures_dir=figures_dir,
        )
    except Exception as exc:
        _abort(exc)


@run_app.command("full")
def run_full(
    system: Annotated[str, typer.Option("--system", help="Molecular system label.")],
    potential_data: Annotated[
        Path,
        typer.Option("--potential-data", exists=True, file_okay=True, dir_okay=False),
    ],
    experimental_data: Annotated[
        Path,
        typer.Option("--experimental-data", exists=True, file_okay=True, dir_okay=False),
    ],
    r_column: Annotated[str, typer.Option("--r-column")] = "r",
    energy_column: Annotated[str, typer.Option("--energy-column")] = "energy",
    temperature_column: Annotated[str, typer.Option("--temperature-column")] = "temperature",
    b2_column: Annotated[str, typer.Option("--b2-column")] = "b2",
    potentials: Annotated[
        list[str],
        typer.Option("--potentials", help="Potential name: lj, ilj, ryd6, or all."),
    ] = ["all"],
    integrators: Annotated[
        list[str],
        typer.Option(
            "--integrators",
            help="Integrator name: scipy_quad, gaussian, simpson, trapezoid, monte_carlo, or all.",
        ),
    ] = ["all"],
    energy_unit: Annotated[str, typer.Option("--energy-unit")] = "kelvin",
    distance_unit: Annotated[str, typer.Option("--distance-unit")] = "angstrom",
    r_min: Annotated[float, typer.Option("--r-min")] = 0.0,
    r_max: Annotated[float, typer.Option("--r-max")] = 30.0,
    results_dir: Annotated[Path, typer.Option("--results-dir")] = Path("data/results"),
    figures_dir: Annotated[Path, typer.Option("--figures-dir")] = Path("outputs/figures"),
    reports_dir: Annotated[Path, typer.Option("--reports-dir")] = Path("outputs/reports"),
) -> None:
    """Run the first general pipeline layer: fit, B(T), and validation."""
    try:
        typer.echo(f"[{system}] Starting general pipeline")
        _run_general_fit(
            system=system,
            potential_data=potential_data,
            r_column=r_column,
            energy_column=energy_column,
            potentials=potentials,
            output_dir=results_dir,
        )
        _run_general_b2(
            system=system,
            experimental_data=experimental_data,
            temperature_column=temperature_column,
            potentials=potentials,
            integrators=integrators,
            results_dir=results_dir,
            energy_unit=energy_unit,
            distance_unit=distance_unit,
            r_min=r_min,
            r_max=r_max,
        )
        _run_general_validate(
            system=system,
            experimental_data=experimental_data,
            temperature_column=temperature_column,
            b2_column=b2_column,
            results_dir=results_dir,
            figures_dir=figures_dir,
        )
        reports_dir.mkdir(parents=True, exist_ok=True)
        typer.echo(f"[{system}] General pipeline completed")
    except Exception as exc:
        _abort(exc)
