"""Compare Monte Carlo B(T) results with deterministic integrators for Ar2."""

from __future__ import annotations

from virialpy.analysis import (
    compare_monte_carlo_with_integrators,
    summarize_monte_carlo_comparison,
)
from virialpy.plotting import (
    plot_monte_carlo_difference,
    plot_monte_carlo_summary_metrics,
    plot_monte_carlo_vs_reference,
)


def main() -> None:
    comparison = compare_monte_carlo_with_integrators(
        "data/results/ar2/b2_comparison_all.csv",
        output_path="data/results/ar2/monte_carlo_comparison.csv",
    )
    summary = summarize_monte_carlo_comparison(comparison)
    summary.to_csv("data/results/ar2/monte_carlo_comparison_summary.csv", index=False)

    references = ["scipy_quad", "gaussian", "simpson", "trapezoid"]
    for reference in references:
        plot_monte_carlo_vs_reference(
            comparison,
            reference,
            output_path=f"outputs/figures/ar2/monte_carlo/mc_vs_{reference}.png",
            title=f"Monte Carlo vs {reference}",
        )
        plot_monte_carlo_difference(
            comparison,
            reference,
            output_path=f"outputs/figures/ar2/monte_carlo/mc_diff_{reference}.png",
            title=f"Diferença Monte Carlo - {reference}",
        )

    plot_monte_carlo_summary_metrics(
        summary,
        metric="mean_abs_difference",
        output_path="outputs/figures/ar2/monte_carlo/mc_summary_mean_abs_difference.png",
        title="Diferença absoluta média do Monte Carlo",
    )
    plot_monte_carlo_summary_metrics(
        summary,
        metric="rmse_difference",
        output_path="outputs/figures/ar2/monte_carlo/mc_summary_rmse_difference.png",
        title="RMSE da diferença do Monte Carlo",
    )

    print(comparison.head())
    print(summary.sort_values("mean_abs_difference"))


if __name__ == "__main__":
    main()

