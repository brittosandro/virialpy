import numpy as np
import pandas as pd
import pytest

from virialpy.integrators import GaussianQuadratureIntegrator, ScipyQuadIntegrator
from virialpy.workflows import (
    load_model_parameters_from_results,
    run_b2_comparison_workflow,
)


EXPECTED_COLUMNS = [
    "temperature",
    "potential",
    "potential_label",
    "integrator",
    "integrator_label",
    "b2",
    "integration_error",
    "distance_unit",
    "energy_unit",
    "r_min",
    "r_max",
]


def _models() -> list[dict]:
    return [
        {
            "name": "lj",
            "label": "Lennard-Jones",
            "parameters": {"epsilon": 10.0, "sigma": 1.0},
        },
        {
            "name": "ilj",
            "label": "Improved Lennard-Jones",
            "parameters": {"de": 10.0, "req": 1.1, "beta": 8.0},
        },
    ]


def _integrators() -> list[dict]:
    return [
        {
            "name": "scipy_quad",
            "label": "SciPy quad",
            "integrator": ScipyQuadIntegrator(),
        },
        {
            "name": "gaussian",
            "label": "Gaussian quadrature",
            "integrator": GaussianQuadratureIntegrator(n_points=64),
        },
    ]


def test_b2_comparison_workflow_calculates_multiple_models_and_integrators() -> None:
    result = run_b2_comparison_workflow(
        models=_models(),
        temperatures=[100.0, 200.0],
        integrators=_integrators(),
        r_min=0.8,
        r_max=5.0,
        energy_unit="kelvin",
    )

    assert set(result["potential"]) == {"lj", "ilj"}
    assert set(result["integrator"]) == {"scipy_quad", "gaussian"}
    assert np.isfinite(result["b2"]).all()


def test_b2_comparison_workflow_returns_expected_columns() -> None:
    result = run_b2_comparison_workflow(
        models=_models(),
        temperatures=[100.0],
        integrators=_integrators(),
        r_min=0.8,
        r_max=5.0,
        energy_unit="kelvin",
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_b2_comparison_workflow_row_count_matches_grid_size() -> None:
    temperatures = [100.0, 200.0]
    models = _models()
    integrators = _integrators()

    result = run_b2_comparison_workflow(
        models=models,
        temperatures=temperatures,
        integrators=integrators,
        r_min=0.8,
        r_max=5.0,
        energy_unit="kelvin",
    )

    assert len(result) == len(models) * len(integrators) * len(temperatures)


def test_b2_comparison_workflow_saves_csv_when_output_path_is_provided(tmp_path) -> None:
    output_path = tmp_path / "results" / "b2_comparison.csv"

    run_b2_comparison_workflow(
        models=_models(),
        temperatures=[100.0],
        integrators=_integrators(),
        r_min=0.8,
        r_max=5.0,
        energy_unit="kelvin",
        output_path=output_path,
    )

    assert output_path.exists()
    assert list(pd.read_csv(output_path).columns) == EXPECTED_COLUMNS


def test_b2_comparison_workflow_raises_error_for_unknown_potential() -> None:
    models = [{"name": "unknown", "label": "Unknown", "parameters": {}}]

    with pytest.raises(ValueError, match="Unknown potential_name"):
        run_b2_comparison_workflow(
            models=models,
            temperatures=[100.0],
            integrators=_integrators(),
            r_min=0.8,
            r_max=5.0,
        )


def test_load_model_parameters_from_results_loads_subfolder_parameters(tmp_path) -> None:
    base_dir = tmp_path / "results"
    lj_dir = base_dir / "lj"
    ilj_dir = base_dir / "ilj"
    lj_dir.mkdir(parents=True)
    ilj_dir.mkdir(parents=True)
    pd.DataFrame(
        {
            "potential": ["lj", "lj"],
            "parameter": ["epsilon", "sigma"],
            "value": [10.0, 1.0],
        }
    ).to_csv(lj_dir / "fit_parameters.csv", index=False)
    pd.DataFrame(
        {
            "potential": ["ilj", "ilj", "ilj"],
            "parameter": ["de", "req", "beta"],
            "value": [10.0, 1.1, 8.0],
        }
    ).to_csv(ilj_dir / "fit_parameters.csv", index=False)

    models = load_model_parameters_from_results(
        base_dir,
        [
            {"name": "lj", "label": "Lennard-Jones"},
            {"name": "ilj", "label": "Improved Lennard-Jones"},
        ],
    )

    assert models == [
        {
            "name": "lj",
            "label": "Lennard-Jones",
            "parameters": {"epsilon": 10.0, "sigma": 1.0},
        },
        {
            "name": "ilj",
            "label": "Improved Lennard-Jones",
            "parameters": {"de": 10.0, "req": 1.1, "beta": 8.0},
        },
    ]


def test_load_model_parameters_from_results_raises_error_for_missing_parameter_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="Parameter file not found"):
        load_model_parameters_from_results(
            tmp_path,
            [{"name": "lj", "label": "Lennard-Jones"}],
        )

