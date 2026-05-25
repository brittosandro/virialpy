import pandas as pd
import pytest

from virialpy.analysis import (
    compare_monte_carlo_with_integrators,
    summarize_monte_carlo_comparison,
)


EXPECTED_COLUMNS = [
    "temperature",
    "potential",
    "reference_integrator",
    "b2_monte_carlo",
    "b2_reference",
    "difference",
    "abs_difference",
    "percent_difference",
]


def _write_b2_results(path) -> None:
    pd.DataFrame(
        {
            "temperature": [100.0, 100.0, 100.0, 200.0, 200.0, 200.0],
            "potential": ["lj", "lj", "lj", "lj", "lj", "lj"],
            "integrator": ["monte_carlo", "scipy_quad", "gaussian"] * 2,
            "b2": [-101.0, -100.0, -99.0, -51.0, -50.0, -49.0],
        }
    ).to_csv(path, index=False)


def test_compare_monte_carlo_with_integrators_returns_expected_columns(tmp_path) -> None:
    path = tmp_path / "b2.csv"
    _write_b2_results(path)

    result = compare_monte_carlo_with_integrators(path)

    assert list(result.columns) == EXPECTED_COLUMNS


def test_compare_monte_carlo_with_all_integrators_when_reference_is_none(tmp_path) -> None:
    path = tmp_path / "b2.csv"
    _write_b2_results(path)

    result = compare_monte_carlo_with_integrators(path)

    assert set(result["reference_integrator"]) == {"gaussian", "scipy_quad"}


def test_compare_monte_carlo_with_integrators_saves_csv(tmp_path) -> None:
    path = tmp_path / "b2.csv"
    output = tmp_path / "results" / "mc.csv"
    _write_b2_results(path)

    compare_monte_carlo_with_integrators(path, output_path=output)

    assert output.exists()


def test_compare_monte_carlo_with_integrators_raises_when_mc_missing(tmp_path) -> None:
    path = tmp_path / "b2.csv"
    pd.DataFrame(
        {
            "temperature": [100.0],
            "potential": ["lj"],
            "integrator": ["scipy_quad"],
            "b2": [-100.0],
        }
    ).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Monte Carlo integrator"):
        compare_monte_carlo_with_integrators(path)


def test_summarize_monte_carlo_comparison_returns_expected_columns(tmp_path) -> None:
    path = tmp_path / "b2.csv"
    _write_b2_results(path)
    comparison = compare_monte_carlo_with_integrators(path)

    summary = summarize_monte_carlo_comparison(comparison)

    assert list(summary.columns) == [
        "potential",
        "reference_integrator",
        "mean_abs_difference",
        "max_abs_difference",
        "rmse_difference",
        "mean_percent_difference",
    ]

