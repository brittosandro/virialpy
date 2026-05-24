import numpy as np
import pandas as pd
import pytest

from virialpy.integrators import ScipyQuadIntegrator
from virialpy.units import kcal_per_mol_to_kelvin
from virialpy.workflows import (
    load_parameters_from_csv,
    load_temperatures_from_csv,
    run_b2_workflow,
)


EXPECTED_COLUMNS = [
    "temperature",
    "b2",
    "integration_error",
    "potential",
    "distance_unit",
    "energy_unit",
    "r_min",
    "r_max",
]


def test_run_b2_workflow_calculates_values_for_lennard_jones_parameters() -> None:
    result = run_b2_workflow(
        potential_name="lj",
        parameters={"epsilon": 120.0, "sigma": 3.4},
        temperatures=[100.0, 200.0],
        integrator=ScipyQuadIntegrator(),
        r_min=2.5,
        r_max=30.0,
    )

    assert len(result) == 2
    assert np.isfinite(result["b2"]).all()


def test_run_b2_workflow_returns_dataframe_with_expected_columns() -> None:
    result = run_b2_workflow(
        potential_name="lj",
        parameters={"epsilon": 120.0, "sigma": 3.4},
        temperatures=[100.0],
        integrator=ScipyQuadIntegrator(),
        r_min=2.5,
        r_max=30.0,
    )

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == EXPECTED_COLUMNS


def test_run_b2_workflow_saves_csv_when_output_path_is_provided(tmp_path) -> None:
    output_path = tmp_path / "results" / "b2.csv"

    run_b2_workflow(
        potential_name="lj",
        parameters={"epsilon": 120.0, "sigma": 3.4},
        temperatures=[100.0],
        integrator=ScipyQuadIntegrator(),
        r_min=2.5,
        r_max=30.0,
        output_path=output_path,
    )

    assert output_path.exists()
    saved = pd.read_csv(output_path)
    assert list(saved.columns) == EXPECTED_COLUMNS


def test_run_b2_workflow_raises_error_for_unknown_potential() -> None:
    with pytest.raises(ValueError, match="Unknown potential_name"):
        run_b2_workflow(
            potential_name="unknown",
            parameters={},
            temperatures=[100.0],
            integrator=ScipyQuadIntegrator(),
            r_min=2.5,
            r_max=30.0,
        )


def test_run_b2_workflow_passes_energy_unit_to_b2_calculation() -> None:
    result_kcal = run_b2_workflow(
        potential_name="lj",
        parameters={"epsilon": 1.0, "sigma": 3.4},
        temperatures=[300.0],
        integrator=ScipyQuadIntegrator(),
        r_min=2.5,
        r_max=30.0,
        energy_unit="kcal/mol",
    )
    result_kelvin = run_b2_workflow(
        potential_name="lj",
        parameters={"epsilon": kcal_per_mol_to_kelvin(1.0), "sigma": 3.4},
        temperatures=[300.0],
        integrator=ScipyQuadIntegrator(),
        r_min=2.5,
        r_max=30.0,
        energy_unit="kelvin",
    )

    assert result_kcal.loc[0, "energy_unit"] == "kcal/mol"
    assert result_kcal.loc[0, "b2"] == pytest.approx(result_kelvin.loc[0, "b2"], rel=1e-6)


def test_load_parameters_from_csv_reads_parameter_table(tmp_path) -> None:
    csv_path = tmp_path / "fit_parameters.csv"
    pd.DataFrame(
        {
            "potential": ["lj", "lj"],
            "parameter": ["epsilon", "sigma"],
            "value": ["120.0", "3.4"],
        }
    ).to_csv(csv_path, index=False)

    parameters = load_parameters_from_csv(csv_path)

    assert parameters == {"epsilon": 120.0, "sigma": 3.4}


def test_load_parameters_from_csv_raises_error_when_required_column_is_missing(tmp_path) -> None:
    csv_path = tmp_path / "fit_parameters.csv"
    pd.DataFrame({"parameter": ["epsilon"], "value": [120.0]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing required column"):
        load_parameters_from_csv(csv_path)


def test_load_temperatures_from_csv_reads_temperature_column(tmp_path) -> None:
    csv_path = tmp_path / "temperatures.csv"
    pd.DataFrame({"temperature": [100.0, None, 200.0]}).to_csv(csv_path, index=False)

    temperatures = load_temperatures_from_csv(csv_path)

    assert temperatures == [100.0, 200.0]


def test_load_temperatures_from_csv_raises_error_when_column_is_missing(tmp_path) -> None:
    csv_path = tmp_path / "temperatures.csv"
    pd.DataFrame({"temp": [100.0, 200.0]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing required column"):
        load_temperatures_from_csv(csv_path)


def test_load_temperatures_from_csv_raises_error_for_non_positive_temperature(tmp_path) -> None:
    csv_path = tmp_path / "temperatures.csv"
    pd.DataFrame({"temperature": [100.0, 0.0, -10.0]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="positive"):
        load_temperatures_from_csv(csv_path)
