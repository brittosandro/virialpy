import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from virialpy.plotting import (
    plot_final_b2_comparison,
    plot_final_b2_residuals,
    plot_final_method_comparison,
    plot_final_metric_ranking,
)


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


def _method_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "temperature": [100.0, 200.0, 100.0, 200.0],
            "b2_exp": [-100.0, -50.0, -100.0, -50.0],
            "b2_calc": [-95.0, -45.0, -91.0, -48.0],
            "potential": ["lj", "lj", "lj", "lj"],
            "method": ["direct", "direct", "partitioned", "partitioned"],
        }
    )


def _metrics_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "potential": ["lj", "ilj"],
            "integrator": ["scipy_quad", "scipy_quad"],
            "mae": [5.0, 7.5],
            "rmse": [5.0, 7.9],
        }
    )


def test_plot_final_b2_comparison_returns_figure() -> None:
    fig = plot_final_b2_comparison(_comparison_df())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_final_b2_residuals_returns_figure() -> None:
    fig = plot_final_b2_residuals(_comparison_df())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_final_metric_ranking_returns_figure() -> None:
    fig = plot_final_metric_ranking(_metrics_df())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_final_method_comparison_returns_figure() -> None:
    fig = plot_final_method_comparison(_method_df())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_final_plot_functions_save_files_when_output_path_is_provided(tmp_path) -> None:
    paths = [
        tmp_path / "comparison.png",
        tmp_path / "residuals.png",
        tmp_path / "ranking.png",
        tmp_path / "methods.png",
    ]

    figures = [
        plot_final_b2_comparison(_comparison_df(), output_path=paths[0]),
        plot_final_b2_residuals(_comparison_df(), output_path=paths[1]),
        plot_final_metric_ranking(_metrics_df(), output_path=paths[2]),
        plot_final_method_comparison(_method_df(), output_path=paths[3]),
    ]

    assert all(path.exists() for path in paths)
    for fig in figures:
        plt.close(fig)


def test_final_plot_functions_create_missing_parent_directories(tmp_path) -> None:
    output = tmp_path / "outputs" / "figures" / "ar2" / "final" / "comparison.png"

    fig = plot_final_b2_comparison(_comparison_df(), output_path=output)

    assert output.exists()
    plt.close(fig)

