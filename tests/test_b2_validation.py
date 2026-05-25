import math

import pandas as pd
import pytest

from virialpy.analysis import calculate_b2_metrics
from virialpy.workflows import validate_b2_against_experiment


def test_calculate_b2_metrics_returns_expected_values_for_simple_data() -> None:
    metrics = calculate_b2_metrics([10.0, 20.0, 40.0], [12.0, 18.0, 44.0])

    assert metrics["mae"] == pytest.approx((2.0 + 2.0 + 4.0) / 3.0)
    assert metrics["rmse"] == pytest.approx(math.sqrt((4.0 + 4.0 + 16.0) / 3.0))
    assert metrics["max_error"] == pytest.approx(4.0)
    assert metrics["mape"] == pytest.approx(((2.0 / 10.0) + (2.0 / 20.0) + (4.0 / 40.0)) / 3.0 * 100.0)
    assert metrics["r2"] == pytest.approx(1.0 - 24.0 / 466.6666666666667)


def test_calculate_b2_metrics_raises_error_for_different_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        calculate_b2_metrics([1.0, 2.0], [1.0])


def _write_validation_inputs(tmp_path):
    calculated_path = tmp_path / "calculated.csv"
    experimental_path = tmp_path / "experimental.csv"
    pd.DataFrame(
        {
            "temperature": [100.0, 200.0, 100.0, 200.0],
            "b2": [-95.0, -45.0, -90.0, -55.0],
            "potential": ["lj", "lj", "ilj", "ilj"],
            "integrator": ["scipy_quad", "scipy_quad", "scipy_quad", "scipy_quad"],
        }
    ).to_csv(calculated_path, index=False)
    pd.DataFrame({"temperature": [100.0, 200.0], "b2": [-100.0, -50.0]}).to_csv(
        experimental_path,
        index=False,
    )
    return calculated_path, experimental_path


def test_validate_b2_against_experiment_merges_calculated_and_experimental_data(tmp_path) -> None:
    calculated_path, experimental_path = _write_validation_inputs(tmp_path)

    comparison, _ = validate_b2_against_experiment(calculated_path, experimental_path)

    assert len(comparison) == 4
    assert set(comparison["temperature"]) == {100.0, 200.0}


def test_validate_b2_against_experiment_creates_comparison_columns(tmp_path) -> None:
    calculated_path, experimental_path = _write_validation_inputs(tmp_path)

    comparison, _ = validate_b2_against_experiment(calculated_path, experimental_path)

    for column in ["temperature", "b2_exp", "b2_calc", "residual", "abs_error", "percent_error"]:
        assert column in comparison.columns
    assert comparison.loc[0, "residual"] == pytest.approx(5.0)
    assert comparison.loc[0, "abs_error"] == pytest.approx(5.0)


def test_validate_b2_against_experiment_creates_grouped_metrics(tmp_path) -> None:
    calculated_path, experimental_path = _write_validation_inputs(tmp_path)

    _, metrics = validate_b2_against_experiment(calculated_path, experimental_path)

    assert set(metrics["potential"]) == {"lj", "ilj"}
    assert set(metrics["integrator"]) == {"scipy_quad"}
    for column in ["mae", "rmse", "max_error", "mape", "r2"]:
        assert column in metrics.columns


def test_validate_b2_against_experiment_saves_csv_outputs(tmp_path) -> None:
    calculated_path, experimental_path = _write_validation_inputs(tmp_path)
    comparison_output = tmp_path / "results" / "comparison.csv"
    metrics_output = tmp_path / "results" / "metrics.csv"

    validate_b2_against_experiment(
        calculated_path,
        experimental_path,
        output_comparison_path=comparison_output,
        output_metrics_path=metrics_output,
    )

    assert comparison_output.exists()
    assert metrics_output.exists()


def test_validate_b2_against_experiment_raises_error_when_required_columns_are_missing(tmp_path) -> None:
    calculated_path = tmp_path / "calculated.csv"
    experimental_path = tmp_path / "experimental.csv"
    pd.DataFrame({"temperature": [100.0], "potential": ["lj"], "integrator": ["scipy_quad"]}).to_csv(
        calculated_path,
        index=False,
    )
    pd.DataFrame({"temperature": [100.0], "b2": [-100.0]}).to_csv(experimental_path, index=False)

    with pytest.raises(ValueError, match="missing required column"):
        validate_b2_against_experiment(calculated_path, experimental_path)
