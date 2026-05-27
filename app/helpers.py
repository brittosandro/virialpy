"""Helper functions for the virialpy Streamlit app."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from virialpy.potentials import POTENTIALS


def safe_system_name(name: str) -> str:
    """Return a filesystem-friendly system name."""
    cleaned = name.strip().lower()
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"[^a-z0-9_-]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        raise ValueError("System name cannot be empty.")
    return cleaned


def _safe_filename(filename: str) -> str:
    """Return a conservative uploaded filename."""
    cleaned = filename.strip().replace(" ", "_")
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", cleaned)
    return cleaned or "uploaded.csv"


def save_uploaded_file(uploaded_file: Any, destination_dir: str | Path) -> Path:
    """Save an uploaded file-like object to a destination directory."""
    destination = Path(destination_dir)
    destination.mkdir(parents=True, exist_ok=True)
    filename = _safe_filename(getattr(uploaded_file, "name", "uploaded.csv"))
    output_path = destination / filename

    if hasattr(uploaded_file, "getbuffer"):
        content = uploaded_file.getbuffer()
    elif hasattr(uploaded_file, "read"):
        content = uploaded_file.read()
    else:
        raise ValueError("uploaded_file must provide getbuffer() or read().")

    output_path.write_bytes(bytes(content))
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    return output_path


def load_csv_preview(uploaded_file_or_path: Any) -> pd.DataFrame:
    """Load a CSV preview from an uploaded file or path."""
    if hasattr(uploaded_file_or_path, "seek"):
        uploaded_file_or_path.seek(0)
    data = pd.read_csv(uploaded_file_or_path)
    if hasattr(uploaded_file_or_path, "seek"):
        uploaded_file_or_path.seek(0)
    return data


def build_yaml_config(
    system_name: str,
    potential_data_path: str | Path,
    experimental_data_path: str | Path,
    r_column: str,
    energy_column: str,
    temperature_column: str,
    b2_column: str,
    potentials: list[str],
    integrators: list[str],
    distance_unit: str,
    energy_unit: str,
    r_min: float,
    r_max: float,
    enable_partitioned: bool,
    r1: float,
    r2: float,
    r3: float,
    r4: float,
    n_points_b2: int,
    n_points_b3: int,
    n_points_b4: int,
    run_fit: bool,
    run_b2: bool,
    run_validate: bool,
    run_partitioned: bool,
    run_method_comparison: bool,
    run_monte_carlo_plots: bool,
    run_final_outputs: bool,
) -> dict[str, Any]:
    """Build a run_from_config-compatible YAML configuration dictionary."""
    safe_name = safe_system_name(system_name)
    suffix = f"{safe_name}_streamlit"
    config: dict[str, Any] = {
        "system": safe_name,
        "data": {
            "potential_data": str(potential_data_path),
            "experimental_data": str(experimental_data_path),
            "r_column": r_column,
            "energy_column": energy_column,
            "temperature_column": temperature_column,
            "b2_column": b2_column,
        },
        "models": {"potentials": list(potentials)},
        "integrators": {"names": list(integrators)},
        "units": {"distance_unit": distance_unit, "energy_unit": energy_unit},
        "b2": {"r_min": float(r_min), "r_max": float(r_max)},
        "partitioned": {
            "enabled": bool(enable_partitioned),
            "r1": float(r1),
            "r2": float(r2),
            "r3": float(r3),
            "r4": float(r4),
            "integrator_b2": {"name": "gaussian", "n_points": int(n_points_b2)},
            "integrator_b3": {"name": "gaussian", "n_points": int(n_points_b3)},
            "integrator_b4": {"name": "gaussian", "n_points": int(n_points_b4)},
        },
        "outputs": {
            "results_dir": f"data/results/{suffix}",
            "figures_dir": f"outputs/figures/{suffix}",
            "reports_dir": f"outputs/reports/{suffix}",
        },
        "run": {
            "fit": bool(run_fit),
            "b2": bool(run_b2),
            "validate": bool(run_validate),
            "partitioned": bool(run_partitioned),
            "method_comparison": bool(run_method_comparison),
            "monte_carlo_plots": bool(run_monte_carlo_plots),
            "final_outputs": bool(run_final_outputs),
        },
    }
    return config


def save_yaml_config(config: dict[str, Any], path: str | Path) -> Path:
    """Save a YAML configuration to disk."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return output_path


