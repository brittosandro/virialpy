"""Workflow for generating multi-system comparison outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from virialpy.analysis import build_multisystem_summary_tables, save_table_csv, save_table_latex
from virialpy.plotting import (
    plot_best_b2_model_by_system,
    plot_best_integrator_by_system,
    plot_direct_partitioned_comparison,
    plot_system_ranking,
)


def run_multisystem_comparison_workflow(
    systems: list[dict[str, Any]],
    results_dir: str | Path = "data/results/multisystem",
    figures_dir: str | Path = "outputs/figures/multisystem",
    reports_dir: str | Path = "outputs/reports/multisystem",
) -> dict[str, str]:
    """Create final multi-system tables and figures from existing outputs."""
    result_base = Path(results_dir)
    figure_base = Path(figures_dir)
    table_base = Path(reports_dir) / "tables"
    result_base.mkdir(parents=True, exist_ok=True)
    table_base.mkdir(parents=True, exist_ok=True)

    tables = build_multisystem_summary_tables(systems)
    table_names = {
        "fit_metrics": "fit_metrics_all_systems",
        "b2_metrics": "b2_metrics_all_systems",
        "method_metrics": "b2_method_metrics_all_systems",
        "best_fit_potential": "best_potential_by_system",
        "best_b2_model": "best_b2_model_by_system",
        "best_integrator": "best_integrator_by_system",
        "direct_vs_partitioned": "direct_vs_partitioned_by_system",
        "best_method": "best_method_by_system",
        "system_ranking": "system_ranking",
    }

    for key, filename in table_names.items():
        csv_path = result_base / f"{filename}.csv"
        report_csv_path = table_base / f"{filename}.csv"
        tex_path = table_base / f"{filename}.tex"
        save_table_csv(tables[key], csv_path)
        save_table_csv(tables[key], report_csv_path)
        save_table_latex(
            tables[key],
            tex_path,
            caption=f"Multi-system table: {filename.replace('_', ' ')}.",
            label=f"tab:{filename}",
        )

    figure_base.mkdir(parents=True, exist_ok=True)
    fig = plot_best_b2_model_by_system(
        tables["best_b2_model"],
        output_path=figure_base / "best_b2_model_by_system.png",
        title="Melhor combinação potencial-integrador por sistema",
    )
    plt.close(fig)
    fig = plot_best_integrator_by_system(
        tables["best_integrator"],
        output_path=figure_base / "best_integrator_by_system.png",
        title="Melhor integrador médio por sistema",
    )
    plt.close(fig)
    fig = plot_direct_partitioned_comparison(
        tables["direct_vs_partitioned"],
        output_path=figure_base / "direct_vs_partitioned_by_system.png",
        title="Desempenho do método direto vs particionado",
    )
    plt.close(fig)
    fig = plot_system_ranking(
        tables["system_ranking"],
        output_path=figure_base / "system_ranking.png",
        title="Sistemas melhor descritos por B(T)",
    )
    plt.close(fig)

    return {
        "results_dir": str(result_base),
        "figures_dir": str(figure_base),
        "reports_dir": str(Path(reports_dir)),
        "tables_dir": str(table_base),
    }


def run_multisystem_analysis(
    system_results: list[dict[str, Any]],
    output_figures_dir: str | Path = "outputs/figures/multisystem",
    output_reports_dir: str | Path = "outputs/reports/multisystem",
    output_results_dir: str | Path = "data/results/multisystem",
) -> dict[str, str]:
    """Run the standard multi-system analysis from result directories."""
    return run_multisystem_comparison_workflow(
        systems=system_results,
        results_dir=output_results_dir,
        figures_dir=output_figures_dir,
        reports_dir=output_reports_dir,
    )
