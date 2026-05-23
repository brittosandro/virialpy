import numpy as np
import pandas as pd
import pytest

from virialpy.fitting import FitResult, fit_potential_scipy, predict_potential
from virialpy.potentials import lennard_jones


def _synthetic_lennard_jones_data() -> pd.DataFrame:
    epsilon = 120.0
    sigma = 3.4
    r = np.linspace(3.2, 8.0, 60)
    energy = lennard_jones(r, epsilon=epsilon, sigma=sigma)
    return pd.DataFrame({"r": r, "energy": energy})


def test_fit_potential_scipy_recovers_lennard_jones_parameters() -> None:
    data = _synthetic_lennard_jones_data()

    result = fit_potential_scipy(
        data=data,
        potential_func=lennard_jones,
        initial_guess=[100.0, 3.2],
        parameter_names=["epsilon", "sigma"],
        potential_name="lj",
    )

    assert result.parameter_values["epsilon"] == pytest.approx(120.0, rel=1e-8)
    assert result.parameter_values["sigma"] == pytest.approx(3.4, rel=1e-8)


def test_predict_potential_works_with_parameter_dictionary() -> None:
    predicted = predict_potential(
        3.4,
        lennard_jones,
        {"epsilon": 120.0, "sigma": 3.4},
    )

    assert predicted == pytest.approx(0.0)


def test_fit_potential_scipy_raises_error_without_r_column() -> None:
    data = pd.DataFrame({"distance": [3.2, 3.5, 4.0], "energy": [1.0, -2.0, -1.0]})

    with pytest.raises(ValueError, match="r"):
        fit_potential_scipy(data, lennard_jones, [100.0, 3.2], ["epsilon", "sigma"])


def test_fit_potential_scipy_raises_error_without_energy_column() -> None:
    data = pd.DataFrame({"r": [3.2, 3.5, 4.0], "u": [1.0, -2.0, -1.0]})

    with pytest.raises(ValueError, match="energy"):
        fit_potential_scipy(data, lennard_jones, [100.0, 3.2], ["epsilon", "sigma"])


def test_fit_potential_scipy_raises_error_when_parameter_count_mismatches() -> None:
    data = _synthetic_lennard_jones_data()

    with pytest.raises(ValueError, match="parameter_names"):
        fit_potential_scipy(data, lennard_jones, [100.0, 3.2], ["epsilon"])


def test_fit_result_success_is_true_for_successful_fit() -> None:
    data = _synthetic_lennard_jones_data()

    result = fit_potential_scipy(data, lennard_jones, [100.0, 3.2], ["epsilon", "sigma"])

    assert isinstance(result, FitResult)
    assert result.success is True


def test_fit_metrics_are_near_zero_for_noise_free_data() -> None:
    data = _synthetic_lennard_jones_data()

    result = fit_potential_scipy(data, lennard_jones, [100.0, 3.2], ["epsilon", "sigma"])

    assert result.rmse == pytest.approx(0.0, abs=1e-10)
    assert result.mae == pytest.approx(0.0, abs=1e-10)

