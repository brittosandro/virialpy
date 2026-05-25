"""Numerical integration strategies.

Integrators used by virial calculations should live here so alternative
quadrature methods can be added without changing virial-domain code.
"""

from virialpy.integrators.base import BaseIntegrator
from virialpy.integrators.gaussian_quadrature import GaussianQuadratureIntegrator
from virialpy.integrators.monte_carlo import MonteCarloIntegrator
from virialpy.integrators.scipy_quad import ScipyQuadIntegrator
from virialpy.integrators.simpson import SimpsonIntegrator
from virialpy.integrators.trapezoid import TrapezoidIntegrator

__all__ = [
    "BaseIntegrator",
    "GaussianQuadratureIntegrator",
    "MonteCarloIntegrator",
    "ScipyQuadIntegrator",
    "SimpsonIntegrator",
    "TrapezoidIntegrator",
]
