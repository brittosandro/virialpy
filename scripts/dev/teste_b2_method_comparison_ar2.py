"""Compare direct and partitioned B(T) methods for Ar2."""

from __future__ import annotations

import pandas as pd

from virialpy.plotting import (
    plot_b2_method_metrics,
    plot_b2_method_residuals,
    plot_b2_methods_vs_experiment,
    plot_partitioned_contributions,
)
from virialpy.workflows import prepare_b2_method_comparison


def main() -> None:
    """Run the Ar2 direct-vs-partitioned B(T) comparison example."""
    comparison_df, metrics_df = prepare_b2_method_comparison(
        direct_path="data/results/ar2/b2_comparison_all.csv",
        partitioned_path="data/results/ar2/partitioned_b2_comparison.csv",
        experimental_path="data/raw/ar2/b2_experimental.csv",
        direct_integrator="scipy_quad",
        temperature_column_exp="Temperatura",
        b2_column_exp="B(segundo coef. virial) [cm³/mol]",
        output_comparison_path="data/results/ar2/b2_method_experiment_comparison.csv",
        output_metrics_path="data/results/ar2/b2_method_experiment_metrics.csv",
    )

    plot_b2_methods_vs_experiment(
        comparison_df,
        output_path="outputs/figures/ar2/b2_methods/b2_methods_vs_experiment.png",
        title=r"Comparação entre métodos de cálculo de $B(T)$ para Ar$_2$",
    )
    plot_b2_method_residuals(
        comparison_df,
        output_path="outputs/figures/ar2/b2_methods/b2_methods_residuals.png",
        title=r"Resíduos dos métodos de cálculo de $B(T)$ para Ar$_2$",
    )
    plot_b2_method_metrics(
        metrics_df,
        metric="rmse",
        output_path="outputs/figures/ar2/b2_methods/b2_methods_rmse.png",
        title=r"RMSE dos métodos de cálculo de $B(T)$ para Ar$_2$",
        xlabel=r"Erro / cm$^3$ mol$^{-1}$",
    )
    plot_b2_method_metrics(
        metrics_df,
        metric="mae",
        output_path="outputs/figures/ar2/b2_methods/b2_methods_mae.png",
        title=r"MAE dos métodos de cálculo de $B(T)$ para Ar$_2$",
        xlabel=r"Erro / cm$^3$ mol$^{-1}$",
    )

    partitioned_df = pd.read_csv("data/results/ar2/partitioned_b2_comparison.csv")
    contribution_titles = {
        "lj": r"Contribuições particionadas para LJ em Ar$_2$",
        "ilj": r"Contribuições particionadas para ILJ em Ar$_2$",
        "ryd6": r"Contribuições particionadas para Rydberg 6 em Ar$_2$",
    }
    for potential, title in contribution_titles.items():
        plot_partitioned_contributions(
            partitioned_df,
            potential=potential,
            output_path=f"outputs/figures/ar2/b2_methods/partitioned_contributions_{potential}.png",
            title=title,
        )

    print(comparison_df.head())
    print(metrics_df.sort_values("rmse"))


if __name__ == "__main__":
    main()
