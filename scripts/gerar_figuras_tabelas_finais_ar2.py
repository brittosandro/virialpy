"""Generate final Ar2 figures and tables for reports."""

from __future__ import annotations

import pandas as pd

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
)


def main() -> None:
    """Generate final report-ready Ar2 outputs."""
    b2_comparison = pd.read_csv("data/results/ar2/b2_experiment_comparison.csv")
    b2_metrics = pd.read_csv("data/results/ar2/b2_experiment_metrics.csv")
    method_comparison = pd.read_csv("data/results/ar2/b2_method_experiment_comparison.csv")
    method_metrics = pd.read_csv("data/results/ar2/b2_method_experiment_metrics.csv")

    figure_dir = "outputs/figures/ar2/final"
    table_dir = "outputs/reports/ar2/tables"

    plot_final_b2_comparison(
        b2_comparison,
        output_path=f"{figure_dir}/final_b2_comparison.png",
        title=r"Comparação final de $B_2(T)$ para Ar$_2$",
    )
    plot_final_b2_residuals(
        b2_comparison,
        output_path=f"{figure_dir}/final_b2_residuals.png",
        title=r"Resíduos finais de $B_2(T)$ para Ar$_2$",
    )
    plot_final_metric_ranking(
        b2_metrics,
        metric="rmse",
        output_path=f"{figure_dir}/final_b2_rmse_ranking.png",
        title=r"Ranking de RMSE para $B_2(T)$ em Ar$_2$",
        xlabel=r"Erro / cm$^3$ mol$^{-1}$",
    )
    plot_final_metric_ranking(
        b2_metrics,
        metric="mae",
        output_path=f"{figure_dir}/final_b2_mae_ranking.png",
        title=r"Ranking de MAE para $B_2(T)$ em Ar$_2$",
        xlabel=r"Erro / cm$^3$ mol$^{-1}$",
    )
    plot_final_method_comparison(
        method_comparison,
        output_path=f"{figure_dir}/final_b2_method_comparison.png",
        title=r"Comparação entre métodos direto e particionado para Ar$_2$",
    )
    plot_final_metric_ranking(
        method_metrics,
        metric="rmse",
        output_path=f"{figure_dir}/final_b2_method_rmse_ranking.png",
        title=r"Ranking de RMSE por método para $B_2(T)$ em Ar$_2$",
        xlabel=r"Erro / cm$^3$ mol$^{-1}$",
    )
    plot_final_metric_ranking(
        method_metrics,
        metric="mae",
        output_path=f"{figure_dir}/final_b2_method_mae_ranking.png",
        title=r"Ranking de MAE por método para $B_2(T)$ em Ar$_2$",
        xlabel=r"Erro / cm$^3$ mol$^{-1}$",
    )

    fit_summary = create_fit_summary_table("data/results/ar2/fit_comparison_metrics.csv")
    b2_metrics_table = create_b2_metrics_table("data/results/ar2/b2_experiment_metrics.csv")
    method_metrics_table = create_b2_metrics_table(
        "data/results/ar2/b2_method_experiment_metrics.csv"
    )

    save_table_csv(fit_summary, f"{table_dir}/fit_summary.csv")
    save_table_latex(
        fit_summary,
        f"{table_dir}/fit_summary.tex",
        caption="Resumo das métricas de ajuste dos potenciais para Ar2.",
        label="tab:fit_summary_ar2",
    )
    save_table_csv(b2_metrics_table, f"{table_dir}/b2_metrics.csv")
    save_table_latex(
        b2_metrics_table,
        f"{table_dir}/b2_metrics.tex",
        caption="Métricas de comparação entre B2 calculado e experimental para Ar2.",
        label="tab:b2_metrics_ar2",
    )
    save_table_csv(method_metrics_table, f"{table_dir}/b2_method_metrics.csv")
    save_table_latex(
        method_metrics_table,
        f"{table_dir}/b2_method_metrics.tex",
        caption="Métricas de comparação entre métodos direto e particionado para Ar2.",
        label="tab:b2_method_metrics_ar2",
    )

    print(f"Figuras finais geradas em: {figure_dir}")
    print(f"Tabelas finais geradas em: {table_dir}")


if __name__ == "__main__":
    main()

