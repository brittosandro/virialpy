import numpy as np
import pandas as pd
import pytest

from virialpy.fitting import FitResult
from virialpy.io import save_fit_metrics, save_fit_parameters, save_fit_residuals


def _fit_result_with_predictions() -> FitResult:
    r_values = np.array([3.0, 3.5, 4.0])
    observed = np.array([1.0, -2.0, -1.0])
    fitted = np.array([0.9, -1.8, -1.1])
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


def _fit_result_without_predictions() -> FitResult:
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


def test_save_fit_parameters_creates_csv_with_adjusted_parameters(tmp_path) -> None:
    output_path = tmp_path / "parameters.csv"

    save_fit_parameters(_fit_result_with_predictions(), output_path)

    data = pd.read_csv(output_path)
    assert list(data.columns) == ["potential", "parameter", "value"]
    assert data["parameter"].tolist() == ["epsilon", "sigma"]
    assert data["value"].tolist() == [120.0, 3.4]


def test_save_fit_metrics_creates_csv_with_fit_metrics(tmp_path) -> None:
    output_path = tmp_path / "metrics.csv"

    save_fit_metrics(_fit_result_with_predictions(), output_path)

    data = pd.read_csv(output_path)
    assert list(data.columns) == ["potential", "rmse", "mae", "r2", "success", "message"]
    assert data.loc[0, "potential"] == "lj"
    assert data.loc[0, "success"] == np.True_
    assert data.loc[0, "message"] == "ok"


def test_save_fit_residuals_creates_csv_with_residual_data(tmp_path) -> None:
    output_path = tmp_path / "residuals.csv"

    save_fit_residuals(_fit_result_with_predictions(), output_path)

    data = pd.read_csv(output_path)
    assert list(data.columns) == ["r", "energy_observed", "energy_fitted", "residual"]
    assert data["r"].tolist() == [3.0, 3.5, 4.0]
    assert data["energy_observed"].tolist() == [1.0, -2.0, -1.0]
    assert data["energy_fitted"].tolist() == [0.9, -1.8, -1.1]
    assert data["residual"].tolist() == pytest.approx([0.1, -0.2, 0.1])


def test_writers_create_missing_parent_directories(tmp_path) -> None:
    output_path = tmp_path / "nested" / "reports" / "parameters.csv"

    save_fit_parameters(_fit_result_with_predictions(), output_path)

    assert output_path.exists()


def test_save_fit_residuals_raises_error_without_prediction_arrays(tmp_path) -> None:
    output_path = tmp_path / "residuals.csv"

    with pytest.raises(ValueError, match="r_values"):
        save_fit_residuals(_fit_result_without_predictions(), output_path)

