"""Run general workflows from a YAML configuration file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

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
        "partitioned_comparison": str(results_dir / "partitioned_b2_comparison.csv"),
        "method_comparison": str(results_dir / "b2_method_experiment_comparison.csv"),
        "method_metrics": str(results_dir / "b2_method_experiment_metrics.csv"),
        "final_tables_dir": str(reports_dir / "tables"),
        "final_figures_dir": str(figures_dir / "final"),
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

    if run.get("partitioned", False):
        _run_config_partitioned_b2(
            system=system,
            config=config,
            results_dir=results_dir,
        )

    if run.get("method_comparison", False):
        _run_config_method_comparison(
            system=system,
            config=config,
            results_dir=results_dir,
            figures_dir=figures_dir,
        )

    if run.get("final_outputs", False):
        _run_config_final_outputs(
            system=system,
            results_dir=results_dir,
            figures_dir=figures_dir,
            reports_dir=reports_dir,
        )

    return generated


def _run_config_partitioned_b2(
    system: str,
    config: dict[str, Any],
    results_dir: Path,
) -> None:
    """Run partitioned B(T) calculations from validated configuration."""
    from virialpy.config import create_integrator_from_config
    from virialpy.workflows.calculate_b2 import load_temperatures_from_csv
    from virialpy.workflows.compare_b2 import load_model_parameters_from_results
    from virialpy.workflows.partitioned_b2 import run_partitioned_b2_workflow
    from virialpy.cli.main import _model_references, normalize_potentials

    partitioned = config.get("partitioned", {})
    if not partitioned.get("enabled", False):
        return

    typer_echo(f"[{system}] Calculating partitioned B(T)")
    data = config["data"]
    units = config["units"]
    potentials = normalize_potentials([str(p) for p in config["models"]["potentials"]])
    temperatures = load_temperatures_from_csv(
        data["experimental_data"],
        temperature_column=str(data["temperature_column"]),
    )
    models = load_model_parameters_from_results(results_dir, _model_references(potentials))
    model_parameters = {model["name"]: model["parameters"] for model in models}

    integrator_b2 = create_integrator_from_config(
        partitioned.get("integrator_b2", {"name": "gaussian"})
    )
    integrator_b3 = create_integrator_from_config(
        partitioned.get("integrator_b3", {"name": "gaussian"})
    )
    integrator_b4 = create_integrator_from_config(
        partitioned.get("integrator_b4", {"name": "gaussian"})
    )

    frames = []
    for potential in potentials:
        output_path = results_dir / f"partitioned_b2_{potential}.csv"
        frame = run_partitioned_b2_workflow(
            potential_name=potential,
            parameters=model_parameters[potential],
            temperatures=temperatures,
            integrator_b2=integrator_b2,
            integrator_b3=integrator_b3,
            integrator_b4=integrator_b4,
            r1=float(partitioned["r1"]),
            r2=float(partitioned["r2"]),
            r3=float(partitioned["r3"]),
            r4=float(partitioned["r4"]),
            distance_unit=str(units["distance_unit"]),
            energy_unit=str(units["energy_unit"]),
            output_path=output_path,
        )
        frames.append(frame)

    comparison = pd.concat(frames, ignore_index=True)
    comparison.to_csv(results_dir / "partitioned_b2_comparison.csv", index=False)
    typer_echo(f"[{system}] Partitioned B(T) results saved to {results_dir}")


def _run_config_method_comparison(
    system: str,
    config: dict[str, Any],
    results_dir: Path,
    figures_dir: Path,
) -> None:
    """Compare direct and partitioned B(T) methods and generate figures."""
    import matplotlib.pyplot as plt

    from virialpy.cli.main import normalize_potentials
    from virialpy.plotting import (
        plot_b2_method_metrics,
        plot_b2_method_residuals,
        plot_b2_methods_vs_experiment,
        plot_partitioned_contributions,
    )
    from virialpy.workflows import prepare_b2_method_comparison

    typer_echo(f"[{system}] Comparing direct and partitioned B(T) methods")
    data = config["data"]
    comparison_path = results_dir / "b2_method_experiment_comparison.csv"
    metrics_path = results_dir / "b2_method_experiment_metrics.csv"
    comparison, metrics = prepare_b2_method_comparison(
        direct_path=results_dir / "b2_comparison_all.csv",
        partitioned_path=results_dir / "partitioned_b2_comparison.csv",
        experimental_path=data["experimental_data"],
        direct_integrator="scipy_quad",
        temperature_column_exp=str(data["temperature_column"]),
        b2_column_exp=str(data["b2_column"]),
        output_comparison_path=comparison_path,
        output_metrics_path=metrics_path,
    )

    output_dir = figures_dir / "b2_methods"
    fig = plot_b2_methods_vs_experiment(
        comparison,
        output_path=output_dir / "b2_methods_vs_experiment.png",
        title=rf"Comparação entre métodos de cálculo de $B(T)$ para {system}",
    )
    plt.close(fig)
    fig = plot_b2_method_residuals(
        comparison,
        output_path=output_dir / "b2_methods_residuals.png",
        title=rf"Resíduos dos métodos de cálculo de $B(T)$ para {system}",
    )
    plt.close(fig)
    fig = plot_b2_method_metrics(
        metrics,
        metric="rmse",
        output_path=output_dir / "b2_methods_rmse.png",
        title=rf"RMSE dos métodos de cálculo de $B(T)$ para {system}",
    )
    plt.close(fig)
    fig = plot_b2_method_metrics(
        metrics,
        metric="mae",
        output_path=output_dir / "b2_methods_mae.png",
        title=rf"MAE dos métodos de cálculo de $B(T)$ para {system}",
    )
    plt.close(fig)

    partitioned_df = pd.read_csv(results_dir / "partitioned_b2_comparison.csv")
    potentials = normalize_potentials([str(p) for p in config["models"]["potentials"]])
    for potential in potentials:
        fig = plot_partitioned_contributions(
            partitioned_df,
            potential=potential,
            output_path=output_dir / f"partitioned_contributions_{potential}.png",
            title=f"Contribuições particionadas para {potential} em {system}",
        )
        plt.close(fig)
    typer_echo(f"[{system}] Method-comparison figures saved to {output_dir}")


def _run_config_final_outputs(
    system: str,
    results_dir: Path,
    figures_dir: Path,
    reports_dir: Path,
) -> None:
    """Generate final figures and report tables from available result files."""
    import matplotlib.pyplot as plt

    from virialpy.analysis import (
        create_b2_metrics_table,
        create_fit_summary_table,
        save_table_csv,
        save_table_latex,
    )
    from virialpy.plotting import (
        plot_final_b2_comparison,
        plot_final_b2_residuals,
        plot_final_method_comparison,
        plot_final_metric_ranking,
        plot_monte_carlo_summary_metrics,
        plot_monte_carlo_vs_reference,
    )

    typer_echo(f"[{system}] Generating final figures and tables")
    final_dir = figures_dir / "final"
    table_dir = reports_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)

    b2_comparison_path = results_dir / "b2_experiment_comparison.csv"
    b2_metrics_path = results_dir / "b2_experiment_metrics.csv"
    method_comparison_path = results_dir / "b2_method_experiment_comparison.csv"
    method_metrics_path = results_dir / "b2_method_experiment_metrics.csv"

    if b2_comparison_path.exists() and b2_metrics_path.exists():
        b2_comparison = pd.read_csv(b2_comparison_path)
        b2_metrics = pd.read_csv(b2_metrics_path)
        fig = plot_final_b2_comparison(
            b2_comparison,
            output_path=final_dir / "final_b2_comparison.png",
            title=rf"Comparação final de $B(T)$ para {system}",
            ylabel=r"$B(T)$ / cm$^3$ mol$^{-1}$",
        )
        plt.close(fig)
        fig = plot_final_b2_residuals(
            b2_comparison,
            output_path=final_dir / "final_b2_residuals.png",
            title=rf"Resíduos finais de $B(T)$ para {system}",
        )
        plt.close(fig)
        fig = plot_final_metric_ranking(
            b2_metrics,
            metric="rmse",
            output_path=final_dir / "final_b2_rmse_ranking.png",
            title=rf"Ranking de RMSE para $B(T)$ em {system}",
            xlabel=r"Erro / cm$^3$ mol$^{-1}$",
        )
        plt.close(fig)
        fig = plot_final_metric_ranking(
            b2_metrics,
            metric="mae",
            output_path=final_dir / "final_b2_mae_ranking.png",
            title=rf"Ranking de MAE para $B(T)$ em {system}",
            xlabel=r"Erro / cm$^3$ mol$^{-1}$",
        )
        plt.close(fig)

    if method_comparison_path.exists() and method_metrics_path.exists():
        method_comparison = pd.read_csv(method_comparison_path)
        method_metrics = pd.read_csv(method_metrics_path)
        fig = plot_final_method_comparison(
            method_comparison,
            output_path=final_dir / "final_b2_method_comparison.png",
            title=f"Comparação entre métodos direto e particionado para {system}",
            ylabel=r"$B(T)$ / cm$^3$ mol$^{-1}$",
        )
        plt.close(fig)
        fig = plot_final_metric_ranking(
            method_metrics,
            metric="rmse",
            output_path=final_dir / "final_b2_method_rmse_ranking.png",
            title=rf"Ranking de RMSE por método para $B(T)$ em {system}",
            xlabel=r"Erro / cm$^3$ mol$^{-1}$",
        )
        plt.close(fig)
        fig = plot_final_metric_ranking(
            method_metrics,
            metric="mae",
            output_path=final_dir / "final_b2_method_mae_ranking.png",
            title=rf"Ranking de MAE por método para $B(T)$ em {system}",
            xlabel=r"Erro / cm$^3$ mol$^{-1}$",
        )
        plt.close(fig)

    fit_metrics_path = results_dir / "fit_comparison_metrics.csv"
    if fit_metrics_path.exists():
        fit_summary = create_fit_summary_table(fit_metrics_path)
        save_table_csv(fit_summary, table_dir / "fit_summary.csv")
        save_table_latex(
            fit_summary,
            table_dir / "fit_summary.tex",
            caption=f"Resumo das métricas de ajuste dos potenciais para {system}.",
            label=f"tab:fit_summary_{system}",
        )
    if b2_metrics_path.exists():
        b2_metrics_table = create_b2_metrics_table(b2_metrics_path)
        save_table_csv(b2_metrics_table, table_dir / "b2_metrics.csv")
        save_table_latex(
            b2_metrics_table,
            table_dir / "b2_metrics.tex",
            caption=f"Métricas de comparação entre B(T) calculado e experimental para {system}.",
            label=f"tab:b2_metrics_{system}",
        )
    if method_metrics_path.exists():
        method_metrics_table = create_b2_metrics_table(method_metrics_path)
        save_table_csv(method_metrics_table, table_dir / "b2_method_metrics.csv")
        save_table_latex(
            method_metrics_table,
            table_dir / "b2_method_metrics.tex",
            caption=f"Métricas de comparação entre métodos direto e particionado para {system}.",
            label=f"tab:b2_method_metrics_{system}",
        )

    mc_comparison_path = results_dir / "monte_carlo_comparison.csv"
    mc_summary_path = results_dir / "monte_carlo_comparison_summary.csv"
    if mc_comparison_path.exists() and mc_summary_path.exists():
        mc_comparison = pd.read_csv(mc_comparison_path)
        mc_summary = pd.read_csv(mc_summary_path)
        save_table_csv(mc_comparison, table_dir / "monte_carlo_comparison.csv")
        save_table_latex(
            mc_comparison,
            table_dir / "monte_carlo_comparison.tex",
            caption=f"Comparação detalhada entre Monte Carlo e demais integradores para {system}.",
            label=f"tab:mc_comparison_{system}",
        )
        save_table_csv(mc_summary, table_dir / "monte_carlo_comparison_summary.csv")
        save_table_latex(
            mc_summary,
            table_dir / "monte_carlo_comparison_summary.tex",
            caption=f"Resumo estatístico das diferenças entre Monte Carlo e demais integradores para {system}.",
            label=f"tab:mc_comparison_summary_{system}",
        )
        for reference in ["scipy_quad", "gaussian", "simpson", "trapezoid"]:
            if reference in set(mc_comparison["reference_integrator"]):
                fig = plot_monte_carlo_vs_reference(
                    mc_comparison,
                    reference_integrator=reference,
                    output_path=final_dir / f"final_mc_vs_{reference}.png",
                    title=f"Monte Carlo vs {reference}",
                )
                plt.close(fig)
        fig = plot_monte_carlo_summary_metrics(
            mc_summary,
            metric="mean_abs_difference",
            output_path=final_dir / "final_mc_summary_mean_abs_difference.png",
            title="Diferença absoluta média do Monte Carlo",
        )
        plt.close(fig)
        fig = plot_monte_carlo_summary_metrics(
            mc_summary,
            metric="rmse_difference",
            output_path=final_dir / "final_mc_summary_rmse_difference.png",
            title="RMSE da diferença do Monte Carlo",
        )
        plt.close(fig)
    typer_echo(f"[{system}] Final outputs saved to {final_dir} and {table_dir}")


def typer_echo(message: str) -> None:
    """Print progress messages without importing Typer at module import time."""
    import typer

    typer.echo(message)
