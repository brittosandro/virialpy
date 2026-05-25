import math

import pytest

from virialpy.constants import AVOGADRO_CONSTANT
from virialpy.integrators import GaussianQuadratureIntegrator, ScipyQuadIntegrator
from virialpy.virial import partitioned_second_virial_coefficient


def zero_potential(r, **parameters):
    return 0.0 * r


def positive_temperature_potential(r, **parameters):
    return parameters["temperature"] + 0.0 * r


def negative_temperature_potential(r, **parameters):
    return -parameters["temperature"] + 0.0 * r


def _integrator():
    return ScipyQuadIntegrator()


def _partitioned_result(potential_func=zero_potential, parameters=None, temperature=100.0):
    return partitioned_second_virial_coefficient(
        temperature=temperature,
        potential_func=potential_func,
        parameters=parameters or {},
        integrator_b2=_integrator(),
        integrator_b3=_integrator(),
        integrator_b4=_integrator(),
        r1=1.0,
        r2=2.0,
        r3=3.0,
        r4=4.0,
    )


def test_partitioned_b2_zero_potential_has_only_b1_contribution() -> None:
    result = _partitioned_result()

    assert result["b2"] == pytest.approx(0.0)
    assert result["b3"] == pytest.approx(0.0)
    assert result["b4"] == pytest.approx(0.0)
    assert result["b_total"] == pytest.approx(result["b1"])


def test_partitioned_b2_positive_constant_potential_has_positive_b2_b3() -> None:
    temperature = 100.0
    result = _partitioned_result(
        positive_temperature_potential,
        {"temperature": temperature},
        temperature=temperature,
    )

    assert result["b2"] > 0.0
    assert result["b3"] > 0.0


def test_partitioned_b2_negative_constant_potential_has_negative_b2_b3() -> None:
    temperature = 100.0
    result = _partitioned_result(
        negative_temperature_potential,
        {"temperature": temperature},
        temperature=temperature,
    )

    assert result["b2"] < 0.0
    assert result["b3"] < 0.0


def test_partitioned_b2_b1_is_analytic_hard_core_term() -> None:
    r1 = 1.5
    result = partitioned_second_virial_coefficient(
        temperature=100.0,
        potential_func=zero_potential,
        parameters={},
        integrator_b2=_integrator(),
        integrator_b3=_integrator(),
        integrator_b4=_integrator(),
        r1=r1,
        r2=2.0,
        r3=3.0,
        r4=4.0,
        distance_unit="angstrom",
    )
    expected = 2.0 * math.pi * AVOGADRO_CONSTANT * r1**3 / 3.0 * 1e-24

    assert result["b1"] == pytest.approx(expected)


def test_partitioned_b2_raises_error_for_non_positive_temperature() -> None:
    with pytest.raises(ValueError, match="temperature"):
        _partitioned_result(temperature=0.0)


def test_partitioned_b2_raises_error_for_invalid_partition_limits() -> None:
    with pytest.raises(ValueError, match="0 < r1 < r2 < r3 < r4"):
        partitioned_second_virial_coefficient(
            temperature=100.0,
            potential_func=zero_potential,
            parameters={},
            integrator_b2=_integrator(),
            integrator_b3=_integrator(),
            integrator_b4=_integrator(),
            r1=1.0,
            r2=1.0,
            r3=3.0,
            r4=4.0,
        )


def test_partitioned_b2_raises_error_for_invalid_distance_unit() -> None:
    with pytest.raises(ValueError, match="Unsupported distance_unit"):
        partitioned_second_virial_coefficient(
            temperature=100.0,
            potential_func=zero_potential,
            parameters={},
            integrator_b2=_integrator(),
            integrator_b3=_integrator(),
            integrator_b4=_integrator(),
            r1=1.0,
            r2=2.0,
            r3=3.0,
            r4=4.0,
            distance_unit="bohr",
        )


def test_partitioned_b2_raises_error_for_invalid_energy_unit() -> None:
    with pytest.raises(ValueError, match="Unsupported energy_unit"):
        partitioned_second_virial_coefficient(
            temperature=100.0,
            potential_func=zero_potential,
            parameters={},
            integrator_b2=_integrator(),
            integrator_b3=_integrator(),
            integrator_b4=_integrator(),
            r1=1.0,
            r2=2.0,
            r3=3.0,
            r4=4.0,
            energy_unit="hartree",
        )


def test_partitioned_b2_result_contains_expected_keys() -> None:
    result = _partitioned_result()

    assert set(result) == {
        "temperature",
        "b1",
        "b2",
        "b3",
        "b4",
        "b_total",
        "error_b2",
        "error_b3",
        "error_b4",
        "r1",
        "r2",
        "r3",
        "r4",
        "distance_unit",
        "energy_unit",
    }


def test_partitioned_b2_total_is_sum_of_components() -> None:
    result = partitioned_second_virial_coefficient(
        temperature=100.0,
        potential_func=positive_temperature_potential,
        parameters={"temperature": 100.0},
        integrator_b2=GaussianQuadratureIntegrator(n_points=16),
        integrator_b3=GaussianQuadratureIntegrator(n_points=16),
        integrator_b4=GaussianQuadratureIntegrator(n_points=16),
        r1=1.0,
        r2=2.0,
        r3=3.0,
        r4=4.0,
    )

    assert result["b_total"] == pytest.approx(
        result["b1"] + result["b2"] + result["b3"] + result["b4"]
    )

