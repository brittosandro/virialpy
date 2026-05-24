import math

import numpy as np
import pytest

from virialpy.integrators import (
    GaussianQuadratureIntegrator,
    ScipyQuadIntegrator,
    SimpsonIntegrator,
    TrapezoidIntegrator,
)


def _integrators():
    return [
        ScipyQuadIntegrator(),
        GaussianQuadratureIntegrator(),
        SimpsonIntegrator(),
        TrapezoidIntegrator(),
    ]


def test_scipy_quad_integrates_x_squared() -> None:
    value, _ = ScipyQuadIntegrator().integrate(lambda x: x**2, 0.0, 1.0)

    assert value == pytest.approx(1.0 / 3.0)


def test_gaussian_quadrature_integrates_x_squared() -> None:
    value, _ = GaussianQuadratureIntegrator().integrate(lambda x: x**2, 0.0, 1.0)

    assert value == pytest.approx(1.0 / 3.0)


def test_simpson_integrates_x_squared() -> None:
    value, _ = SimpsonIntegrator().integrate(lambda x: x**2, 0.0, 1.0)

    assert value == pytest.approx(1.0 / 3.0)


def test_trapezoid_integrates_x_squared() -> None:
    value, _ = TrapezoidIntegrator().integrate(lambda x: x**2, 0.0, 1.0)

    assert value == pytest.approx(1.0 / 3.0, rel=1e-7)


def test_scipy_quad_integrates_sine() -> None:
    value, _ = ScipyQuadIntegrator().integrate(math.sin, 0.0, math.pi)

    assert value == pytest.approx(2.0)


def test_gaussian_quadrature_integrates_sine() -> None:
    value, _ = GaussianQuadratureIntegrator().integrate(np.sin, 0.0, math.pi)

    assert value == pytest.approx(2.0)


@pytest.mark.parametrize("integrator", _integrators())
@pytest.mark.parametrize("lower, upper", [(1.0, 1.0), (2.0, 1.0)])
def test_integrators_raise_error_when_upper_is_not_greater_than_lower(integrator, lower, upper) -> None:
    with pytest.raises(ValueError, match="upper bound"):
        integrator.integrate(lambda x: x**2, lower, upper)


@pytest.mark.parametrize("integrator", _integrators())
def test_integrators_return_value_error_tuple(integrator) -> None:
    result = integrator.integrate(lambda x: x**2, 0.0, 1.0)

    assert isinstance(result, tuple)
    assert len(result) == 2

