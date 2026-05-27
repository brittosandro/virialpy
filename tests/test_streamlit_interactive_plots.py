import pandas as pd
from plotly.graph_objects import Figure

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


def test_plotly_b2_comparison_returns_figure() -> None:
    data = pd.DataFrame(
        {
            "temperature": [100, 200],
            "b2_exp": [-10, -5],
            "b2_calc": [-9, -4],
            "residual": [1, 1],
            "potential": ["lj", "lj"],
            "integrator": ["scipy_quad", "scipy_quad"],
        }
    )

    fig = plotly_b2_comparison(data)

    assert isinstance(fig, Figure)


def test_plotly_fit_curves_returns_figure() -> None:
    observed = pd.DataFrame({"r": [3.0, 4.0], "energy": [-1.0, -0.2]})
    fitted = pd.DataFrame({"r": [3.0, 4.0], "energy_fit": [-0.9, -0.1], "potential": ["lj", "lj"]})

    fig = plotly_fit_curves(observed, fitted)

    assert isinstance(fig, Figure)


def test_plotly_fit_curves_returns_figure_for_single_potential() -> None:
    observed = pd.DataFrame({"r": [3.0, 4.0], "energy": [-1.0, -0.2]})
    fitted = pd.DataFrame(
        {
            "r": [3.0, 4.0, 3.0, 4.0],
            "energy_fit": [-0.9, -0.1, -1.0, -0.2],
            "potential": ["lj", "lj", "ilj", "ilj"],
        }
    )

    fig = plotly_fit_curves(observed, fitted, potential="lj")

    assert isinstance(fig, Figure)


def test_plotly_fit_residuals_returns_figure() -> None:
    residuals = pd.DataFrame({"r": [3.0, 4.0], "residual": [0.1, -0.1], "potential": ["lj", "lj"]})

    fig = plotly_fit_residuals(residuals)

    assert isinstance(fig, Figure)


def test_plotly_fit_residuals_returns_figure_for_single_potential() -> None:
    residuals = pd.DataFrame(
        {
            "r": [3.0, 4.0, 3.0, 4.0],
            "residual": [0.1, -0.1, 0.0, 0.1],
            "potential": ["lj", "lj", "ilj", "ilj"],
        }
    )

    fig = plotly_fit_residuals(residuals, potential="lj")

    assert isinstance(fig, Figure)


def test_plotly_fit_observed_vs_predicted_returns_figure() -> None:
    residuals = pd.DataFrame(
        {
            "energy_observed": [-1.0, -0.2],
            "energy_fitted": [-0.9, -0.1],
            "potential": ["lj", "lj"],
        }
    )

    fig = plotly_fit_observed_vs_predicted(residuals)

    assert isinstance(fig, Figure)


def test_plotly_fit_observed_vs_predicted_returns_figure_for_single_potential() -> None:
    residuals = pd.DataFrame(
        {
            "energy_observed": [-1.0, -0.2, -1.0, -0.2],
            "energy_fitted": [-0.9, -0.1, -1.0, -0.2],
            "potential": ["lj", "lj", "ilj", "ilj"],
        }
    )

    fig = plotly_fit_observed_vs_predicted(residuals, potential="lj")

    assert isinstance(fig, Figure)


def test_plotly_fit_metric_ranking_returns_figure() -> None:
    metrics = pd.DataFrame({"potential": ["lj", "ilj"], "rmse": [0.2, 0.1], "mae": [0.1, 0.05], "r2": [0.9, 0.95]})

    fig = plotly_fit_metric_ranking(metrics, metric="rmse")

    assert isinstance(fig, Figure)


def test_plotly_b2_residuals_returns_figure() -> None:
    data = pd.DataFrame(
        {
            "temperature": [100, 200],
            "residual": [1, -1],
            "abs_error": [1, 1],
            "percent_error": [10, 20],
            "potential": ["lj", "lj"],
            "integrator": ["scipy_quad", "scipy_quad"],
        }
    )

    fig = plotly_b2_residuals(data)

    assert isinstance(fig, Figure)


def test_plotly_b2_by_integrator_returns_figure() -> None:
    data = pd.DataFrame(
        {
            "temperature": [100, 200, 100, 200],
            "b2": [-10, -5, -9, -4],
            "potential": ["lj", "lj", "ilj", "ilj"],
            "integrator": ["scipy_quad", "scipy_quad", "gaussian", "gaussian"],
        }
    )

    fig = plotly_b2_by_integrator(data)

    assert isinstance(fig, Figure)


def test_plotly_metric_ranking_returns_figure() -> None:
    data = pd.DataFrame(
        {
            "potential": ["lj", "ilj"],
            "integrator": ["scipy_quad", "gaussian"],
            "mae": [1.0, 0.5],
            "rmse": [1.2, 0.7],
            "max_error": [2.0, 1.0],
            "mape": [5.0, 3.0],
            "r2": [0.9, 0.95],
        }
    )

    fig = plotly_metric_ranking(data, metric="rmse")

    assert isinstance(fig, Figure)


def test_plotly_method_comparison_returns_figure() -> None:
    data = pd.DataFrame(
        {
            "temperature": [100, 100, 200, 200],
            "b2_exp": [-10, -10, -5, -5],
            "b2_calc": [-9, -8, -4, -3],
            "potential": ["lj", "lj", "lj", "lj"],
            "method": ["direct", "partitioned", "direct", "partitioned"],
        }
    )

    fig = plotly_method_comparison(data)

    assert isinstance(fig, Figure)


def test_plotly_monte_carlo_difference_returns_figure() -> None:
    data = pd.DataFrame(
        {
            "temperature": [100, 200],
            "potential": ["lj", "lj"],
            "reference_integrator": ["scipy_quad", "scipy_quad"],
            "difference": [0.1, -0.2],
        }
    )

    fig = plotly_monte_carlo_difference(data)

    assert isinstance(fig, Figure)
