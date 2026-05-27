from pathlib import Path


def test_streamlit_app_file_exists() -> None:
    assert Path("app/streamlit_app.py").exists()


def test_streamlit_app_readme_exists() -> None:
    assert Path("app/README.md").exists()


def test_streamlit_helpers_file_exists() -> None:
    assert Path("app/helpers.py").exists()


def test_streamlit_interactive_plots_file_exists() -> None:
    assert Path("app/interactive_plots.py").exists()


def test_streamlit_app_references_run_from_config() -> None:
    content = Path("app/streamlit_app.py").read_text(encoding="utf-8")

    assert "run_from_config" in content


def test_streamlit_app_references_streamlit() -> None:
    content = Path("app/streamlit_app.py").read_text(encoding="utf-8")

    assert "streamlit" in content


def test_streamlit_app_contains_new_system_mode() -> None:
    content = Path("app/streamlit_app.py").read_text(encoding="utf-8")

    assert "New system from CSV" in content
    assert "file_uploader" in content


def test_streamlit_app_contains_sequential_workflow_labels() -> None:
    content = Path("app/streamlit_app.py").read_text(encoding="utf-8")

    for text in [
        "Workflow status",
        "Data setup",
        "Fit potentials",
        "Inspect fit quality",
        "Compute B2",
        "Validate against experiment",
        "Advanced methods",
        "Final outputs",
        "Final results summary",
        "Download results",
        "Interactive final visualizations",
        "download_button",
        "key_prefix",
        "csv_final_report_tables",
        "csv_final_raw_outputs",
        "csv_final_yaml",
        "Calculation parameters",
        "Interactive B2(T) calculation preview",
        "plotly_chart",
        "plotly_b2_by_integrator",
        "plotly_b2_comparison",
        "plotly_b2_residuals",
        "plotly_method_comparison",
        "plotly_monte_carlo_difference",
        "Interactive visualization",
        "Static exported figures",
        "display_b2_validation_interactive",
        "display_method_comparison_interactive",
        "display_monte_carlo_interactive",
        "Interactive fit visualization",
        "plotly_fit_curves",
        "plotly_fit_residuals",
        "plotly_fit_observed_vs_predicted",
        "plotly_fit_metric_ranking",
        "Static exported fit figures",
        "csv_fit_curves_",
        "csv_fit_residuals_",
        "csv_fit_obs_pred_",
        'width="stretch"',
        "key=",
        "st.session_state",
        "Run fitting",
        "Compute B2(T)",
        "Validate B2(T)",
    ]:
        assert text in content

    for old_section in [
        "Results files",
        "Figure files",
        "Report table files",
        "Advanced: technical file paths",
        "Show technical paths",
        "Generated file paths",
        "Output paths",
        'st.code(f"results_dir =',
        'st.code(f"figures_dir =',
        'st.code(f"reports_dir =',
    ]:
        assert old_section not in content


def test_streamlit_plotly_charts_have_keys() -> None:
    content = Path("app/streamlit_app.py").read_text(encoding="utf-8")
    lines = content.splitlines()

    plotly_lines = [index for index, line in enumerate(lines) if "st.plotly_chart(" in line]
    assert plotly_lines
    assert "use_container_width" not in content
    for index in plotly_lines:
        call_body = "\n".join(lines[index : index + 8])
        assert "key=" in call_body
        assert 'width="stretch"' in call_body
