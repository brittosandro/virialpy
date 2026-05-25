import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from virialpy.plotting import (
    plot_monte_carlo_difference,
    plot_monte_carlo_summary_metrics,
    plot_monte_carlo_vs_reference,
)


def _comparison_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "temperature": [100.0, 200.0],
            "potential": ["lj", "lj"],
            "reference_integrator": ["scipy_quad", "scipy_quad"],
            "b2_monte_carlo": [-101.0, -51.0],
            "b2_reference": [-100.0, -50.0],
            "difference": [-1.0, -1.0],
            "abs_difference": [1.0, 1.0],
            "percent_difference": [1.0, 2.0],
        }
    )


def _summary_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "potential": ["lj"],
            "reference_integrator": ["scipy_quad"],
            "mean_abs_difference": [1.0],
            "max_abs_difference": [1.0],
            "rmse_difference": [1.0],
            "mean_percent_difference": [1.5],
        }
    )


def test_plot_monte_carlo_vs_reference_returns_figure() -> None:
    fig = plot_monte_carlo_vs_reference(_comparison_df(), "scipy_quad")
    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_monte_carlo_difference_returns_figure() -> None:
    fig = plot_monte_carlo_difference(_comparison_df(), "scipy_quad")
    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_monte_carlo_summary_metrics_returns_figure() -> None:
    fig = plot_monte_carlo_summary_metrics(_summary_df())
    assert isinstance(fig, Figure)
    plt.close(fig)


def test_monte_carlo_plot_functions_save_files(tmp_path) -> None:
    paths = [tmp_path / "vs.png", tmp_path / "diff.png", tmp_path / "summary.png"]
    figs = [
        plot_monte_carlo_vs_reference(_comparison_df(), "scipy_quad", output_path=paths[0]),
        plot_monte_carlo_difference(_comparison_df(), "scipy_quad", output_path=paths[1]),
        plot_monte_carlo_summary_metrics(_summary_df(), output_path=paths[2]),
    ]
    assert all(path.exists() for path in paths)
    for fig in figs:
        plt.close(fig)


def test_monte_carlo_plot_functions_create_missing_directories(tmp_path) -> None:
    output = tmp_path / "outputs" / "mc" / "vs.png"
    fig = plot_monte_carlo_vs_reference(_comparison_df(), "scipy_quad", output_path=output)
    assert output.exists()
    plt.close(fig)

