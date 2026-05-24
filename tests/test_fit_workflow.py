import numpy as np
import pandas as pd
import pytest

from virialpy.fitting import FitResult
from virialpy.potentials import lennard_jones
from virialpy.workflows import run_fit_workflow


def _write_lennard_jones_csv(
    path,
    r_column: str = "r",
    energy_column: str = "energy",
) -> None:
    r = np.linspace(3.2, 8.0, 60)
    energy = lennard_jones(r, epsilon=120.0, sigma=3.4)
    pd.DataFrame({r_column: r, energy_column: energy}).to_csv(path, index=False)


def test_run_fit_workflow_fits_lennard_jones_with_standard_columns(tmp_path) -> None:
    csv_path = tmp_path / "lj.csv"
    _write_lennard_jones_csv(csv_path)

    result = run_fit_workflow(
        data_path=csv_path,
        potential_name="lj",
        initial_guess=[100.0, 3.2],
        parameter_names=["epsilon", "sigma"],
    )

    assert result.parameter_values["epsilon"] == pytest.approx(120.0, rel=1e-8)
    assert result.parameter_values["sigma"] == pytest.approx(3.4, rel=1e-8)


def test_run_fit_workflow_fits_lennard_jones_with_custom_columns(tmp_path) -> None:
    csv_path = tmp_path / "lj_custom.csv"
    _write_lennard_jones_csv(
        csv_path,
        r_column="r(angstrom)",
        energy_column="E_int_CP(kcal/mol)",
    )

    result = run_fit_workflow(
        data_path=csv_path,
        potential_name="lj",
        initial_guess=[100.0, 3.2],
        parameter_names=["epsilon", "sigma"],
        r_column="r(angstrom)",
        energy_column="E_int_CP(kcal/mol)",
    )

    assert result.parameter_values["epsilon"] == pytest.approx(120.0, rel=1e-8)
    assert result.parameter_values["sigma"] == pytest.approx(3.4, rel=1e-8)


def test_run_fit_workflow_raises_error_for_unknown_potential(tmp_path) -> None:
    csv_path = tmp_path / "lj.csv"
    _write_lennard_jones_csv(csv_path)

    with pytest.raises(ValueError, match="Unknown potential_name"):
        run_fit_workflow(
            data_path=csv_path,
            potential_name="unknown",
            initial_guess=[100.0, 3.2],
            parameter_names=["epsilon", "sigma"],
        )


def test_run_fit_workflow_returns_successful_fit_result(tmp_path) -> None:
    csv_path = tmp_path / "lj.csv"
    _write_lennard_jones_csv(csv_path)

    result = run_fit_workflow(csv_path, "lj", [100.0, 3.2], ["epsilon", "sigma"])

    assert isinstance(result, FitResult)
    assert result.success is True


def test_run_fit_workflow_metrics_are_near_zero_for_noise_free_data(tmp_path) -> None:
    csv_path = tmp_path / "lj.csv"
    _write_lennard_jones_csv(csv_path)

    result = run_fit_workflow(csv_path, "lj", [100.0, 3.2], ["epsilon", "sigma"])

    assert result.rmse == pytest.approx(0.0, abs=1e-10)
    assert result.mae == pytest.approx(0.0, abs=1e-10)


def test_run_fit_workflow_does_not_save_files_when_output_dir_is_none(tmp_path) -> None:
    csv_path = tmp_path / "lj.csv"
    _write_lennard_jones_csv(csv_path)

    run_fit_workflow(
        csv_path,
        "lj",
        [100.0, 3.2],
        ["epsilon", "sigma"],
        output_dir=None,
    )

    assert sorted(path.name for path in tmp_path.iterdir()) == ["lj.csv"]


def test_run_fit_workflow_saves_files_when_output_dir_is_provided(tmp_path) -> None:
    csv_path = tmp_path / "lj.csv"
    output_dir = tmp_path / "results" / "fit"
    _write_lennard_jones_csv(csv_path)

    run_fit_workflow(
        csv_path,
        "lj",
        [100.0, 3.2],
        ["epsilon", "sigma"],
        output_dir=output_dir,
    )

    assert (output_dir / "fit_parameters.csv").exists()
    assert (output_dir / "fit_metrics.csv").exists()
    assert (output_dir / "fit_residuals.csv").exists()
