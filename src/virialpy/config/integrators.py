"""Build numerical integrators from configuration dictionaries."""

from __future__ import annotations

from typing import Any

from virialpy.integrators import (
    GaussianQuadratureIntegrator,
    MonteCarloIntegrator,
    ScipyQuadIntegrator,
    SimpsonIntegrator,
    TrapezoidIntegrator,
)


def create_integrator_from_config(config: dict[str, Any]):
    """Create an integrator from a YAML configuration mapping."""
    if not isinstance(config, dict):
        raise ValueError("Integrator configuration must be a mapping.")
    if "name" not in config:
        raise ValueError("Integrator configuration must contain a 'name' field.")

    name = str(config["name"])
    if name == "scipy_quad":
        return ScipyQuadIntegrator(
            epsabs=float(config.get("epsabs", 1e-10)),
            epsrel=float(config.get("epsrel", 1e-10)),
            limit=int(config.get("limit", 500)),
        )
    if name == "gaussian":
        return GaussianQuadratureIntegrator(n_points=int(config.get("n_points", 64)))
    if name == "simpson":
        return SimpsonIntegrator(n_points=int(config.get("n_points", 10001)))
    if name == "trapezoid":
        return TrapezoidIntegrator(n_points=int(config.get("n_points", 10000)))
    if name == "monte_carlo":
        random_state = config.get("random_state", None)
        return MonteCarloIntegrator(
            n_samples=int(config.get("n_samples", 100000)),
            random_state=random_state,
        )

    raise ValueError(f"Unsupported integrator '{name}'.")
