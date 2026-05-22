import numpy as np
import pytest

from virialpy.potentials import POTENTIALS, improved_lennard_jones, lennard_jones, rydberg6


def test_lennard_jones_is_zero_at_sigma() -> None:
    assert lennard_jones(r=3.4, epsilon=120.0, sigma=3.4) == pytest.approx(0.0)


def test_lennard_jones_minimum_is_minus_epsilon() -> None:
    epsilon = 120.0
    sigma = 3.4
    r_min = 2.0 ** (1.0 / 6.0) * sigma

    assert lennard_jones(r=r_min, epsilon=epsilon, sigma=sigma) == pytest.approx(-epsilon)


def test_improved_lennard_jones_minimum_is_minus_de() -> None:
    assert improved_lennard_jones(r=3.75, de=100.0, req=3.75, beta=8.0) == pytest.approx(-100.0)


def test_rydberg6_minimum_is_minus_de() -> None:
    assert rydberg6(
        r=3.75,
        de=100.0,
        re=3.75,
        c1=1.0,
        c2=0.2,
        c3=0.03,
        c4=0.004,
        c5=0.0005,
        c6=0.00006,
    ) == pytest.approx(-100.0)


def test_potentials_accept_numpy_arrays() -> None:
    r = np.array([3.4, 3.8, 4.2])

    lj_values = lennard_jones(r, epsilon=120.0, sigma=3.4)
    ilj_values = improved_lennard_jones(r, de=100.0, req=3.75, beta=8.0)
    ryd_values = rydberg6(r, de=100.0, re=3.75, c1=1.0, c2=0.2, c3=0.03, c4=0.004, c5=0.0005, c6=0.00006)

    assert isinstance(lj_values, np.ndarray)
    assert isinstance(ilj_values, np.ndarray)
    assert isinstance(ryd_values, np.ndarray)
    assert lj_values.shape == r.shape
    assert ilj_values.shape == r.shape
    assert ryd_values.shape == r.shape


def test_registry_contains_builtin_potentials() -> None:
    assert {"lj", "ilj", "ryd6"}.issubset(POTENTIALS)


def test_imported_potentials_work_from_package_namespace() -> None:
    assert POTENTIALS["lj"](3.4, epsilon=120.0, sigma=3.4) == pytest.approx(0.0)
    assert improved_lennard_jones(3.75, de=100.0, req=3.75, beta=8.0) == pytest.approx(-100.0)
    assert rydberg6(3.75, de=100.0, re=3.75, c1=1.0, c2=0.2, c3=0.03, c4=0.004, c5=0.0005, c6=0.00006) == pytest.approx(-100.0)

