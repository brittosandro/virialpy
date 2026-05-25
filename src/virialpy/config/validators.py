"""Validation helpers for run configuration files."""

from __future__ import annotations

from numbers import Real
from typing import Any


def _require_section(config: dict[str, Any], section: str) -> dict[str, Any]:
    if section not in config:
        raise ValueError(f"Missing required section: {section}")
    value = config[section]
    if section == "system":
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Section '{section}' must be a mapping.")
    return value


def _require_fields(section: dict[str, Any], section_name: str, fields: list[str]) -> None:
    missing = [field for field in fields if field not in section]
    if missing:
        raise ValueError(
            f"Section '{section_name}' is missing required field(s): {', '.join(missing)}"
        )


def validate_run_config(config: dict[str, Any]) -> None:
    """Validate the structure and basic types of a YAML run configuration."""
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary.")

    required_sections = ["system", "data", "models", "integrators", "units", "b2", "outputs", "run"]
    for section in required_sections:
        _require_section(config, section)

    data = _require_section(config, "data")
    models = _require_section(config, "models")
    integrators = _require_section(config, "integrators")
    units = _require_section(config, "units")
    b2 = _require_section(config, "b2")
    outputs = _require_section(config, "outputs")
    run = _require_section(config, "run")

    _require_fields(
        data,
        "data",
        [
            "potential_data",
            "experimental_data",
            "r_column",
            "energy_column",
            "temperature_column",
            "b2_column",
        ],
    )
    _require_fields(models, "models", ["potentials"])
    _require_fields(integrators, "integrators", ["names"])
    _require_fields(units, "units", ["distance_unit", "energy_unit"])
    _require_fields(b2, "b2", ["r_min", "r_max"])
    _require_fields(outputs, "outputs", ["results_dir", "figures_dir", "reports_dir"])
    _require_fields(run, "run", ["fit", "b2", "validate"])

    if not isinstance(models["potentials"], list):
        raise ValueError("models.potentials must be a list.")
    if not isinstance(integrators["names"], list):
        raise ValueError("integrators.names must be a list.")
    if not isinstance(b2["r_min"], Real) or not isinstance(b2["r_max"], Real):
        raise ValueError("b2.r_min and b2.r_max must be numeric.")
    if b2["r_max"] <= b2["r_min"]:
        raise ValueError("b2.r_max must be greater than b2.r_min.")

    for field in ["fit", "b2", "validate"]:
        if not isinstance(run[field], bool):
            raise ValueError(f"run.{field} must be a boolean.")
    if "monte_carlo_plots" in run and not isinstance(run["monte_carlo_plots"], bool):
        raise ValueError("run.monte_carlo_plots must be a boolean.")
    for field in ["partitioned", "method_comparison", "final_outputs"]:
        if field in run and not isinstance(run[field], bool):
            raise ValueError(f"run.{field} must be a boolean.")

    if "partitioned" in config:
        partitioned = _require_section(config, "partitioned")
        _require_fields(partitioned, "partitioned", ["enabled"])
        if not isinstance(partitioned["enabled"], bool):
            raise ValueError("partitioned.enabled must be a boolean.")
        if partitioned["enabled"]:
            _require_fields(partitioned, "partitioned", ["r1", "r2", "r3", "r4"])
            limits = [partitioned[key] for key in ["r1", "r2", "r3", "r4"]]
            if not all(isinstance(value, Real) for value in limits):
                raise ValueError("partitioned.r1, r2, r3 and r4 must be numeric.")
            r1, r2, r3, r4 = limits
            if not (0 < r1 < r2 < r3 < r4):
                raise ValueError("partitioned limits must obey 0 < r1 < r2 < r3 < r4.")
            for field in ["integrator_b2", "integrator_b3", "integrator_b4"]:
                if field in partitioned:
                    integrator_config = partitioned[field]
                    if not isinstance(integrator_config, dict):
                        raise ValueError(f"partitioned.{field} must be a mapping.")
                    if "name" not in integrator_config:
                        raise ValueError(f"partitioned.{field} must contain a 'name' field.")
