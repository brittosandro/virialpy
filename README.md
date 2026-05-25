# virialpy

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-green)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)](LICENSE)

`virialpy` is a scientific Python package for fitting intermolecular potentials `U(r)`, calculating the second virial coefficient `B(T)`, comparing calculated values with experimental data, evaluating numerical integrators and generating figures and tables for scientific analysis.

The current reproducible case study is Ar2, including LJ, ILJ and Rydberg6 potentials, direct and partitioned virial integration, Monte Carlo comparisons and publication-style outputs.

## Scientific Motivation

The second virial coefficient connects the macroscopic behavior of real gases with microscopic pair interactions. By fitting intermolecular potentials and propagating them into `B(T)`, `virialpy` helps evaluate how model choices, integration strategies and fitted parameters affect thermodynamic predictions.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
pytest
virialpy ar2 full-pipeline
```

## Main Features

- Read theoretical potential energy data `U(r)`.
- Read experimental virial coefficient data.
- Evaluate LJ, ILJ and Rydberg6 intermolecular potentials.
- Fit potentials with SciPy.
- Export fitted parameters, residuals and metrics.
- Generate individual and comparative fit plots.
- Integrate with SciPy quad, Gauss-Legendre, Simpson, trapezoid and Monte Carlo.
- Calculate direct `B(T)`.
- Calculate partitioned `B(T)` in radial regions.
- Compare calculated values with experiment.
- Calculate statistical metrics.
- Export final tables in CSV and LaTeX.
- Generate final figures for reports, articles and dissertations.
- Run the Ar2 workflow from a Typer command-line interface.

## Ar2 Reproducible Workflow

The complete Ar2 workflow can be executed with:

```bash
virialpy ar2 full-pipeline
```

Equivalent scripts remain available in `scripts/` for transparency and reproducibility:

```bash
python3 scripts/run_compare_potentials_ar2.py
python3 scripts/run_b2_comparison_ar2.py
python3 scripts/run_b2_validation_ar2.py
python3 scripts/run_partitioned_b2_ar2.py
python3 scripts/run_b2_method_comparison_ar2.py
python3 scripts/run_monte_carlo_comparison_ar2.py
python3 scripts/gerar_figuras_tabelas_finais_ar2.py
```

## Command-Line Interface

After installing in editable mode, use:

```bash
virialpy --help
virialpy ar2 --help
virialpy ar2 fit
virialpy ar2 b2
virialpy ar2 validate
virialpy ar2 partitioned
virialpy ar2 methods
virialpy ar2 monte-carlo
virialpy ar2 figures
virialpy ar2 full-pipeline
```

The CLI calls the existing reproducible scripts and is the recommended terminal interface for the Ar2 case study.

The general CLI can run workflows from user-provided paths and column names:

```bash
virialpy run fit \
    --system ar2 \
    --potential-data data/raw/ar2/ar2_cep_bsse.csv \
    --r-column "r(angstrom)" \
    --energy-column "E_int_CP(kcal/mol)" \
    --potentials all \
    --output-dir data/results/ar2_general_cli

virialpy run b2 \
    --system ar2 \
    --experimental-data data/raw/ar2/b2_experimental.csv \
    --temperature-column "Temperatura" \
    --potentials all \
    --integrators all \
    --results-dir data/results/ar2_general_cli \
    --energy-unit "kcal/mol" \
    --distance-unit angstrom \
    --r-min 2.5 \
    --r-max 30.0

virialpy run validate \
    --system ar2 \
    --experimental-data data/raw/ar2/b2_experimental.csv \
    --temperature-column "Temperatura" \
    --b2-column "B(segundo coef. virial) [cm³/mol]" \
    --results-dir data/results/ar2_general_cli \
    --figures-dir outputs/figures/ar2_general_cli

virialpy run full \
    --system ar2 \
    --potential-data data/raw/ar2/ar2_cep_bsse.csv \
    --experimental-data data/raw/ar2/b2_experimental.csv \
    --r-column "r(angstrom)" \
    --energy-column "E_int_CP(kcal/mol)" \
    --temperature-column "Temperatura" \
    --b2-column "B(segundo coef. virial) [cm³/mol]" \
    --potentials all \
    --integrators all \
    --energy-unit "kcal/mol" \
    --distance-unit angstrom \
    --r-min 2.5 \
    --r-max 30.0 \
    --results-dir data/results/ar2_general_cli \
    --figures-dir outputs/figures/ar2_general_cli \
    --reports-dir outputs/reports/ar2_general_cli
