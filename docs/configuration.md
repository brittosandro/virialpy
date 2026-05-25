# YAML Configuration

The YAML configuration layer lets users describe a molecular system and run the general `virialpy` workflow with:

```bash
virialpy run-config configs/ar2.yaml
```

The configuration reuses the same workflow logic as the argument-based CLI. It does not define new physical calculations.

## General Structure

```yaml
system: ar2

data:
  potential_data: data/raw/ar2/ar2_cep_bsse.csv
  experimental_data: data/raw/ar2/b2_experimental.csv
  r_column: "r(angstrom)"
  energy_column: "E_int_CP(kcal/mol)"
  temperature_column: "Temperatura"
  b2_column: "B(segundo coef. virial) [cm³/mol]"

models:
  potentials:
    - all

integrators:
  names:
    - all

units:
  distance_unit: angstrom
  energy_unit: kcal/mol

b2:
  r_min: 2.5
  r_max: 30.0

partitioned:
  enabled: true
  r1: 3.052
  r2: 3.7578
  r3: 13.0391
  r4: 30.0
  integrator_b2:
    name: gaussian
    n_points: 6
  integrator_b3:
    name: gaussian
    n_points: 10
  integrator_b4:
    name: gaussian
    n_points: 24

outputs:
  results_dir: data/results/ar2_config
  figures_dir: outputs/figures/ar2_config
  reports_dir: outputs/reports/ar2_config

run:
  fit: true
  b2: true
  validate: true
  partitioned: true
  method_comparison: true
  monte_carlo_plots: true
  final_outputs: true
```

## Sections

`system`: short molecular-system label used in progress messages and plot titles.

`data`: input files and column names. `potential_data` points to a CSV with theoretical `U(r)` values. `experimental_data` points to a CSV with experimental `B(T)` values.

`models`: potentials to fit and use. Use explicit names such as `lj`, `ilj`, `ryd6`, or use:

```yaml
potentials:
  - all
```

`integrators`: numerical integrators for direct `B(T)`. Use explicit names such as `scipy_quad`, `gaussian`, `simpson`, `trapezoid`, `monte_carlo`, or use:

```yaml
names:
  - all
```

`units`: unit metadata passed to virial calculations. Supported `distance_unit` values are `angstrom`, `pm`, and `meter`. Supported `energy_unit` values are `kelvin`, `kcal/mol`, `kj/mol`, `ev`, and `mev`.

`b2`: radial integration bounds `r_min` and `r_max` in the selected distance unit.

`partitioned`: optional settings for partitioned `B(T)` calculations. When
`enabled` is true, the limits must obey `0 < r1 < r2 < r3 < r4`. The
`integrator_b2`, `integrator_b3`, and `integrator_b4` mappings select the
integrators used in each numerical region. For example:

```yaml
partitioned:
  enabled: true
  r1: 3.052
  r2: 3.7578
  r3: 13.0391
  r4: 30.0
  integrator_b2:
    name: gaussian
    n_points: 6
```

Supported partitioned integrator names are `scipy_quad`, `gaussian`,
`simpson`, `trapezoid`, and `monte_carlo`. Optional parameters follow the
integrator constructor names, such as `n_points`, `epsabs`, `epsrel`, `limit`,
`n_samples`, and `random_state`.

`outputs`: output directories for numerical results, figures, and reports.

`run`: workflow stages. The YAML workflow can control:

- `fit`: potential fitting.
- `b2`: direct `B(T)` calculations.
- `validate`: comparison with experimental data.
- `partitioned`: partitioned `B(T)` calculations.
- `method_comparison`: direct-vs-partitioned comparison.
- `monte_carlo_plots`: Monte Carlo comparison tables and figures.
- `final_outputs`: final figures and CSV/LaTeX tables.

## New Molecular Systems

To create a configuration for another system:

1. Copy `configs/ar2.yaml`.
2. Change `system`.
3. Point `data.potential_data` and `data.experimental_data` to the new CSV files.
4. Update all column names.
5. Choose `models.potentials` and `integrators.names`.
6. Set the correct `units`.
7. Choose `b2.r_min` and `b2.r_max`.
8. Choose output directories under `data/results/`, `outputs/figures/`, and `outputs/reports/`.
9. Enable or disable optional stages in `run`.
