import pandas as pd
import pytest

from virialpy.integrators import GaussianQuadratureIntegrator
from virialpy.workflows import run_partitioned_b2_workflow


def _integrator():
    return GaussianQuadratureIntegrator(n_points=16)


def test_run_partitioned_b2_workflow_returns_dataframe() -> None:
    result = run_partitioned_b2_workflow(
        potential_name="lj",
        parameters={"epsilon": 100.0, "sigma": 3.4},
        temperatures=[100.0],
        integrator_b2=_integrator(),
        integrator_b3=_integrator(),
        integrator_b4=_integrator(),
        r1=2.5,
        r2=3.5,
        r3=8.0,
        r4=12.0,
        energy_unit="kelvin",
    )

    assert isinstance(result, pd.DataFrame)


def test_run_partitioned_b2_workflow_has_one_row_per_temperature() -> None:
    temperatures = [100.0, 200.0, 300.0]

    result = run_partitioned_b2_workflow(
        "lj",
        {"epsilon": 100.0, "sigma": 3.4},
        temperatures,
        _integrator(),
        _integrator(),
        _integrator(),
        2.5,
        3.5,
        8.0,
        12.0,
        energy_unit="kelvin",
    )

    assert len(result) == len(temperatures)


def test_run_partitioned_b2_workflow_contains_components_and_total() -> None:
    result = run_partitioned_b2_workflow(
        "lj",
        {"epsilon": 100.0, "sigma": 3.4},
        [100.0],
        _integrator(),
        _integrator(),
        _integrator(),
        2.5,
        3.5,
        8.0,
        12.0,
        energy_unit="kelvin",
    )

    for column in ["b1", "b2", "b3", "b4", "b_total"]:
        assert column in result.columns


def test_run_partitioned_b2_workflow_total_equals_sum_of_components() -> None:
    result = run_partitioned_b2_workflow(
        "lj",
        {"epsilon": 100.0, "sigma": 3.4},
        [100.0],
        _integrator(),
        _integrator(),
        _integrator(),
        2.5,
        3.5,
        8.0,
        12.0,
        energy_unit="kelvin",
    )
    row = result.iloc[0]

    assert row["b_total"] == pytest.approx(row["b1"] + row["b2"] + row["b3"] + row["b4"])


def test_run_partitioned_b2_workflow_saves_csv(tmp_path) -> None:
    output_path = tmp_path / "results" / "partitioned.csv"

    run_partitioned_b2_workflow(
        "lj",
        {"epsilon": 100.0, "sigma": 3.4},
        [100.0],
        _integrator(),
        _integrator(),
        _integrator(),
        2.5,
        3.5,
        8.0,
        12.0,
        energy_unit="kelvin",
        output_path=output_path,
    )

    assert output_path.exists()


def test_run_partitioned_b2_workflow_raises_error_for_unknown_potential() -> None:
    with pytest.raises(ValueError, match="Unknown potential_name"):
        run_partitioned_b2_workflow(
            "unknown",
            {},
            [100.0],
            _integrator(),
            _integrator(),
            _integrator(),
            2.5,
            3.5,
            8.0,
            12.0,
        )

