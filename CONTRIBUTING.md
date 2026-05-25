# Contributing

Contributions are welcome. Please keep changes focused and include tests for scientific behavior whenever possible.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

## Running Tests

```bash
pytest
```

The test suite covers data loading, potential functions, fitting, integrators, virial calculations, plotting helpers, workflows, tables and the CLI.

## Adding a New Potential

1. Create a module in `src/virialpy/potentials/`.
2. Implement a general `U(r)` function that accepts scalars, lists and NumPy arrays.
3. Register it in `src/virialpy/potentials/registry.py`.
4. Export it from `src/virialpy/potentials/__init__.py` when appropriate.
5. Add focused tests in `tests/`.

## Adding a New Integrator

1. Create a class that inherits from `BaseIntegrator`.
2. Implement `integrate(function, lower, upper)`.
3. Return `(value, error)`, using `None` for `error` when no estimate is available.
4. Export the class from `src/virialpy/integrators/__init__.py`.
5. Add tests against simple analytical integrals.

## Issues and Pull Requests

Open an issue for bugs, scientific questions or proposed features. Pull requests should describe the motivation, summarize the change and report the tests that were run.
