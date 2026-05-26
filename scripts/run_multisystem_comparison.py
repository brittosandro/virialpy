"""Generate Ar2 vs Kr2 multi-system comparison outputs."""

from __future__ import annotations

from virialpy.workflows import run_multisystem_comparison_workflow


def main() -> None:
    """Run the multi-system comparison for available Ar2 and Kr2 outputs."""
    outputs = run_multisystem_comparison_workflow(
        systems=[
            {"system": "Ar2", "results_dir": "data/results/ar2_config"},
            {"system": "Kr2", "results_dir": "data/results/kr2_config"},
        ],
        results_dir="data/results/multisystem",
        figures_dir="outputs/figures/multisystem",
        reports_dir="outputs/reports/multisystem",
    )
    print(f"Resultados multi-sistema em: {outputs['results_dir']}")
    print(f"Figuras multi-sistema em: {outputs['figures_dir']}")
    print(f"Tabelas multi-sistema em: {outputs['tables_dir']}")


if __name__ == "__main__":
    main()
