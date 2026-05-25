import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.figure import Figure

from virialpy.plotting import plot_b2_comparison, plot_b2_metrics, plot_b2_residuals


def _comparison_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "temperature": [100.0, 200.0, 100.0, 200.0],
            "b2_exp": [-100.0, -50.0, -100.0, -50.0],
            "b2_calc": [-95.0, -45.0, -90.0, -55.0],
            "residual": [5.0, 5.0, 10.0, -5.0],
            "potential": ["lj", "lj", "ilj", "ilj"],
            "integrator": ["scipy_quad", "scipy_quad", "scipy_quad", "scipy_quad"],
        }
    )


def _metrics_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "potential": ["lj", "ilj"],
            "integrator": ["scipy_quad", "scipy_quad"],
            "mae": [5.0, 7.5],
            "rmse": [5.0, 7.9],
            "max_error": [5.0, 10.0],
            "mape": [7.5, 12.5],
            "r2": [0.9, 0.8],
        }
    )


def test_plot_b2_comparison_returns_figure() -> None:
    fig = plot_b2_comparison(_comparison_df(), integrator="scipy_quad")

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_b2_residuals_returns_figure() -> None:
    fig = plot_b2_residuals(_comparison_df(), integrator="scipy_quad")

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_b2_metrics_returns_figure() -> None:
    fig = plot_b2_metrics(_metrics_df(), metric="rmse")

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_b2_plot_functions_save_files_when_output_path_is_provided(tmp_path) -> None:
    paths = [
        tmp_path / "comparison.png",
        tmp_path / "residuals.png",
        tmp_path / "metrics.png",
    ]

    figures = [
        plot_b2_comparison(_comparison_df(), output_path=paths[0], integrator="scipy_quad"),
        plot_b2_residuals(_comparison_df(), output_path=paths[1], integrator="scipy_quad"),
        plot_b2_metrics(_metrics_df(), output_path=paths[2], metric="rmse"),
    ]

    assert all(path.exists() for path in paths)
    for fig in figures:
        plt.close(fig)


def test_b2_plot_functions_create_missing_parent_directories(tmp_path) -> None:
    output_path = tmp_path / "outputs" / "figures" / "ar2" / "b2" / "comparison.png"

    fig = plot_b2_comparison(_comparison_df(), output_path=output_path, integrator="scipy_quad")

    assert output_path.exists()
    plt.close(fig)


def test_plot_b2_metrics_creates_missing_parent_directories(tmp_path) -> None:
    output_path = tmp_path / "outputs" / "figures" / "ar2" / "b2" / "metrics.png"

    fig = plot_b2_metrics(_metrics_df(), metric="rmse", output_path=output_path)

    assert output_path.exists()
    plt.close(fig)


def test_plot_b2_metrics_raises_error_for_missing_metric() -> None:
    with pytest.raises(ValueError, match="Missing required column"):
        plot_b2_metrics(_metrics_df(), metric="median_error")
