import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from virialpy.fitting import FitResult
from virialpy.potentials import lennard_jones
from virialpy.workflows import run_potential_comparison_workflow, summarize_fit_results


def _write_synthetic_lennard_jones_csv(path) -> None:
    r = np.linspace(3.2, 8.0, 60)
    energy = lennard_jones(r, epsilon=120.0, sigma=3.4)
    pd.DataFrame({"r": r, "energy": energy}).to_csv(path, index=False)


def _models() -> list[dict]:
    return [
        {
            "name": "lj",
            "label": "Lennard-Jones",
            "initial_guess": [100.0, 3.2],
            "parameter_names": ["epsilon", "sigma"],
            "bounds": ([0.0, 0.0], [np.inf, np.inf]),
        },
        {
            "name": "ilj",
            "label": "Improved Lennard-Jones",
            "initial_guess": [100.0, 3.4, 8.0],
            "parameter_names": ["de", "req", "beta"],
            "bounds": ([0.0, 0.0, 6.1], [np.inf, np.inf, 30.0]),
        },
    ]


def test_comparison_workflow_fits_at_least_two_models(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    _write_synthetic_lennard_jones_csv(csv_path)

    results = run_potential_comparison_workflow(csv_path, _models())

    assert set(results) == {"lj", "ilj"}


def test_comparison_workflow_returns_fit_result_objects(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    _write_synthetic_lennard_jones_csv(csv_path)

    results = run_potential_comparison_workflow(csv_path, _models())

    assert all(isinstance(result, FitResult) for result in results.values())


def test_summarize_fit_results_returns_expected_columns(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    _write_synthetic_lennard_jones_csv(csv_path)
    results = run_potential_comparison_workflow(csv_path, _models())

    summary = summarize_fit_results(results)

    assert list(summary.columns) == ["model", "potential", "rmse", "mae", "r2", "success"]


def test_summarize_fit_results_is_sorted_by_increasing_rmse(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    _write_synthetic_lennard_jones_csv(csv_path)
    results = run_potential_comparison_workflow(csv_path, _models())

    summary = summarize_fit_results(results)

    assert summary["rmse"].tolist() == sorted(summary["rmse"].tolist())


def test_comparison_workflow_raises_error_for_unknown_potential(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    _write_synthetic_lennard_jones_csv(csv_path)
    models = [{"name": "unknown", "label": "Unknown", "initial_guess": [1.0], "parameter_names": ["a"]}]

    with pytest.raises(ValueError, match="Unknown potential name"):
        run_potential_comparison_workflow(csv_path, models)


def test_comparison_workflow_saves_per_model_results(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    results_dir = tmp_path / "results"
    _write_synthetic_lennard_jones_csv(csv_path)

    run_potential_comparison_workflow(csv_path, _models(), results_dir=results_dir)

    for model_name in ["lj", "ilj"]:
        assert (results_dir / model_name / "fit_parameters.csv").exists()
        assert (results_dir / model_name / "fit_metrics.csv").exists()
        assert (results_dir / model_name / "fit_residuals.csv").exists()


def test_comparison_workflow_saves_comparison_metrics(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    results_dir = tmp_path / "results"
    _write_synthetic_lennard_jones_csv(csv_path)

    run_potential_comparison_workflow(csv_path, _models(), results_dir=results_dir)

    assert (results_dir / "fit_comparison_metrics.csv").exists()


def test_comparison_workflow_saves_figures_for_each_model(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    figures_dir = tmp_path / "figures"
    _write_synthetic_lennard_jones_csv(csv_path)

    run_potential_comparison_workflow(csv_path, _models(), figures_dir=figures_dir)

    for model_name in ["lj", "ilj"]:
        assert (figures_dir / f"{model_name}_fit.png").exists()
        assert (figures_dir / f"{model_name}_residuals.png").exists()
        assert (figures_dir / f"{model_name}_diagnostics.png").exists()

