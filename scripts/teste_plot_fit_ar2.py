"""Fit Lennard-Jones to Ar2 data and save diagnostic plots."""

from __future__ import annotations

import numpy as np

from virialpy.plotting import plot_fit_diagnostics, plot_fit_residuals, plot_fit_result
from virialpy.workflows import run_fit_workflow


def main() -> None:
    """Run the Ar2 Lennard-Jones fitting and plotting example."""
    result = run_fit_workflow(
        data_path="data/raw/ar2/ar2_cep_bsse.csv",
        potential_name="lj",
        initial_guess=[0.25, 3.4],
        parameter_names=["epsilon", "sigma"],
        r_column="r(angstrom)",
        energy_column="E_int_CP(kcal/mol)",
        bounds=([0.0, 0.0], [np.inf, np.inf]),
        output_dir="data/results/ar2/lj/",
    )

    plot_fit_result(
        result,
        output_path="outputs/figures/ar2/fit/lj_fit.png",
        title=r"Ajuste do potencial de Lennard-Jones para Ar$_2$",
        xlabel=r"$r$ / \AA",
        ylabel=r"$E_{\mathrm{int}}^{\mathrm{CP}}$ / kcal mol$^{-1}$",
    )

    plot_fit_residuals(
        result,
        output_path="outputs/figures/ar2/fit/lj_residuals.png",
        title=r"Resíduos do ajuste Lennard-Jones para Ar$_2$",
        xlabel=r"$r$ / \AA",
        ylabel=r"$E_{\mathrm{obs}} - E_{\mathrm{fit}}$ / kcal mol$^{-1}$",
    )

    plot_fit_diagnostics(
        result,
        output_path="outputs/figures/ar2/fit/lj_diagnostics.png",
        title=r"Diagnóstico do ajuste Lennard-Jones para Ar$_2$",
        xlabel=r"$r$ / \AA",
        ylabel=r"$E_{\mathrm{int}}^{\mathrm{CP}}$ / kcal mol$^{-1}$",
    )


if __name__ == "__main__":
    main()
