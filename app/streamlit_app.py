"""Streamlit interface for virialpy YAML workflows."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd
import streamlit as st
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from app.interactive_plots import (
        plotly_b2_comparison,
        plotly_b2_by_integrator,
        plotly_b2_residuals,
        plotly_fit_curves,
        plotly_fit_metric_ranking,
        plotly_fit_observed_vs_predicted,
        plotly_fit_residuals,
        plotly_metric_ranking,
        plotly_method_comparison,
        plotly_monte_carlo_difference,
    )
    from app.helpers import (
        b2_results_exist,
        build_fit_residuals_dataframe,
        build_fitted_curves_dataframe,
        build_yaml_config,
        dataframe_from_csv_if_exists,
        existing_fitted_potentials,
        existing_integrators_in_b2_results,
        fit_results_exist,
        read_file_bytes,
        list_files_safe,
        list_existing_figures,
        load_csv_preview,
        paths_for_system,
        safe_system_name,
        save_uploaded_file,
        save_yaml_config,
        summarize_output_availability,
        unique_downloads,
        validation_results_exist,
        workflow_step_status,
    )
except ModuleNotFoundError:
    from interactive_plots import (
        plotly_b2_comparison,
        plotly_b2_by_integrator,
        plotly_b2_residuals,
        plotly_fit_curves,
        plotly_fit_metric_ranking,
        plotly_fit_observed_vs_predicted,
        plotly_fit_residuals,
        plotly_metric_ranking,
        plotly_method_comparison,
        plotly_monte_carlo_difference,
    )
    from helpers import (
        b2_results_exist,
        build_fit_residuals_dataframe,
        build_fitted_curves_dataframe,
        build_yaml_config,
        dataframe_from_csv_if_exists,
        existing_fitted_potentials,
        existing_integrators_in_b2_results,
        fit_results_exist,
        read_file_bytes,
        list_files_safe,
        list_existing_figures,
        load_csv_preview,
        paths_for_system,
        safe_system_name,
        save_uploaded_file,
        save_yaml_config,
        summarize_output_availability,
        unique_downloads,
        validation_results_exist,
        workflow_step_status,
    )

from virialpy.config import load_config
from virialpy.datasets import load_potential_data
from virialpy.fitting import get_default_fit_settings
from virialpy.plotting import (
    plot_b2_comparison,
    plot_b2_metrics,
    plot_b2_residuals,
    plot_comparison_diagnostics,
    plot_multiple_fits,
    plot_multiple_residuals,
)
from virialpy.workflows import (
    load_model_parameters_from_results,
    load_temperatures_from_csv,
    run_b2_comparison_workflow,
    run_from_config,
    run_potential_comparison_workflow,
    summarize_fit_results,
    validate_b2_against_experiment,
)
from virialpy.cli.main import (
    _generate_general_monte_carlo_outputs,
    _model_references,
    create_integrators,
)


DEFAULT_CONFIGS = ["configs/ar2.yaml", "configs/kr2.yaml"]
POTENTIAL_OPTIONS = ["lj", "ilj", "ryd6"]
INTEGRATOR_OPTIONS = ["scipy_quad", "gaussian", "simpson", "trapezoid", "monte_carlo"]


def _init_session_state() -> None:
    defaults = {
        "system_name": "",
        "safe_system_name": "",
        "potential_data_path": None,
        "experimental_data_path": None,
        "r_column": "",
        "energy_column": "",
        "temperature_column": "",
        "b2_column": "",
        "selected_potentials": POTENTIAL_OPTIONS.copy(),
        "approved_potentials": POTENTIAL_OPTIONS.copy(),
        "selected_integrators": INTEGRATOR_OPTIONS.copy(),
        "distance_unit": "angstrom",
        "energy_unit": "kcal/mol",
        "r_min": 2.5,
        "r_max": 30.0,
        "enable_partitioned": True,
        "r1": 3.0,
        "r2": 4.0,
        "r3": 14.0,
        "r4": 30.0,
        "n_points_b2": 6,
        "n_points_b3": 10,
        "n_points_b4": 24,
        "results_dir": None,
        "figures_dir": None,
        "reports_dir": None,
        "data_ready": False,
        "fit_completed": False,
        "b2_completed": False,
        "validation_completed": False,
        "advanced_completed": False,
        "final_outputs_completed": False,
        "generated_config_path": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _output_paths(config: dict[str, Any]) -> tuple[Path, Path, Path]:
    outputs = config.get("outputs", {})
    return (
        Path(outputs.get("results_dir", "")),
        Path(outputs.get("figures_dir", "")),
        Path(outputs.get("reports_dir", "")),
    )


def _config_summary(config: dict[str, Any]) -> pd.DataFrame:
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
    st.subheader(title)
    if path.exists():
        st.dataframe(pd.read_csv(path), width="stretch")
        st.caption(str(path))
    else:
        st.info(f"Table not found: {path}")


def _show_image(path: Path, title: str) -> None:
    st.subheader(title)
    if path.exists():
        st.image(str(path), caption=str(path), width="stretch")
    else:
        st.info(f"Figure not found: {path}")


def _list_files(path: Path, title: str) -> None:
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


def display_fit_results_interactive(
    results_dir: Path,
    figures_dir: Path,
    key_prefix: str = "fit_results",
    potential_data_path: Path | None = None,
    r_column: str = "r",
    energy_column: str = "energy",
) -> None:
    """Display fit tables and figures with an interactive ranking."""
    metrics = dataframe_from_csv_if_exists(results_dir / "fit_comparison_metrics.csv")
    st.subheader("Tables")
    if metrics is not None:
        if "rmse" in metrics.columns:
            metrics = metrics.sort_values("rmse")
        st.dataframe(metrics, width="stretch")
        if "rmse" in metrics.columns:
            st.subheader("Interactive fit visualization")
            st.plotly_chart(
                plotly_fit_metric_ranking(metrics, metric="rmse"),
                width="stretch",
                key=f"{key_prefix}_rmse_ranking",
            )
    else:
        st.info("Fit comparison metrics were not found.")

    fitted = existing_fitted_potentials(results_dir)
    if potential_data_path is not None and fitted:
        try:
            potential_data = load_potential_data(
                potential_data_path,
                r_column=r_column,
                energy_column=energy_column,
            )
            fitted_curves = build_fitted_curves_dataframe(potential_data, results_dir, fitted)
            residuals = build_fit_residuals_dataframe(results_dir, fitted)
            st.plotly_chart(
                plotly_fit_curves(potential_data, fitted_curves),
                width="stretch",
                key=f"{key_prefix}_curves",
            )
            if residuals is not None:
                st.plotly_chart(
                    plotly_fit_residuals(residuals),
                    width="stretch",
                    key=f"{key_prefix}_residuals",
                )
                st.plotly_chart(
                    plotly_fit_observed_vs_predicted(residuals),
                    width="stretch",
                    key=f"{key_prefix}_observed_vs_predicted",
                )
        except Exception as exc:
            potential_data = None
            fitted_curves = None
            residuals = None
            st.info(f"Interactive fit curves are not available: {exc}")
    else:
        potential_data = None
        fitted_curves = None
        residuals = None

    with st.expander("Static exported fit figures"):
        for figure in ["comparison_fits.png", "comparison_residuals.png", "comparison_diagnostics.png"]:
            _show_image(figures_dir / "fit" / figure, figure)

    for potential in fitted:
        with st.expander(f"{potential} fit details"):
            st.markdown("### Interactive fit diagnostics")
            _show_table(results_dir / potential / "fit_parameters.csv", f"{potential} parameters")
            _show_table(results_dir / potential / "fit_metrics.csv", f"{potential} metrics")
            if potential_data is not None and fitted_curves is not None:
                st.plotly_chart(
                    plotly_fit_curves(potential_data, fitted_curves, potential=potential),
                    width="stretch",
                    key=f"{key_prefix}_curves_{potential}",  # csv_fit_curves_<potential>
                )
            else:
                st.info("Interactive fitted curve is not available for this potential.")
            if residuals is not None:
                st.plotly_chart(
                    plotly_fit_residuals(residuals, potential=potential),
                    width="stretch",
                    key=f"{key_prefix}_residuals_{potential}",  # csv_fit_residuals_<potential>
                )
                st.plotly_chart(
                    plotly_fit_observed_vs_predicted(residuals, potential=potential),
                    width="stretch",
                    key=f"{key_prefix}_obs_pred_{potential}",  # csv_fit_obs_pred_<potential>
                )
            else:
                st.info("Interactive residual diagnostics are not available for this potential.")
            with st.expander("Static exported figures"):
                _show_image(figures_dir / "fit" / f"{potential}_fit.png", f"{potential} fit")
                _show_image(figures_dir / "fit" / f"{potential}_residuals.png", f"{potential} residuals")
                _show_image(figures_dir / "fit" / f"{potential}_diagnostics.png", f"{potential} diagnostics")


def display_b2_validation_interactive(results_dir: Path, figures_dir: Path, key_prefix: str = "b2_validation") -> None:
    """Display B(T) validation outputs with Plotly and static exported figures."""
    comparison = dataframe_from_csv_if_exists(results_dir / "b2_experiment_comparison.csv")
    metrics = dataframe_from_csv_if_exists(results_dir / "b2_experiment_metrics.csv")
    st.subheader("Interactive visualization")
    if comparison is not None:
        st.plotly_chart(
            plotly_b2_comparison(comparison, integrator="scipy_quad"),
            width="stretch",
            key=f"{key_prefix}_comparison",
        )
        st.plotly_chart(
            plotly_b2_residuals(comparison, integrator="scipy_quad"),
            width="stretch",
            key=f"{key_prefix}_residuals",
        )
    else:
        st.info("B2 experiment comparison table not found.")
    if metrics is not None:
        st.plotly_chart(
            plotly_metric_ranking(metrics, metric="rmse"),
            width="stretch",
            key=f"{key_prefix}_rmse",
        )
        st.plotly_chart(
            plotly_metric_ranking(metrics, metric="mae"),
            width="stretch",
            key=f"{key_prefix}_mae",
        )

    st.subheader("Tables")
    if metrics is not None:
        if "rmse" in metrics.columns:
            metrics = metrics.sort_values("rmse")
        st.dataframe(metrics, width="stretch")
    if comparison is not None:
        st.dataframe(comparison.head(), width="stretch")

    with st.expander("Static exported figures"):
        c1, c2 = st.columns(2)
        with c1:
            _show_image(figures_dir / "b2" / "b2_comparison_scipy_quad.png", "B2 comparison")
            _show_image(figures_dir / "b2" / "b2_rmse_metrics.png", "RMSE metrics")
            _show_image(figures_dir / "final" / "final_b2_comparison.png", "Final B(T) comparison")
            _show_image(figures_dir / "final" / "final_b2_rmse_ranking.png", "Final B(T) RMSE ranking")
        with c2:
            _show_image(figures_dir / "b2" / "b2_residuals_scipy_quad.png", "B2 residuals")
            _show_image(figures_dir / "b2" / "b2_mae_metrics.png", "MAE metrics")
            _show_image(figures_dir / "final" / "final_b2_residuals.png", "Final B(T) residuals")


def display_method_comparison_interactive(results_dir: Path, figures_dir: Path, key_prefix: str = "method_comparison") -> None:
    """Display direct-vs-partitioned outputs with Plotly and static figures."""
    method_comparison = dataframe_from_csv_if_exists(results_dir / "b2_method_experiment_comparison.csv")
    method_metrics = dataframe_from_csv_if_exists(results_dir / "b2_method_experiment_metrics.csv")
    st.subheader("Direct vs partitioned interactive visualization")
    if method_comparison is not None:
        st.plotly_chart(
            plotly_method_comparison(method_comparison),
            width="stretch",
            key=f"{key_prefix}_curve",
        )
    else:
        st.info("Direct-vs-partitioned comparison table not found.")
    if method_metrics is not None:
        st.plotly_chart(
            plotly_metric_ranking(method_metrics, metric="rmse"),
            width="stretch",
            key=f"{key_prefix}_rmse",
        )
        st.plotly_chart(
            plotly_metric_ranking(method_metrics, metric="mae"),
            width="stretch",
            key=f"{key_prefix}_mae",
        )
        _show_table(results_dir / "b2_method_experiment_metrics.csv", "Direct vs partitioned metrics")

    with st.expander("Static exported figures"):
        for figure in [
            "b2_methods_vs_experiment.png",
            "b2_methods_residuals.png",
            "b2_methods_rmse.png",
            "b2_methods_mae.png",
            "partitioned_contributions_lj.png",
            "partitioned_contributions_ilj.png",
            "partitioned_contributions_ryd6.png",
        ]:
            _show_image(figures_dir / "b2_methods" / figure, figure)
        _show_image(figures_dir / "final" / "final_b2_method_comparison.png", "Final method comparison")
        _show_image(figures_dir / "final" / "final_b2_method_rmse_ranking.png", "Final method RMSE ranking")


def display_monte_carlo_interactive(results_dir: Path, figures_dir: Path, key_prefix: str = "monte_carlo") -> None:
    """Display Monte Carlo comparison outputs with Plotly and static figures."""
    mc_comparison = dataframe_from_csv_if_exists(results_dir / "monte_carlo_comparison.csv")
    mc_summary = dataframe_from_csv_if_exists(results_dir / "monte_carlo_comparison_summary.csv")
    st.subheader("Monte Carlo interactive visualization")
    if mc_comparison is not None:
        st.plotly_chart(
            plotly_monte_carlo_difference(mc_comparison, reference_integrator="scipy_quad"),
            width="stretch",
            key=f"{key_prefix}_difference_scipy",
        )
    else:
        st.info("Monte Carlo comparison table not found.")
    if mc_summary is not None:
        st.plotly_chart(
            plotly_metric_ranking(mc_summary, metric="mean_abs_difference"),
            width="stretch",
            key=f"{key_prefix}_mean_abs_difference",
        )
        st.plotly_chart(
            plotly_metric_ranking(mc_summary, metric="rmse_difference"),
            width="stretch",
            key=f"{key_prefix}_rmse_difference",
        )
        _show_table(results_dir / "monte_carlo_comparison_summary.csv", "Monte Carlo comparison summary")

    with st.expander("Static exported figures"):
        for figure in [
            "mc_vs_scipy_quad.png",
            "mc_vs_gaussian.png",
            "mc_vs_simpson.png",
            "mc_vs_trapezoid.png",
            "mc_diff_scipy_quad.png",
            "mc_diff_gaussian.png",
            "mc_diff_simpson.png",
            "mc_diff_trapezoid.png",
            "mc_summary_mean_abs_difference.png",
            "mc_summary_rmse_difference.png",
        ]:
            _show_image(figures_dir / "monte_carlo" / figure, figure)
        _show_image(figures_dir / "final" / "final_mc_summary_mean_abs_difference.png", "Final Monte Carlo mean absolute difference")


def display_final_outputs(results_dir: Path, figures_dir: Path, reports_dir: Path, key_prefix: str = "final_outputs") -> None:
    """Display final summaries, static figures and report tables."""
    config_path = st.session_state.get("generated_config_path")
    st.subheader("Final results summary")
    availability = summarize_output_availability(results_dir, figures_dir, reports_dir, config_path=config_path)
    columns = st.columns(3)
    for index, (label, available) in enumerate(availability.items()):
        with columns[index % 3]:
            if available:
                st.success(f"{label}: available")
            else:
                st.warning(f"{label}: not available yet")

    st.subheader("Interactive final visualizations")
    comparison = dataframe_from_csv_if_exists(results_dir / "b2_experiment_comparison.csv")
    b2_metrics = dataframe_from_csv_if_exists(results_dir / "b2_experiment_metrics.csv")
    method_comparison = dataframe_from_csv_if_exists(results_dir / "b2_method_experiment_comparison.csv")
    method_metrics = dataframe_from_csv_if_exists(results_dir / "b2_method_experiment_metrics.csv")
    mc_comparison = dataframe_from_csv_if_exists(results_dir / "monte_carlo_comparison.csv")
    mc_summary = dataframe_from_csv_if_exists(results_dir / "monte_carlo_comparison_summary.csv")
    if comparison is not None:
        st.plotly_chart(
            plotly_b2_comparison(comparison, integrator="scipy_quad"),
            width="stretch",
            key=f"{key_prefix}_final_b2_comparison_interactive",
        )
        st.plotly_chart(
            plotly_b2_residuals(comparison, integrator="scipy_quad"),
            width="stretch",
            key=f"{key_prefix}_final_b2_residuals_interactive",
        )
    if b2_metrics is not None and "rmse" in b2_metrics.columns:
        st.plotly_chart(
            plotly_metric_ranking(b2_metrics, metric="rmse"),
            width="stretch",
            key=f"{key_prefix}_final_b2_rmse_interactive",
        )
        st.plotly_chart(
            plotly_metric_ranking(b2_metrics, metric="mae"),
            width="stretch",
            key=f"{key_prefix}_final_b2_mae_interactive",
        )
    if method_comparison is not None:
        st.plotly_chart(
            plotly_method_comparison(method_comparison),
            width="stretch",
            key=f"{key_prefix}_final_method_comparison_interactive",
        )
    if method_metrics is not None and "rmse" in method_metrics.columns:
        st.plotly_chart(
            plotly_metric_ranking(method_metrics, metric="rmse"),
            width="stretch",
            key=f"{key_prefix}_final_method_rmse_interactive",
        )
        st.plotly_chart(
            plotly_metric_ranking(method_metrics, metric="mae"),
            width="stretch",
            key=f"{key_prefix}_final_method_mae_interactive",
        )
    if mc_comparison is not None:
        st.plotly_chart(
            plotly_monte_carlo_difference(mc_comparison, reference_integrator="scipy_quad"),
            width="stretch",
            key=f"{key_prefix}_final_mc_difference_interactive",
        )
    if mc_summary is not None and "mean_abs_difference" in mc_summary.columns:
        st.plotly_chart(
            plotly_metric_ranking(mc_summary, metric="mean_abs_difference"),
            width="stretch",
            key=f"{key_prefix}_final_mc_mean_abs_difference_interactive",
        )
        st.plotly_chart(
            plotly_metric_ranking(mc_summary, metric="rmse_difference"),
            width="stretch",
            key=f"{key_prefix}_final_mc_rmse_difference_interactive",
        )

    final_dir = figures_dir / "final"
    with st.expander("Static exported figures"):
        final_figures = list_existing_figures(final_dir)
        if final_figures:
            figure_columns = st.columns(2)
            for index, figure_path in enumerate(final_figures):
                with figure_columns[index % 2]:
                    st.image(str(figure_path), caption=figure_path.name, width="stretch")
        else:
            st.info("No final PNG figures were found yet.")

    st.subheader("Final tables")
    tables_dir = reports_dir / "tables"
    for table in ["fit_summary.csv", "b2_metrics.csv", "b2_method_metrics.csv", "monte_carlo_comparison_summary.csv"]:
        if (tables_dir / table).exists():
            _show_table(tables_dir / table, table)

    st.subheader("Download results")

    def _download_if_exists(path: Path, label: str, mime: str, download_key_prefix: str) -> None:
        content = read_file_bytes(path)
        if content is not None:
            safe_path = str(path).replace("/", "_").replace("\\", "_").replace(".", "_").replace(" ", "_")
            button_key = f"{key_prefix}_{download_key_prefix}_{safe_path}"
            st.download_button(label, content, file_name=path.name, mime=mime, key=button_key)

    download_columns = st.columns(2)
    report_downloads = [
        (tables_dir / "fit_summary.csv", "Download fit summary CSV", "text/csv"),
        (tables_dir / "b2_metrics.csv", "Download B2 metrics CSV", "text/csv"),
        (tables_dir / "b2_method_metrics.csv", "Download B2 method metrics CSV", "text/csv"),
        (tables_dir / "monte_carlo_comparison_summary.csv", "Download Monte Carlo summary CSV", "text/csv"),
        (tables_dir / "fit_summary.tex", "Download fit summary LaTeX", "text/plain"),
        (tables_dir / "b2_metrics.tex", "Download B2 metrics LaTeX", "text/plain"),
        (tables_dir / "b2_method_metrics.tex", "Download B2 method metrics LaTeX", "text/plain"),
        (tables_dir / "monte_carlo_comparison_summary.tex", "Download Monte Carlo summary LaTeX", "text/plain"),
    ]
    raw_downloads = [
        (results_dir / "fit_comparison_metrics.csv", "Download fit comparison metrics CSV", "text/csv"),
        (results_dir / "b2_comparison_all.csv", "Download B2 comparison all CSV", "text/csv"),
        (results_dir / "b2_experiment_metrics.csv", "Download B2 experiment metrics CSV", "text/csv"),
        (results_dir / "b2_method_experiment_metrics.csv", "Download B2 method metrics CSV", "text/csv"),
    ]
    if not (tables_dir / "monte_carlo_comparison_summary.csv").exists():
        raw_downloads.append((results_dir / "monte_carlo_comparison_summary.csv", "Download Monte Carlo comparison summary CSV", "text/csv"))
    yaml_downloads = []
    if config_path:
        yaml_downloads.append((Path(config_path), "Download generated YAML", "text/yaml"))
    with download_columns[0]:
        st.caption("Final report tables")
        for path, label, mime in unique_downloads(report_downloads):
            _download_if_exists(path, label, mime, "csv_final_report_tables")
    with download_columns[1]:
        st.caption("Raw workflow outputs")
        for path, label, mime in unique_downloads(raw_downloads):
            _download_if_exists(path, label, mime, "csv_final_raw_outputs")
        for path, label, mime in unique_downloads(yaml_downloads):
            _download_if_exists(path, label, mime, "csv_final_yaml")


def _status_icon(completed: bool, ready: bool = True) -> str:
    return "✅" if completed else ("⚠️" if ready else "⏳")


def _render_workflow_status() -> None:
    st.sidebar.divider()
    st.sidebar.subheader("Workflow status")
    data_ready = _data_ready()
    fit_ready = data_ready
    fitted = bool(st.session_state.fit_completed or existing_fitted_potentials(st.session_state.results_dir or ""))
    approved = list(st.session_state.approved_potentials or [])
    b2_ready = bool(approved and fitted)
    b2_done = bool(st.session_state.b2_completed or b2_results_exist(st.session_state.results_dir or ""))
    validation_done = bool(st.session_state.validation_completed or validation_results_exist(st.session_state.results_dir or ""))
    st.sidebar.write(f"{_status_icon(data_ready)} Data setup: {workflow_step_status(data_ready, True)}")
    st.sidebar.write(f"{_status_icon(fitted, fit_ready)} Fit potentials: {workflow_step_status(fitted, fit_ready)}")
    st.sidebar.write("Approved potentials: " + (", ".join(approved) if approved else "none"))
    st.sidebar.write(f"{_status_icon(b2_done, b2_ready)} B2 calculation: {workflow_step_status(b2_done, b2_ready)}")
    st.sidebar.write(f"{_status_icon(validation_done, b2_done)} Validation: {workflow_step_status(validation_done, b2_done)}")
    st.sidebar.write(f"{_status_icon(bool(st.session_state.advanced_completed), b2_done)} Advanced methods: {workflow_step_status(bool(st.session_state.advanced_completed), b2_done)}")
    st.sidebar.write(f"{_status_icon(bool(st.session_state.final_outputs_completed), validation_done)} Final outputs: {workflow_step_status(bool(st.session_state.final_outputs_completed), validation_done)}")


def _run_pipeline(config_path: Path) -> None:
    with st.status("Running virialpy pipeline...", expanded=True) as status:
        st.write(f"Configuration: `{config_path}`")
        outputs = run_from_config(config_path)
        st.write(f"Results: `{outputs['results_dir']}`")
        status.update(label="Pipeline completed.", state="complete")


def _existing_yaml_mode() -> None:
    selected = st.sidebar.selectbox("YAML configuration", DEFAULT_CONFIGS)
    manual_path = st.sidebar.text_input("Manual YAML path", value="")
    config_path = Path(manual_path.strip() or selected)
    try:
        config = load_config(config_path)
    except Exception as exc:
        st.error(f"Could not load YAML configuration: {exc}")
        return

    if st.sidebar.button("Run pipeline", type="primary"):
        try:
            _run_pipeline(config_path)
            st.success("Pipeline finished successfully.")
            config = load_config(config_path)
        except Exception as exc:
            st.error(f"Pipeline failed: {exc}")
    _render_results(config)


def _current_config(
    run_fit: bool = True,
    run_b2: bool = True,
    run_validate: bool = True,
    run_partitioned: bool = True,
    run_method_comparison: bool = True,
    run_monte_carlo_plots: bool = True,
    run_final_outputs: bool = True,
) -> dict[str, Any]:
    return build_yaml_config(
        system_name=st.session_state.safe_system_name or st.session_state.system_name,
        potential_data_path=Path(st.session_state.potential_data_path),
        experimental_data_path=Path(st.session_state.experimental_data_path),
        r_column=st.session_state.r_column,
        energy_column=st.session_state.energy_column,
        temperature_column=st.session_state.temperature_column,
        b2_column=st.session_state.b2_column,
        potentials=st.session_state.approved_potentials or st.session_state.selected_potentials,
        integrators=st.session_state.selected_integrators,
        distance_unit=st.session_state.distance_unit,
        energy_unit=st.session_state.energy_unit,
        r_min=float(st.session_state.r_min),
        r_max=float(st.session_state.r_max),
        enable_partitioned=bool(st.session_state.enable_partitioned),
        r1=float(st.session_state.r1),
        r2=float(st.session_state.r2),
        r3=float(st.session_state.r3),
        r4=float(st.session_state.r4),
        n_points_b2=int(st.session_state.n_points_b2),
        n_points_b3=int(st.session_state.n_points_b3),
        n_points_b4=int(st.session_state.n_points_b4),
        run_fit=run_fit,
        run_b2=run_b2,
        run_validate=run_validate,
        run_partitioned=run_partitioned,
        run_method_comparison=run_method_comparison,
        run_monte_carlo_plots=run_monte_carlo_plots,
        run_final_outputs=run_final_outputs,
    )


def _save_current_yaml(**run_flags: bool) -> Path:
    config = _current_config(**run_flags)
    config_path = save_yaml_config(config, Path(st.session_state.generated_config_path))
    return config_path


def _data_step() -> None:
    st.header("1. Data setup")
    st.info("Upload the theoretical potential and experimental B(T) CSV files, then choose the columns used by the workflow.")
    system_name = st.text_input("System name", value=st.session_state.system_name or "new_system")
    try:
        st.caption(f"Safe system name: `{safe_system_name(system_name)}`")
    except ValueError:
        st.warning("System name cannot be empty.")
    potential_file = st.file_uploader("Theoretical U(r) CSV", type=["csv"], key="potential_upload")
    experimental_file = st.file_uploader("Experimental B(T) CSV", type=["csv"], key="experimental_upload")

    potential_data = load_csv_preview(potential_file) if potential_file is not None else None
    experimental_data = load_csv_preview(experimental_file) if experimental_file is not None else None
    if potential_data is not None:
        st.subheader("Potential data preview")
        st.caption(f"{len(potential_data)} rows, {len(potential_data.columns)} columns")
        st.dataframe(potential_data.head(), width="stretch")
    if experimental_data is not None:
        st.subheader("Experimental data preview")
        st.caption(f"{len(experimental_data)} rows, {len(experimental_data.columns)} columns")
        st.dataframe(experimental_data.head(), width="stretch")
    st.divider()
    st.subheader("Calculation parameters")
    st.caption(
        "Choose the molecular potentials, numerical integrators, units and integration limits "
        "that will be used in the fitting and B2(T) calculation steps."
    )
    calc_col1, calc_col2 = st.columns(2)
    with calc_col1:
        selected_potentials = st.multiselect(
            "Potentials",
            POTENTIAL_OPTIONS,
            default=st.session_state.selected_potentials or POTENTIAL_OPTIONS,
            key="data_selected_potentials",
        )
        selected_integrators = st.multiselect(
            "Integrators",
            INTEGRATOR_OPTIONS,
            default=st.session_state.selected_integrators or INTEGRATOR_OPTIONS,
            key="data_selected_integrators",
        )
        distance_unit = st.selectbox(
            "distance_unit",
            ["angstrom", "pm", "meter"],
            index=["angstrom", "pm", "meter"].index(st.session_state.distance_unit),
            key="data_distance_unit",
        )
        energy_unit_options = ["kelvin", "kcal/mol", "kj/mol", "ev", "mev"]
        energy_unit = st.selectbox(
            "energy_unit",
            energy_unit_options,
            index=energy_unit_options.index(st.session_state.energy_unit),
            key="data_energy_unit",
        )
    with calc_col2:
        r_min = st.number_input("r_min", value=float(st.session_state.r_min), key="data_r_min")
        r_max = st.number_input("r_max", value=float(st.session_state.r_max), key="data_r_max")
        enable_partitioned = st.checkbox("Enable partitioned B2", value=bool(st.session_state.enable_partitioned), key="data_enable_partitioned")
        if enable_partitioned:
            p1, p2 = st.columns(2)
            with p1:
                r1 = st.number_input("r1", value=float(st.session_state.r1), key="data_r1")
                r2 = st.number_input("r2", value=float(st.session_state.r2), key="data_r2")
            with p2:
                r3 = st.number_input("r3", value=float(st.session_state.r3), key="data_r3")
                r4 = st.number_input("r4", value=float(st.session_state.r4), key="data_r4")
            n1, n2, n3 = st.columns(3)
            with n1:
                n_points_b2 = st.number_input("n_points_b2", min_value=1, value=int(st.session_state.n_points_b2), step=1, key="data_n_points_b2")
            with n2:
                n_points_b3 = st.number_input("n_points_b3", min_value=1, value=int(st.session_state.n_points_b3), step=1, key="data_n_points_b3")
            with n3:
                n_points_b4 = st.number_input("n_points_b4", min_value=1, value=int(st.session_state.n_points_b4), step=1, key="data_n_points_b4")
        else:
            r1, r2, r3, r4 = st.session_state.r1, st.session_state.r2, st.session_state.r3, st.session_state.r4
            n_points_b2, n_points_b3, n_points_b4 = st.session_state.n_points_b2, st.session_state.n_points_b3, st.session_state.n_points_b4

    if not selected_potentials:
        st.warning("Select at least one potential.")
    if not selected_integrators:
        st.warning("Select at least one integrator.")
    if r_max <= r_min:
        st.error("r_max must be greater than r_min.")
    if enable_partitioned and not (0 < float(r1) < float(r2) < float(r3) < float(r4)):
        st.error("Partitioned limits must obey 0 < r1 < r2 < r3 < r4.")

    if potential_data is None or experimental_data is None:
        st.info("Upload both CSV files to continue.")
        return
    if len(potential_data.columns) < 2:
        st.error("The theoretical CSV must contain at least two columns.")
        return
    if len(experimental_data.columns) < 2:
        st.error("The experimental CSV must contain at least two columns.")
        return

    col1, col2 = st.columns(2)
    with col1:
        r_column = st.selectbox("r_column", list(potential_data.columns))
        energy_default = 1 if len(potential_data.columns) > 1 else 0
        energy_column = st.selectbox("energy_column", list(potential_data.columns), index=energy_default)
    with col2:
        temperature_column = st.selectbox("temperature_column", list(experimental_data.columns))
        b2_default = 1 if len(experimental_data.columns) > 1 else 0
        b2_column = st.selectbox("b2_column", list(experimental_data.columns), index=b2_default)

    if r_column == energy_column:
        st.error("r_column and energy_column must be different.")
        return
    if temperature_column == b2_column:
        st.error("temperature_column and b2_column must be different.")
        return

    can_save = bool(selected_potentials and selected_integrators and r_max > r_min)
    can_save = can_save and (not enable_partitioned or (0 < float(r1) < float(r2) < float(r3) < float(r4)))
    if st.button("Save data setup", type="primary", disabled=not can_save):
        try:
            safe_name = safe_system_name(system_name)
            paths = paths_for_system(safe_name)
            potential_path = save_uploaded_file(potential_file, paths["raw_dir"])
            experimental_path = save_uploaded_file(experimental_file, paths["raw_dir"])
            paths["results_dir"].mkdir(parents=True, exist_ok=True)
            paths["figures_dir"].mkdir(parents=True, exist_ok=True)
            paths["reports_dir"].mkdir(parents=True, exist_ok=True)

            st.session_state.system_name = system_name
            st.session_state.safe_system_name = safe_name
            st.session_state.potential_data_path = str(potential_path)
            st.session_state.experimental_data_path = str(experimental_path)
            st.session_state.r_column = str(r_column)
            st.session_state.energy_column = str(energy_column)
            st.session_state.temperature_column = str(temperature_column)
            st.session_state.b2_column = str(b2_column)
            st.session_state.selected_potentials = list(selected_potentials)
            st.session_state.approved_potentials = list(selected_potentials)
            st.session_state.selected_integrators = list(selected_integrators)
            st.session_state.distance_unit = str(distance_unit)
            st.session_state.energy_unit = str(energy_unit)
            st.session_state.r_min = float(r_min)
            st.session_state.r_max = float(r_max)
            st.session_state.enable_partitioned = bool(enable_partitioned)
            st.session_state.r1 = float(r1)
            st.session_state.r2 = float(r2)
            st.session_state.r3 = float(r3)
            st.session_state.r4 = float(r4)
            st.session_state.n_points_b2 = int(n_points_b2)
            st.session_state.n_points_b3 = int(n_points_b3)
            st.session_state.n_points_b4 = int(n_points_b4)
            st.session_state.results_dir = str(paths["results_dir"])
            st.session_state.figures_dir = str(paths["figures_dir"])
            st.session_state.reports_dir = str(paths["reports_dir"])
            st.session_state.generated_config_path = str(paths["config_path"])
            st.session_state.data_ready = True
            st.session_state.fit_completed = False
            st.session_state.b2_completed = False
            st.session_state.validation_completed = False
            st.session_state.advanced_completed = False
            st.session_state.final_outputs_completed = False
            st.success(f"Data saved for {safe_name}.")
        except Exception as exc:
            st.error(f"Could not save data: {exc}")


def _data_ready() -> bool:
    required = [
        st.session_state.potential_data_path,
        st.session_state.experimental_data_path,
        st.session_state.r_column,
        st.session_state.energy_column,
        st.session_state.temperature_column,
        st.session_state.b2_column,
        st.session_state.results_dir,
        st.session_state.figures_dir,
        st.session_state.reports_dir,
    ]
    return bool(st.session_state.get("data_ready")) and all(required)


def _fit_step() -> None:
    st.header("2. Fit potentials")
    if not _data_ready():
        st.warning("Pending: complete Data setup first.")
        return
    st.caption("Default initial guesses are provided for convenience and can be refined in a future version.")
    select_all = st.checkbox("all potentials", value=True, key="fit_all_potentials")
    selected = st.multiselect(
        "Potentials",
        POTENTIAL_OPTIONS,
        default=POTENTIAL_OPTIONS if select_all else st.session_state.selected_potentials,
    )
    st.session_state.selected_potentials = selected

    st.subheader("Default initial guesses")
    settings = []
    for potential in selected:
        default = get_default_fit_settings(potential)
        settings.append(
            {
                "potential": potential,
                "parameter_names": ", ".join(default["parameter_names"]),
                "initial_guess": default["initial_guess"],
            }
    )
    st.dataframe(pd.DataFrame(settings), width="stretch")

    if st.button("Run fitting", type="primary", disabled=not selected):
        results = {}
        errors = {}
        fit_dir = Path(st.session_state.figures_dir) / "fit"
        for potential in selected:
            try:
                default = get_default_fit_settings(potential)
                model = {
                    "name": potential,
                    "label": _model_references([potential])[0]["label"],
                    "initial_guess": default["initial_guess"],
                    "parameter_names": default["parameter_names"],
                }
                partial = run_potential_comparison_workflow(
                    data_path=Path(st.session_state.potential_data_path),
                    models=[model],
                    r_column=st.session_state.r_column,
                    energy_column=st.session_state.energy_column,
                    results_dir=Path(st.session_state.results_dir),
                    figures_dir=fit_dir,
                )
                results.update(partial)
            except Exception as exc:
                errors[potential] = str(exc)

        if results:
            summarize_fit_results(results).to_csv(
                Path(st.session_state.results_dir) / "fit_comparison_metrics.csv",
                index=False,
            )
            plot_multiple_fits(results, output_path=fit_dir / "comparison_fits.png")
            plot_multiple_residuals(results, output_path=fit_dir / "comparison_residuals.png")
            plot_comparison_diagnostics(results, output_path=fit_dir / "comparison_diagnostics.png")
            st.session_state.fit_completed = True
            st.session_state.approved_potentials = list(results.keys())
            st.success("Potential fitting completed.")
            _show_table(Path(st.session_state.results_dir) / "fit_comparison_metrics.csv", "Fit comparison metrics")
        if errors:
            for potential, message in errors.items():
                st.error(f"{potential} fitting failed: {message}")
        if not results:
            st.session_state.fit_completed = False
            st.error("No potential was fitted successfully.")


def _inspect_fit_step() -> None:
    st.header("3. Inspect fit quality")
    if not _data_ready():
        st.warning("Pending: complete Data setup first.")
        return
    results_dir = Path(st.session_state.results_dir)
    figures_dir = Path(st.session_state.figures_dir)
    fitted = existing_fitted_potentials(results_dir)
    if not st.session_state.fit_completed and not fitted:
        st.warning("Run potential fitting first.")
        return

    display_fit_results_interactive(
        results_dir,
        figures_dir,
        key_prefix="csv_fit",
        potential_data_path=Path(st.session_state.potential_data_path),
        r_column=st.session_state.r_column,
        energy_column=st.session_state.energy_column,
    )

    approved = st.multiselect(
        "Use these potentials for B2 calculation",
        fitted,
        default=[p for p in (st.session_state.approved_potentials or fitted) if p in fitted],
    )
    st.session_state.approved_potentials = approved
    if not approved:
        st.warning("Select at least one fitted potential before computing B2(T).")


def _compute_b2_step() -> None:
    st.header("4. Compute B2(T)")
    if not _data_ready():
        st.warning("Pending: complete Data setup first.")
        return
    approved = st.session_state.approved_potentials or st.session_state.selected_potentials
    if not approved:
        st.warning("Select approved fitted potentials in Inspect fit quality first.")
        return
    if not fit_results_exist(st.session_state.results_dir, approved):
        st.warning("Missing fit_parameters.csv for one or more approved potentials.")
        return

    select_all_integrators = st.checkbox("all integrators", value=True, key="b2_all_integrators")
    integrators = st.multiselect(
        "Integrators",
        INTEGRATOR_OPTIONS,
        default=INTEGRATOR_OPTIONS if select_all_integrators else st.session_state.selected_integrators,
    )
    col1, col2 = st.columns(2)
    with col1:
        distance_unit = st.selectbox("distance_unit", ["angstrom", "pm", "meter"], index=0)
        r_min = st.number_input("r_min", value=float(st.session_state.r_min))
        r_max = st.number_input("r_max", value=float(st.session_state.r_max))
    with col2:
        energy_unit = st.selectbox("energy_unit", ["kelvin", "kcal/mol", "kj/mol", "ev", "mev"], index=1)

    if r_max <= r_min:
        st.error("r_max must be greater than r_min.")
        return
    if not integrators:
        st.error("Select at least one integrator.")
        return
    experimental_columns = pd.read_csv(st.session_state.experimental_data_path, nrows=0).columns
    if st.session_state.temperature_column not in experimental_columns:
        st.error("The selected temperature column was not found in the experimental CSV.")
        return

    st.session_state.selected_integrators = integrators
    st.session_state.distance_unit = distance_unit
    st.session_state.energy_unit = energy_unit
    st.session_state.r_min = float(r_min)
    st.session_state.r_max = float(r_max)

    if st.button("Compute B2(T)", type="primary", disabled=not integrators):
        try:
            temperatures = load_temperatures_from_csv(
                st.session_state.experimental_data_path,
                temperature_column=st.session_state.temperature_column,
            )
            models = load_model_parameters_from_results(
                st.session_state.results_dir,
                _model_references(approved),
            )
            run_b2_comparison_workflow(
                models=models,
                temperatures=temperatures,
                integrators=create_integrators(integrators),
                r_min=float(r_min),
                r_max=float(r_max),
                distance_unit=distance_unit,
                energy_unit=energy_unit,
                output_path=Path(st.session_state.results_dir) / "b2_comparison_all.csv",
            )
            st.session_state.b2_completed = True
            st.success("B2 calculation completed.")
            st.caption("Used potentials: " + ", ".join(approved))
            st.caption("Used integrators: " + ", ".join(integrators))
        except Exception as exc:
            st.error(f"B2 calculation failed: {exc}")
    b2_data = dataframe_from_csv_if_exists(Path(st.session_state.results_dir) / "b2_comparison_all.csv")
    if b2_data is not None:
        st.subheader("Interactive B2(T) calculation preview")
        st.plotly_chart(
            plotly_b2_by_integrator(b2_data),
            width="stretch",
            key="csv_b2_calculation_preview",
        )
        st.subheader("B2 calculation preview")
        st.dataframe(b2_data.head(), width="stretch")


def _validate_b2_step() -> None:
    st.header("5. Validate against experiment")
    if not _data_ready():
        st.warning("Pending: complete Data setup first.")
        return
    results_dir = Path(st.session_state.results_dir)
    figures_dir = Path(st.session_state.figures_dir)
    if not b2_results_exist(results_dir):
        st.warning("Compute B2(T) first.")
        return

    if st.button("Validate B2(T)", type="primary"):
        try:
            comparison, metrics = validate_b2_against_experiment(
                calculated_path=results_dir / "b2_comparison_all.csv",
                experimental_path=st.session_state.experimental_data_path,
                temperature_column_exp=st.session_state.temperature_column,
                b2_column_exp=st.session_state.b2_column,
                group_columns=("potential", "integrator"),
                output_comparison_path=results_dir / "b2_experiment_comparison.csv",
                output_metrics_path=results_dir / "b2_experiment_metrics.csv",
            )
            b2_dir = figures_dir / "b2"
            plot_b2_comparison(comparison, output_path=b2_dir / "b2_comparison_scipy_quad.png", integrator="scipy_quad")
            plot_b2_residuals(comparison, output_path=b2_dir / "b2_residuals_scipy_quad.png", integrator="scipy_quad")
            plot_b2_metrics(metrics, metric="rmse", output_path=b2_dir / "b2_rmse_metrics.png", xlabel=r"Erro / cm$^3$ mol$^{-1}$")
            plot_b2_metrics(metrics, metric="mae", output_path=b2_dir / "b2_mae_metrics.png", xlabel=r"Erro / cm$^3$ mol$^{-1}$")
            b2_data = pd.read_csv(results_dir / "b2_comparison_all.csv")
            if "monte_carlo" in set(b2_data["integrator"]):
                _generate_general_monte_carlo_outputs(
                    system=st.session_state.safe_system_name,
                    results_dir=results_dir,
                    figures_dir=figures_dir,
                )
            st.session_state.validation_completed = True
            st.success("Validation completed.")
        except Exception as exc:
            st.error(f"Validation failed: {exc}")

    if validation_results_exist(results_dir):
        display_b2_validation_interactive(results_dir, figures_dir, key_prefix="csv_b2_validation")


def _partitioned_controls() -> tuple[bool, bool, bool, bool]:
    st.session_state.enable_partitioned = st.checkbox("Enable partitioned B2", value=bool(st.session_state.enable_partitioned))
    run_partitioned = st.session_state.enable_partitioned
    run_method_comparison = st.checkbox("Compare direct vs partitioned", value=True)
    run_monte_carlo_plots = st.checkbox("Generate Monte Carlo comparison plots", value=True)
    if st.session_state.enable_partitioned:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.session_state.r1 = st.number_input("r1", value=float(st.session_state.r1))
        with c2:
            st.session_state.r2 = st.number_input("r2", value=float(st.session_state.r2))
        with c3:
            st.session_state.r3 = st.number_input("r3", value=float(st.session_state.r3))
        with c4:
            st.session_state.r4 = st.number_input("r4", value=float(st.session_state.r4))
        if not (0 < float(st.session_state.r1) < float(st.session_state.r2) < float(st.session_state.r3) < float(st.session_state.r4)):
            st.error("Partitioned limits must obey 0 < r1 < r2 < r3 < r4.")
            return run_partitioned, run_method_comparison, run_monte_carlo_plots, False
        g1, g2, g3 = st.columns(3)
        with g1:
            st.session_state.n_points_b2 = st.number_input("n_points_b2", min_value=1, value=int(st.session_state.n_points_b2), step=1)
        with g2:
            st.session_state.n_points_b3 = st.number_input("n_points_b3", min_value=1, value=int(st.session_state.n_points_b3), step=1)
        with g3:
            st.session_state.n_points_b4 = st.number_input("n_points_b4", min_value=1, value=int(st.session_state.n_points_b4), step=1)
    return run_partitioned, run_method_comparison, run_monte_carlo_plots, True


def _advanced_methods_step() -> None:
    st.header("6. Advanced methods")
    if not _data_ready():
        st.warning("Pending: complete Data setup first.")
        return
    if not b2_results_exist(st.session_state.results_dir):
        st.warning("Compute B2(T) before running advanced methods.")
        return
    st.info("Optional methods use the existing workflow code: partitioned B(T), direct-vs-partitioned comparison, and Monte Carlo diagnostics.")

    run_partitioned, run_method_comparison, run_monte_carlo_plots, limits_ok = _partitioned_controls()

    if st.button("Run advanced methods", type="primary", disabled=not limits_ok):
        try:
            config_path = _save_current_yaml(
                run_fit=False,
                run_b2=False,
                run_validate=False,
                run_partitioned=run_partitioned,
                run_method_comparison=run_method_comparison,
                run_monte_carlo_plots=run_monte_carlo_plots,
                run_final_outputs=False,
            )
            run_from_config(config_path)
            st.session_state.advanced_completed = True
            st.success("Advanced methods completed.")
        except Exception as exc:
            st.error(f"Advanced methods failed: {exc}")

    results_dir = Path(st.session_state.results_dir)
    figures_dir = Path(st.session_state.figures_dir)
    if (results_dir / "b2_method_experiment_metrics.csv").exists():
        display_method_comparison_interactive(results_dir, figures_dir, key_prefix="csv_method_comparison")
    if (results_dir / "monte_carlo_comparison.csv").exists() or (results_dir / "monte_carlo_comparison_summary.csv").exists():
        display_monte_carlo_interactive(results_dir, figures_dir, key_prefix="csv_monte_carlo")


def _final_outputs_step() -> None:
    st.header("7. Final outputs")
    if not _data_ready():
        st.warning("Pending: complete Data setup first.")
        return
    if not validation_results_exist(st.session_state.results_dir):
        st.warning("Validate B2(T) before generating final publication outputs.")

    if st.button("Save YAML configuration"):
        try:
            config_path = _save_current_yaml(
                run_fit=False,
                run_b2=False,
                run_validate=False,
                run_partitioned=False,
                run_method_comparison=False,
                run_monte_carlo_plots=False,
                run_final_outputs=False,
            )
            st.session_state.generated_config_path = str(config_path)
            st.success(f"YAML saved to {config_path}")
            st.code(Path(config_path).read_text(encoding="utf-8"), language="yaml")
        except Exception as exc:
            st.error(f"Could not save YAML: {exc}")

    if st.button("Generate final figures and tables", type="primary"):
        try:
            config_path = _save_current_yaml(
                run_fit=False,
                run_b2=False,
                run_validate=False,
                run_partitioned=False,
                run_method_comparison=False,
                run_monte_carlo_plots=True,
                run_final_outputs=True,
            )
            run_from_config(config_path)
            st.session_state.final_outputs_completed = True
            st.success("Final figures and tables generated.")
        except Exception as exc:
            st.error(f"Could not generate final outputs: {exc}")

    display_final_outputs(
        Path(st.session_state.results_dir or ""),
        Path(st.session_state.figures_dir or ""),
        Path(st.session_state.reports_dir or ""),
        key_prefix="csv_final_outputs",
    )


def _new_system_mode() -> None:
    st.sidebar.caption("Sequential workflow from uploaded CSV files.")
    _render_workflow_status()
    tabs = st.tabs(
        [
            "1. Data setup",
            "2. Fit potentials",
            "3. Inspect fit quality",
            "4. Compute B2(T)",
            "5. Validate against experiment",
            "6. Advanced methods",
            "7. Final outputs",
        ]
    )
    with tabs[0]:
        _data_step()
    with tabs[1]:
        _fit_step()
    with tabs[2]:
        _inspect_fit_step()
    with tabs[3]:
        _compute_b2_step()
    with tabs[4]:
        _validate_b2_step()
    with tabs[5]:
        _advanced_methods_step()
    with tabs[6]:
        _final_outputs_step()


def _render_results(config: dict[str, Any]) -> None:
    results_dir, figures_dir, reports_dir = _output_paths(config)
    overview, fit, b2_validation, methods, monte_carlo, final_outputs = st.tabs(
        ["Overview", "Fit results", "B2 validation", "Direct vs partitioned", "Monte Carlo", "Final outputs"]
    )
    with overview:
        st.header("Configuration Summary")
        st.dataframe(_config_summary(config), width="stretch")
    with fit:
        data = config.get("data", {})
        display_fit_results_interactive(
            results_dir,
            figures_dir,
            key_prefix="yaml_fit",
            potential_data_path=Path(data["potential_data"]) if data.get("potential_data") else None,
            r_column=str(data.get("r_column", "r")),
            energy_column=str(data.get("energy_column", "energy")),
        )
    with b2_validation:
        display_b2_validation_interactive(results_dir, figures_dir, key_prefix="yaml_b2_validation")
    with methods:
        display_method_comparison_interactive(results_dir, figures_dir, key_prefix="yaml_method_comparison")
    with monte_carlo:
        display_monte_carlo_interactive(results_dir, figures_dir, key_prefix="yaml_monte_carlo")
    with final_outputs:
        display_final_outputs(results_dir, figures_dir, reports_dir, key_prefix="yaml_final_outputs")


def main() -> None:
    """Render the Streamlit application."""
    _init_session_state()
    st.set_page_config(page_title="virialpy", layout="wide")
    st.title("virialpy — Second Virial Coefficient Workflow")
    st.write(
        "Aplicação para ajustar potenciais intermoleculares, calcular B2(T), "
        "validar contra dados experimentais e visualizar resultados."
    )

    st.sidebar.header("Workflow")
    mode = st.sidebar.radio("Mode", ["Use existing YAML", "New system from CSV"])
    if mode == "Use existing YAML":
        _existing_yaml_mode()
    else:
        _new_system_mode()


if __name__ == "__main__":
    main()
