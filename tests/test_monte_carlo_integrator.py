import math

import numpy as np
import pytest

from virialpy.integrators import MonteCarloIntegrator


def test_monte_carlo_integrates_x_squared() -> None:
    value, _ = MonteCarloIntegrator(n_samples=200000, random_state=1).integrate(
        lambda x: x**2,
        0.0,
        1.0,
    )

    assert value == pytest.approx(1.0 / 3.0, rel=1e-2)


def test_monte_carlo_integrates_sine() -> None:
    value, _ = MonteCarloIntegrator(n_samples=200000, random_state=2).integrate(
        np.sin,
        0.0,
        math.pi,
    )

    assert value == pytest.approx(2.0, rel=1e-2)


def test_monte_carlo_returns_non_negative_error() -> None:
    _, error = MonteCarloIntegrator(n_samples=10000, random_state=3).integrate(
        lambda x: x**2,
        0.0,
        1.0,
    )

    assert error >= 0.0


def test_monte_carlo_is_reproducible_with_fixed_random_state() -> None:
    integrator_a = MonteCarloIntegrator(n_samples=10000, random_state=42)
    integrator_b = MonteCarloIntegrator(n_samples=10000, random_state=42)

    result_a = integrator_a.integrate(lambda x: x**2, 0.0, 1.0)
    result_b = integrator_b.integrate(lambda x: x**2, 0.0, 1.0)

    assert result_a == result_b


def test_monte_carlo_raises_error_for_non_positive_samples() -> None:
    with pytest.raises(ValueError, match="n_samples"):
        MonteCarloIntegrator(n_samples=0)


def test_monte_carlo_raises_error_when_upper_is_not_greater_than_lower() -> None:
    with pytest.raises(ValueError, match="upper bound"):
        MonteCarloIntegrator().integrate(lambda x: x, 1.0, 1.0)


def test_monte_carlo_returns_value_error_tuple() -> None:
    result = MonteCarloIntegrator(n_samples=1000, random_state=4).integrate(
        lambda x: x,
        0.0,
        1.0,
    )

    assert isinstance(result, tuple)
    assert len(result) == 2


def test_monte_carlo_falls_back_to_scalar_function() -> None:
    def scalar_function(x):
        if isinstance(x, np.ndarray):
            raise TypeError("scalar only")
        return x**2

    value, _ = MonteCarloIntegrator(n_samples=200000, random_state=5).integrate(
        scalar_function,
        0.0,
        1.0,
    )

    assert value == pytest.approx(1.0 / 3.0, rel=1e-2)

