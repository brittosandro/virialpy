"""Compare multiple potential models for the Ar2 dataset."""

from __future__ import annotations

from virialpy.plotting import (
    plot_comparison_diagnostics,
    plot_fit_diagnostics,
    plot_fit_residuals,
    plot_fit_result,
    plot_multiple_fits,
    plot_multiple_residuals,
)
from virialpy.workflows import run_potential_comparison_workflow, summarize_fit_results


def main() -> None:
    """Run the Ar2 potential comparison example."""
    models = [
        {
            "name": "lj",
            "label": "Lennard-Jones",
            "initial_guess": [0.25, 3.5],
            "parameter_names": ["epsilon", "sigma"],
        },
        {
            "name": "ilj",
            "label": "Improved Lennard-Jones",
            "initial_guess": [0.25, 3.8, 8.0],
            "parameter_names": ["de", "req", "beta"],
        },
        {
            "name": "ryd6",
            "label": "Rydberg 6",
            "initial_guess": [0.25, 3.8, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "parameter_names": ["de", "re", "c1", "c2", "c3", "c4", "c5", "c6"],
        },
    ]

    results = run_potential_comparison_workflow(
        data_path="data/raw/ar2/ar2_cep_bsse.csv",
        models=models,
        r_column="r(angstrom)",
        energy_column="E_int_CP(kcal/mol)",
        results_dir="data/results/ar2/",
        figures_dir=None,
    )

    xlabel = r"$r$ / $\AA$"
    ylabel = r"$E_{\mathrm{int}}^{\mathrm{CP}}$ / kcal mol$^{-1}$"
    residual_ylabel = r"$E_{\mathrm{obs}} - E_{\mathrm{fit}}$ / kcal mol$^{-1}$"
    title_names = {
        "lj": "Lennard-Jones",
        "ilj": "Improved Lennard-Jones",
        "ryd6": "Rydberg 6",
    }

    for model_name, result in results.items():
        title_name = title_names[model_name]
        plot_fit_result(
            result,
            output_path=f"outputs/figures/ar2/fit/{model_name}_fit.png",
            title=rf"Ajuste {title_name} para Ar$_2$",
            xlabel=xlabel,
            ylabel=ylabel,
        )
        plot_fit_residuals(
            result,
            output_path=f"outputs/figures/ar2/fit/{model_name}_residuals.png",
            title=rf"Resíduos {title_name} para Ar$_2$",
            xlabel=xlabel,
            ylabel=residual_ylabel,
        )
        plot_fit_diagnostics(
            result,
            output_path=f"outputs/figures/ar2/fit/{model_name}_diagnostics.png",
            title=rf"Diagnóstico {title_name} para Ar$_2$",
            xlabel=xlabel,
            ylabel=ylabel,
        )

    plot_multiple_fits(
        results,
        output_path="outputs/figures/ar2/fit/comparison_fits.png",
        title=r"Comparação dos ajustes LJ, ILJ e Rydberg 6 para Ar$_2$",
        xlabel=xlabel,
        ylabel=ylabel,
    )
    plot_multiple_residuals(
        results,
        output_path="outputs/figures/ar2/fit/comparison_residuals.png",
        title=r"Comparação dos resíduos LJ, ILJ e Rydberg 6 para Ar$_2$",
        xlabel=xlabel,
        ylabel=residual_ylabel,
    )
    plot_comparison_diagnostics(
        results,
        output_path="outputs/figures/ar2/fit/comparison_diagnostics.png",
        title=r"Diagnóstico comparativo dos ajustes para Ar$_2$",
        xlabel=xlabel,
        ylabel=ylabel,
        residual_ylabel=residual_ylabel,
    )

    print(summarize_fit_results(results).to_string(index=False))


if __name__ == "__main__":
    main()
