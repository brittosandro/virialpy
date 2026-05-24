import math

import pytest

from virialpy.constants import AVOGADRO_CONSTANT
from virialpy.integrators import ScipyQuadIntegrator
from virialpy.units import kcal_per_mol_to_kelvin
from virialpy.virial import mayer_function, mayer_integrand, second_virial_coefficient


def zero_potential(r, **parameters):
    return 0.0 * r


def positive_temperature_potential(r, **parameters):
    return parameters["temperature"] + 0.0 * r


def one_kcal_per_mol_potential(r, **parameters):
    return 1.0 + 0.0 * r


def one_kcal_per_mol_in_kelvin_potential(r, **parameters):
    return kcal_per_mol_to_kelvin(1.0) + 0.0 * r


def negative_temperature_potential(r, **parameters):
    return -parameters["temperature"] + 0.0 * r


def test_mayer_function_is_zero_when_energy_is_zero() -> None:
    assert mayer_function(0.0, temperature=100.0) == pytest.approx(0.0)


def test_mayer_integrand_is_zero_for_zero_potential() -> None:
    value = mayer_integrand(
        r=1.0,
        temperature=100.0,
        potential_func=zero_potential,
        parameters={},
    )

    assert value == pytest.approx(0.0)


def test_second_virial_coefficient_raises_error_for_non_positive_temperature() -> None:
    with pytest.raises(ValueError, match="temperature"):
        second_virial_coefficient(
            temperature=0.0,
            potential_func=zero_potential,
            parameters={},
            integrator=ScipyQuadIntegrator(),
            r_min=0.0,
            r_max=1.0,
        )


def test_second_virial_coefficient_raises_error_when_r_max_is_not_greater_than_r_min() -> None:
    with pytest.raises(ValueError, match="r_max"):
        second_virial_coefficient(
            temperature=100.0,
            potential_func=zero_potential,
            parameters={},
            integrator=ScipyQuadIntegrator(),
            r_min=1.0,
            r_max=1.0,
        )


def test_second_virial_coefficient_raises_error_for_invalid_distance_unit() -> None:
    with pytest.raises(ValueError, match="Unsupported distance_unit"):
        second_virial_coefficient(
            temperature=100.0,
            potential_func=zero_potential,
            parameters={},
            integrator=ScipyQuadIntegrator(),
            r_min=0.0,
            r_max=1.0,
            distance_unit="bohr",
        )


def test_second_virial_coefficient_is_zero_for_zero_potential() -> None:
    value, error = second_virial_coefficient(
        temperature=100.0,
        potential_func=zero_potential,
        parameters={},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=1.0,
    )

    assert value == pytest.approx(0.0)
    assert error == pytest.approx(0.0)


def test_second_virial_coefficient_keeps_previous_kelvin_behavior() -> None:
    temperature = 100.0
    value, _ = second_virial_coefficient(
        temperature=temperature,
        potential_func=positive_temperature_potential,
        parameters={"temperature": temperature},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=1.0,
        energy_unit="kelvin",
    )
    expected_integral_factor = (1.0 - math.exp(-1.0)) / 3.0
    expected = 2.0 * math.pi * AVOGADRO_CONSTANT * expected_integral_factor * 1e-24

    assert value == pytest.approx(expected)


def test_second_virial_coefficient_is_positive_for_constant_repulsive_potential() -> None:
    temperature = 100.0
    value, _ = second_virial_coefficient(
        temperature=temperature,
        potential_func=positive_temperature_potential,
        parameters={"temperature": temperature},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=1.0,
    )

    assert value > 0.0


def test_second_virial_coefficient_is_negative_for_constant_attractive_potential() -> None:
    temperature = 100.0
    value, _ = second_virial_coefficient(
        temperature=temperature,
        potential_func=negative_temperature_potential,
        parameters={"temperature": temperature},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=1.0,
    )

    assert value < 0.0


def test_second_virial_coefficient_returns_value_error_tuple() -> None:
    result = second_virial_coefficient(
        temperature=100.0,
        potential_func=zero_potential,
        parameters={},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=1.0,
    )

    assert isinstance(result, tuple)
    assert len(result) == 2


def test_second_virial_coefficient_unit_conversion_is_consistent_between_angstrom_and_pm() -> None:
    temperature = 100.0
    expected_integral_factor = (1.0 - math.exp(-1.0)) / 3.0
    expected_angstrom = 2.0 * math.pi * AVOGADRO_CONSTANT * expected_integral_factor * 1e-24

    value_angstrom, _ = second_virial_coefficient(
        temperature=temperature,
        potential_func=positive_temperature_potential,
        parameters={"temperature": temperature},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=1.0,
        distance_unit="angstrom",
    )
    value_pm, _ = second_virial_coefficient(
        temperature=temperature,
        potential_func=positive_temperature_potential,
        parameters={"temperature": temperature},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=100.0,
        distance_unit="pm",
    )

    assert value_angstrom == pytest.approx(expected_angstrom)
    assert value_pm == pytest.approx(value_angstrom)


def test_second_virial_coefficient_converts_kcal_per_mol_to_kelvin() -> None:
    value_kcal, _ = second_virial_coefficient(
        temperature=300.0,
        potential_func=one_kcal_per_mol_potential,
        parameters={},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=1.0,
        energy_unit="kcal/mol",
    )
    value_kelvin, _ = second_virial_coefficient(
        temperature=300.0,
        potential_func=one_kcal_per_mol_in_kelvin_potential,
        parameters={},
        integrator=ScipyQuadIntegrator(),
        r_min=0.0,
        r_max=1.0,
        energy_unit="kelvin",
    )

    assert value_kcal == pytest.approx(value_kelvin)


def test_second_virial_coefficient_raises_error_for_invalid_energy_unit() -> None:
    with pytest.raises(ValueError, match="Unsupported energy_unit"):
        second_virial_coefficient(
            temperature=300.0,
            potential_func=one_kcal_per_mol_potential,
            parameters={},
            integrator=ScipyQuadIntegrator(),
            r_min=0.0,
            r_max=1.0,
            energy_unit="hartree",
        )
