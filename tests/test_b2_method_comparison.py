import pandas as pd
import pytest

from virialpy.workflows import prepare_b2_method_comparison


def _write_method_inputs(tmp_path):
    direct_path = tmp_path / "direct.csv"
    partitioned_path = tmp_path / "partitioned.csv"
    experimental_path = tmp_path / "experimental.csv"

    pd.DataFrame(
        {
            "temperature": [100.0, 200.0, 100.0, 200.0],
            "potential": ["lj", "lj", "lj", "lj"],
            "integrator": ["scipy_quad", "scipy_quad", "gaussian", "gaussian"],
            "b2": [-95.0, -45.0, -96.0, -46.0],
        }
    ).to_csv(direct_path, index=False)
    pd.DataFrame(
        {
            "temperature": [100.0, 200.0],
            "potential": ["lj", "lj"],
            "b1": [1.0, 1.0],
            "b2": [-10.0, -8.0],
            "b3": [-80.0, -40.0],
            "b4": [-2.0, -1.0],
            "b_total": [-91.0, -48.0],
        }
    ).to_csv(partitioned_path, index=False)
    pd.DataFrame(
        {
            "Temperatura": [100.0, 200.0],
            "B(segundo coef. virial) [cm³/mol]": [-100.0, -50.0],
        }
    ).to_csv(experimental_path, index=False)

    return direct_path, partitioned_path, experimental_path


def test_prepare_b2_method_comparison_returns_comparison_and_metrics(tmp_path) -> None:
    direct_path, partitioned_path, experimental_path = _write_method_inputs(tmp_path)

    comparison, metrics = prepare_b2_method_comparison(
        direct_path,
        partitioned_path,
        experimental_path,
    )

    assert isinstance(comparison, pd.DataFrame)
    assert isinstance(metrics, pd.DataFrame)


def test_prepare_b2_method_comparison_contains_expected_comparison_columns(tmp_path) -> None:
    direct_path, partitioned_path, experimental_path = _write_method_inputs(tmp_path)

    comparison, _ = prepare_b2_method_comparison(direct_path, partitioned_path, experimental_path)

    for column in [
        "temperature",
        "b2_exp",
        "b2_calc",
        "residual",
        "abs_error",
        "percent_error",
        "potential",
        "method",
    ]:
        assert column in comparison.columns


def test_prepare_b2_method_comparison_groups_metrics_by_potential_and_method(tmp_path) -> None:
    direct_path, partitioned_path, experimental_path = _write_method_inputs(tmp_path)

    _, metrics = prepare_b2_method_comparison(direct_path, partitioned_path, experimental_path)

    assert set(metrics["potential"]) == {"lj"}
    assert set(metrics["method"]) == {"direct", "partitioned"}
    for column in ["mae", "rmse", "max_error", "mape", "r2"]:
        assert column in metrics.columns


def test_prepare_b2_method_comparison_saves_csv_outputs(tmp_path) -> None:
    direct_path, partitioned_path, experimental_path = _write_method_inputs(tmp_path)
    comparison_output = tmp_path / "results" / "comparison.csv"
    metrics_output = tmp_path / "results" / "metrics.csv"

    prepare_b2_method_comparison(
        direct_path,
        partitioned_path,
        experimental_path,
        output_comparison_path=comparison_output,
        output_metrics_path=metrics_output,
    )

    assert comparison_output.exists()
    assert metrics_output.exists()


def test_prepare_b2_method_comparison_raises_error_for_missing_columns(tmp_path) -> None:
    direct_path = tmp_path / "direct.csv"
    partitioned_path = tmp_path / "partitioned.csv"
    experimental_path = tmp_path / "experimental.csv"
    pd.DataFrame({"temperature": [100.0], "potential": ["lj"], "integrator": ["scipy_quad"]}).to_csv(
        direct_path,
        index=False,
    )
    pd.DataFrame({"temperature": [100.0], "potential": ["lj"], "b_total": [-90.0]}).to_csv(
        partitioned_path,
        index=False,
    )
    pd.DataFrame(
        {
            "Temperatura": [100.0],
            "B(segundo coef. virial) [cm³/mol]": [-100.0],
        }
    ).to_csv(experimental_path, index=False)

    with pytest.raises(ValueError, match="missing required column"):
        prepare_b2_method_comparison(direct_path, partitioned_path, experimental_path)

