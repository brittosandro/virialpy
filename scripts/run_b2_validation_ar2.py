"""Validate calculated Ar2 B2 values against experimental data."""

from __future__ import annotations

from virialpy.plotting import plot_b2_comparison, plot_b2_metrics, plot_b2_residuals
from virialpy.workflows import validate_b2_against_experiment


def main() -> None:
    """Run the Ar2 B2 validation workflow example."""
    comparison_df, metrics_df = validate_b2_against_experiment(
        calculated_path="data/results/ar2/b2_comparison_all.csv",
        experimental_path="data/raw/ar2/b2_experimental.csv",
        temperature_column_exp="Temperatura",
        b2_column_exp="B(segundo coef. virial) [cm³/mol]",
        group_columns=("potential", "integrator"),
        output_comparison_path="data/results/ar2/b2_experiment_comparison.csv",
        output_metrics_path="data/results/ar2/b2_experiment_metrics.csv",
    )

    plot_b2_comparison(
        comparison_df,
        output_path="outputs/figures/ar2/b2/b2_comparison_scipy_quad.png",
        title=r"Comparação entre $B(T)$ calculado e experimental para Ar$_2$",
        integrator="scipy_quad",
    )
    plot_b2_residuals(
        comparison_df,
        output_path="outputs/figures/ar2/b2/b2_residuals_scipy_quad.png",
        title=r"Resíduos de $B(T)$ para Ar$_2$",
        integrator="scipy_quad",
    )
    plot_b2_metrics(
        metrics_df,
        metric="rmse",
        output_path="outputs/figures/ar2/b2/b2_rmse_metrics.png",
        title=r"RMSE dos modelos de $B(T)$ para Ar$_2$",
        xlabel=r"Erro / cm$^3$ mol$^{-1}$",
        ylabel="Modelo",
    )
    plot_b2_metrics(
        metrics_df,
        metric="mae",
        output_path="outputs/figures/ar2/b2/b2_mae_metrics.png",
        title=r"MAE dos modelos de $B(T)$ para Ar$_2$",
        xlabel=r"Erro / cm$^3$ mol$^{-1}$",
        ylabel="Modelo",
    )

    print(comparison_df.head())
    print(metrics_df.sort_values("rmse"))


if __name__ == "__main__":
    main()
