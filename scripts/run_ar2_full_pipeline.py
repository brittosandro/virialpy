"""Run the complete reproducible Ar2 workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPTS = [
    "run_compare_potentials_ar2.py",
    "run_b2_comparison_ar2.py",
    "run_b2_validation_ar2.py",
    "run_partitioned_b2_ar2.py",
    "run_b2_method_comparison_ar2.py",
    "run_monte_carlo_comparison_ar2.py",
    "gerar_figuras_tabelas_finais_ar2.py",
]


def main() -> None:
    """Execute the Ar2 pipeline scripts in the recommended order."""
    scripts_dir = Path(__file__).resolve().parent
    repo_root = scripts_dir.parent

    for script_name in SCRIPTS:
        script_path = scripts_dir / script_name
        print(f"Running {script_name}...")
        subprocess.run([sys.executable, str(script_path)], cwd=repo_root, check=True)

    print("Ar2 full pipeline completed successfully.")


if __name__ == "__main__":
    main()
