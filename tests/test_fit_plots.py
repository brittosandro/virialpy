import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from virialpy.fitting import FitResult
from virialpy.plotting import plot_fit_diagnostics, plot_fit_residuals, plot_fit_result


def _fit_result_with_arrays() -> FitResult:
    r_values = np.array([4.0, 3.0, 3.5])
    observed = np.array([-1.0, 1.0, -2.0])
    fitted = np.array([-1.1, 0.9, -1.8])
    residuals = observed - fitted
    return FitResult(
        potential_name="lj",
        parameter_names=["epsilon", "sigma"],
        parameter_values={"epsilon": 120.0, "sigma": 3.4},
        covariance=None,
        residuals=residuals,
        rmse=float(np.sqrt(np.mean(residuals**2))),
        mae=float(np.mean(np.abs(residuals))),
        r2=0.99,
        success=True,
        message="ok",
        r_values=r_values,
        observed_values=observed,
        fitted_values=fitted,
    )


def _fit_result_without_arrays() -> FitResult:
    return FitResult(
        potential_name="lj",
        parameter_names=["epsilon", "sigma"],
        parameter_values={"epsilon": 120.0, "sigma": 3.4},
        covariance=None,
        residuals=np.array([0.0, 0.0]),
        rmse=0.0,
        mae=0.0,
        r2=1.0,
        success=True,
        message="ok",
    )


def test_plot_fit_result_returns_figure() -> None:
    fig = plot_fit_result(_fit_result_with_arrays())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_fit_residuals_returns_figure() -> None:
    fig = plot_fit_residuals(_fit_result_with_arrays())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_fit_diagnostics_returns_figure() -> None:
    fig = plot_fit_diagnostics(_fit_result_with_arrays())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_fit_result_saves_file_when_output_path_is_provided(tmp_path) -> None:
    output_path = tmp_path / "fit.png"

    fig = plot_fit_result(_fit_result_with_arrays(), output_path=output_path)

    assert output_path.exists()
    plt.close(fig)


def test_plot_fit_residuals_saves_file_when_output_path_is_provided(tmp_path) -> None:
    output_path = tmp_path / "residuals.png"

    fig = plot_fit_residuals(_fit_result_with_arrays(), output_path=output_path)

    assert output_path.exists()
    plt.close(fig)


def test_plot_fit_diagnostics_saves_file_when_output_path_is_provided(tmp_path) -> None:
    output_path = tmp_path / "diagnostics.png"

    fig = plot_fit_diagnostics(_fit_result_with_arrays(), output_path=output_path)

    assert output_path.exists()
    plt.close(fig)


def test_plot_functions_create_missing_parent_directories(tmp_path) -> None:
    output_path = tmp_path / "outputs" / "figures" / "ar2" / "fit" / "lj_fit.png"

    fig = plot_fit_result(_fit_result_with_arrays(), output_path=output_path)

    assert output_path.exists()
    plt.close(fig)


def test_plot_functions_raise_clear_error_without_required_arrays() -> None:
    result = _fit_result_without_arrays()

    with pytest.raises(ValueError, match="r_values"):
        plot_fit_result(result)

    with pytest.raises(ValueError, match="r_values"):
        plot_fit_residuals(result)

    with pytest.raises(ValueError, match="r_values"):
        plot_fit_diagnostics(result)

