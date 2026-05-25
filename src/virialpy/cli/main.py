"""Command-line interface for virialpy."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import typer


app = typer.Typer(help="Scientific tools for virial coefficient workflows.")
ar2_app = typer.Typer(help="Run reproducible Ar2 workflows.")
app.add_typer(ar2_app, name="ar2")


def _run_script(script_name: str, description: str) -> None:
    """Run a project script from the repository root."""
    repo_root = Path.cwd()
    script_path = repo_root / "scripts" / script_name
    if not script_path.exists():
        raise typer.BadParameter(f"Script not found: {script_path}")

    typer.echo(f"Starting: {description}")
    try:
        subprocess.run([sys.executable, str(script_path)], cwd=repo_root, check=True)
    except subprocess.CalledProcessError as exc:
        raise typer.Exit(code=exc.returncode) from exc
    typer.echo(f"Finished: {description}")


@ar2_app.command()
def fit() -> None:
    """Fit and compare Ar2 intermolecular potentials."""
    _run_script("run_compare_potentials_ar2.py", "Ar2 potential fitting")


@ar2_app.command()
def b2() -> None:
    """Calculate direct B(T) values for Ar2 potentials and integrators."""
    _run_script("run_b2_comparison_ar2.py", "Ar2 direct B(T) comparison")


@ar2_app.command()
def validate() -> None:
    """Validate calculated Ar2 B(T) values against experiment."""
    _run_script("run_b2_validation_ar2.py", "Ar2 B(T) experimental validation")


@ar2_app.command()
def partitioned() -> None:
    """Calculate partitioned B(T) values for Ar2."""
    _run_script("run_partitioned_b2_ar2.py", "Ar2 partitioned B(T)")


@ar2_app.command()
def methods() -> None:
    """Compare direct and partitioned Ar2 B(T) methods."""
    _run_script("run_b2_method_comparison_ar2.py", "Ar2 B(T) method comparison")


@ar2_app.command("monte-carlo")
def monte_carlo() -> None:
    """Compare Monte Carlo integration with other Ar2 integrators."""
    _run_script("run_monte_carlo_comparison_ar2.py", "Ar2 Monte Carlo comparison")


@ar2_app.command()
def figures() -> None:
    """Generate final Ar2 figures and report tables."""
    _run_script("gerar_figuras_tabelas_finais_ar2.py", "Ar2 final figures and tables")


@ar2_app.command("full-pipeline")
def full_pipeline() -> None:
    """Run the complete reproducible Ar2 pipeline."""
    _run_script("run_ar2_full_pipeline.py", "Ar2 full pipeline")

