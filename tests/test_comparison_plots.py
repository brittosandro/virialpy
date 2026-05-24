import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from virialpy.fitting import FitResult
from virialpy.plotting import (
    plot_comparison_diagnostics,
    plot_multiple_fits,
    plot_multiple_residuals,
)


def _fit_result(model_name: str, offset: float = 0.0) -> FitResult:
    r_values = np.array([4.0, 3.0, 3.5])
    observed = np.array([-1.0, 1.0, -2.0])
    fitted = np.array([-1.1, 0.9, -1.8]) + offset
    residuals = observed - fitted
    return FitResult(
        potential_name=model_name,
        parameter_names=["a", "b"],
        parameter_values={"a": 1.0, "b": 2.0},
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


def _comparison_results() -> dict[str, FitResult]:
    return {
        "lj": _fit_result("lj"),
        "ilj": _fit_result("ilj", offset=0.05),
    }


def _bad_comparison_results() -> dict[str, FitResult]:
    bad = _fit_result("bad")
    bad.r_values = None
    return {"lj": _fit_result("lj"), "bad": bad}


def test_plot_multiple_fits_returns_figure() -> None:
    fig = plot_multiple_fits(_comparison_results())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_multiple_residuals_returns_figure() -> None:
    fig = plot_multiple_residuals(_comparison_results())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_comparison_diagnostics_returns_figure() -> None:
    fig = plot_comparison_diagnostics(_comparison_results())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_comparison_plot_functions_save_files_when_output_path_is_provided(tmp_path) -> None:
    paths = [
        tmp_path / "fits.png",
        tmp_path / "residuals.png",
        tmp_path / "diagnostics.png",
    ]

    figures = [
        plot_multiple_fits(_comparison_results(), output_path=paths[0]),
        plot_multiple_residuals(_comparison_results(), output_path=paths[1]),
        plot_comparison_diagnostics(_comparison_results(), output_path=paths[2]),
    ]

    assert all(path.exists() for path in paths)
    for fig in figures:
        plt.close(fig)


def test_comparison_plot_functions_create_missing_parent_directories(tmp_path) -> None:
    output_path = tmp_path / "outputs" / "figures" / "ar2" / "fit" / "comparison_fits.png"

    fig = plot_multiple_fits(_comparison_results(), output_path=output_path)

    assert output_path.exists()
    plt.close(fig)


def test_comparison_plot_functions_raise_clear_error_without_required_arrays() -> None:
    results = _bad_comparison_results()

    with pytest.raises(ValueError, match="r_values"):
        plot_multiple_fits(results)

    with pytest.raises(ValueError, match="r_values"):
        plot_multiple_residuals(results)

    with pytest.raises(ValueError, match="r_values"):
        plot_comparison_diagnostics(results)

