"""Streamlit interface for virialpy YAML workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from virialpy.config import load_config
from virialpy.workflows import run_from_config


DEFAULT_CONFIGS = ["configs/ar2.yaml", "configs/kr2.yaml"]


def _selected_config_path() -> Path:
    """Return the selected or manually provided YAML path."""
    selected = st.sidebar.selectbox("YAML configuration", DEFAULT_CONFIGS)
    manual_path = st.sidebar.text_input("Manual YAML path", value="")
    return Path(manual_path.strip() or selected)


def _output_paths(config: dict[str, Any]) -> tuple[Path, Path, Path]:
    """Extract output directories from a loaded config."""
    outputs = config.get("outputs", {})
    return (
        Path(outputs.get("results_dir", "")),
        Path(outputs.get("figures_dir", "")),
        Path(outputs.get("reports_dir", "")),
    )


def _config_summary(config: dict[str, Any]) -> pd.DataFrame:
    """Build a compact configuration summary table."""
    data = config.get("data", {})
    models = config.get("models", {})
    integrators = config.get("integrators", {})
    units = config.get("units", {})
    outputs = config.get("outputs", {})
    rows = {
        "system": config.get("system", ""),
        "potential_data": data.get("potential_data", ""),
        "experimental_data": data.get("experimental_data", ""),
        "potentials": ", ".join(map(str, models.get("potentials", []))),
        "integrators": ", ".join(map(str, integrators.get("names", []))),
        "distance_unit": units.get("distance_unit", ""),
        "energy_unit": units.get("energy_unit", ""),
        "results_dir": outputs.get("results_dir", ""),
        "figures_dir": outputs.get("figures_dir", ""),
        "reports_dir": outputs.get("reports_dir", ""),
    }
    return pd.DataFrame(rows.items(), columns=["Field", "Value"])


def _show_table(path: Path, title: str) -> None:
    """Show a CSV table when it exists."""
    st.subheader(title)
    if path.exists():
        st.dataframe(pd.read_csv(path), use_container_width=True)
        st.caption(str(path))
    else:
        st.info(f"Table not found: {path}")


def _show_image(path: Path, title: str) -> None:
    """Show an image when it exists."""
    st.subheader(title)
    if path.exists():
        st.image(str(path), caption=str(path), use_container_width=True)
    else:
        st.info(f"Figure not found: {path}")


def _list_files(path: Path, title: str) -> None:
    """List files from a directory when it exists."""
    st.subheader(title)
    if not path.exists():
        st.info(f"Directory not found: {path}")
        return
    files = sorted(file for file in path.iterdir() if file.is_file())
    if not files:
        st.info(f"No files found in: {path}")
        return
    for file in files:
        st.code(str(file), language="text")


def _run_pipeline(config_path: Path) -> None:
    """Run a YAML pipeline with Streamlit status messages."""
    with st.status("Running virialpy pipeline...", expanded=True) as status:
        st.write(f"Configuration: `{config_path}`")
        outputs = run_from_config(config_path)
        st.write(f"Results: `{outputs['results_dir']}`")
        status.update(label="Pipeline completed.", state="complete")


def main() -> None:
    """Render the Streamlit application."""
    st.set_page_config(page_title="virialpy", layout="wide")
    st.title("virialpy — Second Virial Coefficient Workflow")
    st.write(
        "Aplicação para ajustar potenciais intermoleculares, calcular B2(T), "
        "validar contra dados experimentais e visualizar resultados."
    )

    st.sidebar.header("Workflow")
    config_path = _selected_config_path()
    run_pipeline = st.sidebar.button("Run pipeline", type="primary")

    try:
        config = load_config(config_path)
    except Exception as exc:
        st.error(f"Could not load YAML configuration: {exc}")
        return

    results_dir, figures_dir, reports_dir = _output_paths(config)

    if run_pipeline:
        try:
            _run_pipeline(config_path)
            st.success("Pipeline finished successfully.")
            config = load_config(config_path)
            results_dir, figures_dir, reports_dir = _output_paths(config)
        except Exception as exc:
            st.error(f"Pipeline failed: {exc}")

    overview, fit, b2_validation, methods, monte_carlo, final_outputs = st.tabs(
        [
            "Overview",
            "Fit results",
            "B2 validation",
            "Direct vs partitioned",
            "Monte Carlo",
            "Final outputs",
        ]
    )

    with overview:
        st.header("Configuration Summary")
        st.dataframe(_config_summary(config), use_container_width=True)
        st.subheader("Output Paths")
        st.code(f"results_dir = {results_dir}", language="text")
        st.code(f"figures_dir = {figures_dir}", language="text")
        st.code(f"reports_dir = {reports_dir}", language="text")

    with fit:
        _show_table(results_dir / "fit_comparison_metrics.csv", "Fit comparison metrics")
        fit_dir = figures_dir / "fit"
        for figure_name in [
            "comparison_fits.png",
            "comparison_residuals.png",
            "comparison_diagnostics.png",
        ]:
            if (fit_dir / figure_name).exists():
                _show_image(fit_dir / figure_name, figure_name)
        if not fit_dir.exists():
            st.info(f"Fit figure directory not found: {fit_dir}")

    with b2_validation:
        _show_table(results_dir / "b2_experiment_metrics.csv", "B(T) experiment metrics")
        final_dir = figures_dir / "final"
        _show_image(final_dir / "final_b2_comparison.png", "Final B(T) comparison")
        _show_image(final_dir / "final_b2_residuals.png", "Final B(T) residuals")
        _show_image(final_dir / "final_b2_rmse_ranking.png", "Final B(T) RMSE ranking")

    with methods:
        _show_table(
            results_dir / "b2_method_experiment_metrics.csv",
            "Direct vs partitioned metrics",
        )
        final_dir = figures_dir / "final"
        _show_image(final_dir / "final_b2_method_comparison.png", "Final method comparison")
        _show_image(
            final_dir / "final_b2_method_rmse_ranking.png",
            "Final method RMSE ranking",
        )

    with monte_carlo:
        _show_table(
            results_dir / "monte_carlo_comparison_summary.csv",
            "Monte Carlo comparison summary",
        )
        final_dir = figures_dir / "final"
        mc_dir = figures_dir / "monte_carlo"
        _show_image(
            final_dir / "final_mc_summary_mean_abs_difference.png",
            "Final Monte Carlo mean absolute difference",
        )
        _show_image(mc_dir / "mc_vs_scipy_quad.png", "Monte Carlo vs SciPy quad")
        _show_image(mc_dir / "mc_diff_scipy_quad.png", "Monte Carlo difference vs SciPy quad")

    with final_outputs:
        st.header("Final Outputs")
        tables_dir = reports_dir / "tables"
        _show_table(tables_dir / "fit_summary.csv", "Final fit summary")
        _show_table(tables_dir / "b2_metrics.csv", "Final B(T) metrics")
        _show_table(tables_dir / "b2_method_metrics.csv", "Final method metrics")
        _show_table(
            tables_dir / "monte_carlo_comparison_summary.csv",
            "Final Monte Carlo summary",
        )
        _list_files(figures_dir / "final", "Files in final figures directory")
        _list_files(tables_dir, "Files in report tables directory")


if __name__ == "__main__":
    main()