def paths_for_system(system_name: str) -> dict[str, Path]:
    """Return standard Streamlit paths for a system."""
    safe_name = safe_system_name(system_name)
    suffix = f"{safe_name}_streamlit"
    return {
        "raw_dir": Path("data/raw") / safe_name,
        "results_dir": Path("data/results") / suffix,
        "figures_dir": Path("outputs/figures") / suffix,
        "reports_dir": Path("outputs/reports") / suffix,
        "config_path": Path("configs/generated") / f"{suffix}.yaml",
    }


def results_exist(results_dir: str | Path) -> bool:
    """Return True when a results directory exists and contains files."""
    path = Path(results_dir)
    return path.exists() and any(path.rglob("*"))


def fit_results_exist(results_dir: str | Path, potentials: list[str]) -> bool:
    """Return True when all selected potentials have fitted parameter files."""
    path = Path(results_dir)
    return all((path / potential / "fit_parameters.csv").exists() for potential in potentials)


def b2_results_exist(results_dir: str | Path) -> bool:
    """Return True when direct B(T) results exist."""
    return (Path(results_dir) / "b2_comparison_all.csv").exists()


def validation_results_exist(results_dir: str | Path) -> bool:
    """Return True when B(T) validation metrics exist."""
    return (Path(results_dir) / "b2_experiment_metrics.csv").exists()


def list_existing_figures(figures_dir: str | Path) -> list[Path]:
    """List generated figure files under a figure directory."""
    path = Path(figures_dir)
    if not path.exists():
        return []
    return sorted(file for file in path.rglob("*") if file.is_file() and file.suffix.lower() in {".png", ".jpg", ".jpeg"})


def workflow_step_status(completed: bool, ready: bool) -> str:
    """Return a compact status label for a workflow step."""
    if completed:
        return "Completed"
    if ready:
        return "Ready"
    return "Pending"


def dataframe_from_csv_if_exists(path: str | Path) -> pd.DataFrame | None:
    """Load a CSV file if it exists, otherwise return None."""
    csv_path = Path(path)
    if not csv_path.exists():
        return None
    return pd.read_csv(csv_path)


def image_if_exists(path: str | Path) -> Path | None:
    """Return an image path if it exists."""
    image_path = Path(path)
    return image_path if image_path.exists() else None


def list_files_safe(path: str | Path, pattern: str = "*") -> list[Path]:
    """List files matching a pattern, returning an empty list for missing directories."""
    directory = Path(path)
    if not directory.exists():
        return []
    return sorted(file for file in directory.glob(pattern) if file.is_file())


def display_table_if_exists(path: str | Path, label: str) -> tuple[str, pd.DataFrame | None]:
    """Return a label and optional table for UI display."""
    return label, dataframe_from_csv_if_exists(path)


def display_image_if_exists(path: str | Path, caption: str) -> tuple[str, Path | None]:
    """Return a caption and optional image path for UI display."""
    return caption, image_if_exists(path)


def file_exists(path: str | Path) -> bool:
    """Return True when a file exists."""
    return Path(path).is_file()


def read_file_bytes(path: str | Path) -> bytes | None:
    """Read file bytes if a file exists."""
    file_path = Path(path)
    if not file_path.is_file():
        return None
    return file_path.read_bytes()


def summarize_output_availability(
    results_dir: str | Path,
    figures_dir: str | Path,
    reports_dir: str | Path,
    config_path: str | Path | None = None,
) -> dict[str, bool]:
    """Summarize whether the main Streamlit workflow outputs are available."""
    results = Path(results_dir)
    figures = Path(figures_dir)
    reports = Path(reports_dir)
    return {
        "Fit results": (results / "fit_comparison_metrics.csv").exists(),
        "B2 validation results": (results / "b2_experiment_metrics.csv").exists(),
        "Direct vs partitioned results": (results / "b2_method_experiment_metrics.csv").exists(),
        "Monte Carlo comparison": (results / "monte_carlo_comparison_summary.csv").exists(),
        "Final figures": (figures / "final").exists() and any((figures / "final").glob("*.png")),
        "Final tables": (reports / "tables").exists() and any((reports / "tables").glob("*")),
        "YAML configuration": bool(config_path and Path(config_path).exists()),
    }


