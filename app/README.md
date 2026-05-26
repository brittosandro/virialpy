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

The app requires `streamlit`, which is listed as a project dependency.

## Running

```bash
streamlit run app/streamlit_app.py
```

## Usage

Use the sidebar to choose:

- `configs/ar2.yaml`
- `configs/kr2.yaml`

You can also enter a manual YAML path. Click **Run pipeline** to execute the workflow through `run_from_config`.

## Outputs

Results are saved in the directories defined by the YAML file:

- `outputs.results_dir`
- `outputs.figures_dir`
- `outputs.reports_dir`

The app displays available fit metrics, B(T) validation metrics, direct-vs-partitioned metrics, Monte Carlo summaries, final figures and report tables.

## Limitations

This first version focuses on executing existing YAML configurations and visualizing generated outputs. It does not yet edit YAML files, upload arbitrary datasets, or provide interactive fitting controls.
