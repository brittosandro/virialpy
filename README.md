# virialpy

`virialpy` is an early-stage scientific Python project for working with intermolecular potentials and second virial coefficient calculations.

The project is intended to support:

- fitting intermolecular potentials `U(r)`;
- calculating the second virial coefficient `B(T)`;
- comparing calculated values with experimental datasets;
- extending the codebase with new potentials, numerical integrators, scientific methods, CLI commands, and future web integrations.

This repository currently contains only the initial architecture. Scientific implementations will be added incrementally.

## Project Layout

```text
src/virialpy/
  constants/      Physical constants and scientific defaults.
  units/          Unit conversion helpers and conventions.
  potentials/     Intermolecular potential models.
  fitting/        Parameter estimation and optimization workflows.
  integrators/    Numerical integration strategies.
  virial/         Virial coefficient equations and calculators.
  datasets/       Loading, validating, and preparing datasets.
  analysis/       Comparison between calculated and experimental results.
  plotting/       Figures and visualization utilities.
  workflows/      End-to-end scientific workflows.
  cli/            Command-line interface entry points.
```

## Development

Install the package in editable mode after dependencies are available:

```bash
pip install -e .
```

Run tests:

```bash
pytest
```