def unique_downloads(downloads: list[tuple[Path, str, str]]) -> list[tuple[Path, str, str]]:
    """Remove duplicate downloads by path while preserving order."""
    seen: set[str] = set()
    unique: list[tuple[Path, str, str]] = []
    for path, label, mime in downloads:
        normalized = str(Path(path))
        if normalized in seen:
            continue
        seen.add(normalized)
        unique.append((Path(path), label, mime))
    return unique


def existing_fitted_potentials(results_dir: str | Path) -> list[str]:
    """Return potentials that have fitted parameter files in a results directory."""
    path = Path(results_dir)
    if not path.exists():
        return []
    return sorted(
        potential_dir.name
        for potential_dir in path.iterdir()
        if potential_dir.is_dir() and (potential_dir / "fit_parameters.csv").exists()
    )


def existing_integrators_in_b2_results(results_dir: str | Path) -> list[str]:
    """Return integrator names present in b2_comparison_all.csv."""
    path = Path(results_dir) / "b2_comparison_all.csv"
    if not path.exists():
        return []
    data = pd.read_csv(path)
    if "integrator" not in data.columns:
        return []
    return sorted(str(value) for value in data["integrator"].dropna().unique())


def _load_fit_parameters(path: Path) -> dict[str, float]:
    data = pd.read_csv(path)
    required = {"parameter", "value"}
    if not required.issubset(data.columns):
        raise ValueError(f"Fit parameter file must contain columns: {sorted(required)}")
    return {str(row["parameter"]): float(row["value"]) for _, row in data.iterrows()}


def build_fitted_curves_dataframe(
    potential_data_df: pd.DataFrame,
    results_dir: str | Path,
    potentials: list[str],
    n_points: int = 500,
) -> pd.DataFrame:
    """Build smooth fitted U(r) curves from saved fit parameters."""
    if not {"r", "energy"}.issubset(potential_data_df.columns):
        raise ValueError('potential_data_df must contain columns "r" and "energy".')
    r_values = pd.to_numeric(potential_data_df["r"], errors="coerce").dropna()
    if r_values.empty:
        return pd.DataFrame(columns=["r", "energy_fit", "potential"])

    r_grid = np.linspace(float(r_values.min()), float(r_values.max()), int(n_points))
    rows: list[pd.DataFrame] = []
    base_dir = Path(results_dir)
    for potential in potentials:
        parameter_path = base_dir / potential / "fit_parameters.csv"
        if not parameter_path.exists() or potential not in POTENTIALS:
            continue
        try:
            parameters = _load_fit_parameters(parameter_path)
            energy_fit = POTENTIALS[potential](r_grid, **parameters)
            rows.append(pd.DataFrame({"r": r_grid, "energy_fit": energy_fit, "potential": potential}))
        except Exception:
            continue
    if not rows:
        return pd.DataFrame(columns=["r", "energy_fit", "potential"])
    return pd.concat(rows, ignore_index=True)


def build_fit_residuals_dataframe(results_dir: str | Path, potentials: list[str]) -> pd.DataFrame | None:
    """Combine saved fit residual files into one long DataFrame."""
    frames: list[pd.DataFrame] = []
    base_dir = Path(results_dir)
    for potential in potentials:
        residual_path = base_dir / potential / "fit_residuals.csv"
        if not residual_path.exists():
            continue
        data = pd.read_csv(residual_path)
        data = data.rename(
            columns={
                "energy_fit": "energy_fitted",
                "fitted": "energy_fitted",
                "observed": "energy_observed",
            }
        )
        data["potential"] = potential
        frames.append(data)
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)