```

## YAML Configuration

The same general workflow can be described in a YAML file and executed with one command:

```bash
virialpy run-config configs/ar2.yaml
```

The example [configs/ar2.yaml](configs/ar2.yaml) defines the molecular system, input files, column names, potentials, integrators, units, integration bounds and output directories. See [docs/configuration.md](docs/configuration.md) for the full configuration reference.

YAML execution can control potential fitting, direct `B(T)`, experimental validation, partitioned `B(T)`, direct-vs-partitioned comparison, Monte Carlo plots, final figures and final CSV/LaTeX tables.

## Outputs

Project outputs follow these conventions:

```text
data/results/<system>/<model>/
outputs/figures/<system>/<stage>/
outputs/reports/<system>/tables/
```

For Ar2, the final figures and tables are generated in:

```text
outputs/figures/ar2/final/
outputs/reports/ar2/tables/
```

Large generated files should be avoided in Git. Small raw example datasets required to reproduce the Ar2 study may be kept in `data/raw/`; large raw datasets should be documented and stored externally.

## Project Structure

```text
virialpy/
├── data/
├── docs/
├── examples/
├── legacy/
├── outputs/
├── scripts/
├── src/virialpy/
└── tests/
```

- `data/`: raw example data and generated numerical results.
- `docs/`: workflow, data-format and developer documentation.
- `examples/`: example systems and templates.
- `legacy/`: reference scripts used during scientific development.
- `outputs/`: generated figures, reports and final tables.
- `scripts/`: reproducible Ar2 execution scripts.
- `src/virialpy/`: package source code.
- `tests/`: automated test suite.

## Input Data Format

Potential data can use the default columns:

```csv
r,energy
3.0,1.2
3.5,-0.1
4.0,-0.2
```

Custom columns are also supported:

```csv
r(angstrom),E_int_CP(kcal/mol)
3.0,2.078
3.5,-0.120
4.0,-0.230
```

Experimental data can use:

```csv
temperature,b2
100,-180.0
200,-45.0
```

The Ar2 experimental file currently uses:

```csv
Temperatura,B(segundo coef. virial) [cm³/mol]
100.3086419753086,-183.7441314553991
```

## Python Examples

Fit a Lennard-Jones potential directly:

```python
from virialpy.datasets import load_potential_data
from virialpy.fitting import fit_potential_scipy
from virialpy.potentials import lennard_jones

data = load_potential_data(
    "data/raw/ar2/ar2_cep_bsse.csv",
    r_column="r(angstrom)",
    energy_column="E_int_CP(kcal/mol)",
)

result = fit_potential_scipy(
    data=data,
    potential_func=lennard_jones,
    initial_guess=[0.25, 3.5],
    parameter_names=["epsilon", "sigma"],
    potential_name="lj",
)
```

Run the high-level fitting workflow:

```python
from virialpy.workflows import run_fit_workflow

result = run_fit_workflow(
    data_path="data/raw/ar2/ar2_cep_bsse.csv",
    potential_name="lj",
    initial_guess=[0.25, 3.5],
    parameter_names=["epsilon", "sigma"],
    r_column="r(angstrom)",
    energy_column="E_int_CP(kcal/mol)",
    output_dir="data/results/ar2/lj",
)
```

## Adding New Potentials

1. Create a module in `src/virialpy/potentials/`.
2. Implement a general `U(r)` function.
3. Register it in `src/virialpy/potentials/registry.py`.
4. Export it from `src/virialpy/potentials/__init__.py` when appropriate.
5. Add tests in `tests/`.

## Adding New Integrators

1. Create a class that inherits from `BaseIntegrator`.
2. Implement `integrate(function, lower, upper)`.
3. Return `(value, error)`.
4. Export the class from `src/virialpy/integrators/__init__.py`.
5. Add tests against simple analytical integrals.

## Units

- The distance unit of `r` must be consistent with `sigma`, `req` or `re`.
- The energy unit of fitted potential parameters must be passed to virial calculations through `energy_unit`.
- `B(T)` is returned in `cm³/mol`.
- Supported `distance_unit` values are `angstrom`, `pm` and `meter`.
- Supported `energy_unit` values are `kelvin`, `kcal/mol`, `kj/mol`, `ev` and `mev`.

## Citation

If you use `virialpy`, please cite it using the metadata in [CITATION.cff](CITATION.cff).

## License

`virialpy` is distributed under the GNU General Public License v3.0 or later, `GPL-3.0-or-later`. See [LICENSE](LICENSE) for the full license text.
