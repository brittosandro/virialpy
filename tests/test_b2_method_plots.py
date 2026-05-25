import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from virialpy.plotting import (
    plot_b2_method_metrics,
    plot_b2_method_residuals,
    plot_b2_methods_vs_experiment,
    plot_partitioned_contributions,
)


def _comparison_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "temperature": [100.0, 200.0, 100.0, 200.0],
            "b2_exp": [-100.0, -50.0, -100.0, -50.0],
            "b2_calc": [-95.0, -45.0, -91.0, -48.0],
            "residual": [5.0, 5.0, 9.0, 2.0],
            "potential": ["lj", "lj", "lj", "lj"],
            "method": ["direct", "direct", "partitioned", "partitioned"],
        }
    )


def _metrics_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "potential": ["lj", "lj"],
            "method": ["direct", "partitioned"],
            "mae": [5.0, 5.5],
            "rmse": [5.0, 6.5],
            "max_error": [5.0, 9.0],
            "mape": [7.5, 8.0],
            "r2": [0.9, 0.8],
        }
    )


def _partitioned_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "temperature": [100.0, 200.0],
            "potential": ["lj", "lj"],
            "b1": [1.0, 1.0],
            "b2": [-10.0, -8.0],
            "b3": [-80.0, -40.0],
            "b4": [-2.0, -1.0],
            "b_total": [-91.0, -48.0],
        }
    )


def test_plot_b2_methods_vs_experiment_returns_figure() -> None:
    fig = plot_b2_methods_vs_experiment(_comparison_df())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_b2_method_residuals_returns_figure() -> None:
    fig = plot_b2_method_residuals(_comparison_df())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_b2_method_metrics_returns_figure() -> None:
    fig = plot_b2_method_metrics(_metrics_df())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_partitioned_contributions_returns_figure() -> None:
    fig = plot_partitioned_contributions(_partitioned_df(), potential="lj")

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_b2_method_plot_functions_save_files_when_output_path_is_provided(tmp_path) -> None:
    paths = [
        tmp_path / "methods.png",
        tmp_path / "residuals.png",
        tmp_path / "metrics.png",
        tmp_path / "contrib.png",
    ]

    figures = [
        plot_b2_methods_vs_experiment(_comparison_df(), output_path=paths[0]),
        plot_b2_method_residuals(_comparison_df(), output_path=paths[1]),
        plot_b2_method_metrics(_metrics_df(), output_path=paths[2]),
        plot_partitioned_contributions(_partitioned_df(), potential="lj", output_path=paths[3]),
    ]

    assert all(path.exists() for path in paths)
    for fig in figures:
        plt.close(fig)


def test_b2_method_plot_functions_create_missing_parent_directories(tmp_path) -> None:
    output_path = tmp_path / "outputs" / "figures" / "ar2" / "methods" / "methods.png"

    fig = plot_b2_methods_vs_experiment(_comparison_df(), output_path=output_path)

    assert output_path.exists()
    plt.close(fig)

