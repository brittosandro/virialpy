# virialpy Streamlit App

This is a first graphical interface for running existing `virialpy` YAML workflows and viewing generated tables and figures.

## Installation

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

The app requires `streamlit` and `plotly`, which are listed as project dependencies.

## Running

```bash
streamlit run app/streamlit_app.py
```

## Usage

Use the sidebar to choose:

- `configs/ar2.yaml`
- `configs/kr2.yaml`

You can also enter a manual YAML path. Click **Run pipeline** to execute the workflow through `run_from_config`.

## Creating a New System from CSV

Select **New system from CSV** in the sidebar to create a workflow without editing YAML by hand.

1. Enter a system name such as `kr2`, `xe2`, or `meu_sistema`.
2. Upload the theoretical potential-energy CSV.
3. Upload the experimental B(T) CSV.
4. Preview both files.
5. Choose the distance, energy, temperature, and B(T) columns.
6. Review **Calculation parameters**.
7. Choose potentials and integrators.
8. Choose distance and energy units.
9. Set direct integration bounds.
10. Optionally enable partitioned B(T) and choose `r1`, `r2`, `r3`, `r4`.
11. Save the data setup.
12. Run the workflow step by step: fit potentials, inspect fit quality, compute B(T), validate against experiment, run advanced methods and generate final outputs.

The app saves uploaded files and generated outputs under:

```text
data/raw/<system_name>/
configs/generated/<system_name>_streamlit.yaml
data/results/<system_name>_streamlit/
outputs/figures/<system_name>_streamlit/
outputs/reports/<system_name>_streamlit/
```

## Outputs

Results are saved in the directories defined by the YAML file:

- `outputs.results_dir`
- `outputs.figures_dir`
- `outputs.reports_dir`

The app displays available fit metrics, B(T) validation metrics, direct-vs-partitioned metrics, Monte Carlo summaries, final figures and report tables.

## Interactive Visualization

The web interface uses Plotly for interactive exploration inside Streamlit. These plots are meant for quick inspection, hover details and visual comparison during analysis.

Matplotlib remains the backend used by `virialpy` for static exported figures, report images and publication-style PNG files.

## Limitations

This first version focuses on executing existing YAML configurations, creating new workflows from uploaded CSV files and visualizing generated outputs. It does not yet provide manual parameter editing for each nonlinear fit.
