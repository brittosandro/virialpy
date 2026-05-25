"""Helpers for final scientific tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _model_label(value: str) -> str:
    """Return readable labels for known model and method names."""
    labels = {
        "lj": "LJ",
        "ilj": "ILJ",
        "ryd6": "Rydberg 6",
        "scipy_quad": "SciPy quad",
        "gaussian": "Gauss-Legendre",
        "simpson": "Simpson",
        "trapezoid": "Trapézio",
        "direct": "direto",
        "partitioned": "particionado",
    }
    return labels.get(value, value)


def _round_numeric(data: pd.DataFrame, decimals: int = 4) -> pd.DataFrame:
    """Round numeric columns in a copy of a DataFrame."""
    rounded = data.copy()
    numeric_columns = rounded.select_dtypes(include="number").columns
    rounded[numeric_columns] = rounded[numeric_columns].round(decimals)
    return rounded


def create_fit_summary_table(fit_metrics_path: str | Path) -> pd.DataFrame:
    """Create a formatted fit-summary table ordered by increasing RMSE."""
    data = pd.read_csv(fit_metrics_path)
    if "rmse" not in data.columns:
        raise ValueError("fit metrics table must contain an 'rmse' column.")

    table = data.sort_values("rmse", ascending=True).reset_index(drop=True).copy()
    rename = {
        "potential": "Modelo",
        "rmse": "RMSE",
        "mae": "MAE",
        "r2": "R²",
    }
    table = table.rename(columns=rename)
    if "Modelo" in table.columns:
        table["Modelo"] = table["Modelo"].astype(str).map(_model_label)

    keep = [column for column in ["Modelo", "RMSE", "MAE", "R²"] if column in table.columns]
    return _round_numeric(table.loc[:, keep])


def create_b2_metrics_table(metrics_path: str | Path) -> pd.DataFrame:
    """Create a formatted B(T)-metrics table ordered by increasing RMSE."""
    data = pd.read_csv(metrics_path)
    if "rmse" not in data.columns:
        raise ValueError("B2 metrics table must contain an 'rmse' column.")

    table = data.sort_values("rmse", ascending=True).reset_index(drop=True).copy()
    label_parts = []
    for column in ["potential", "integrator", "method"]:
        if column in table.columns:
            label_parts.append(table[column].astype(str).map(_model_label))
    if label_parts:
        model_label = label_parts[0]
        for part in label_parts[1:]:
            model_label = model_label + " | " + part
        table.insert(0, "Modelo", model_label)

    table = table.rename(
        columns={
            "mae": "MAE",
            "rmse": "RMSE",
            "max_error": "Erro máximo",
            "mape": "MAPE (%)",
            "r2": "R²",
        }
    )

    keep = [
        column
        for column in ["Modelo", "MAE", "RMSE", "Erro máximo", "MAPE (%)", "R²"]
        if column in table.columns
    ]
    return _round_numeric(table.loc[:, keep])


def save_table_csv(table: pd.DataFrame, path: str | Path) -> None:
    """Save a table as CSV, creating parent directories automatically."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False)


def save_table_latex(
    table: pd.DataFrame,
    path: str | Path,
    caption: str | None = None,
    label: str | None = None,
) -> None:
    """Save a table as LaTeX, creating parent directories automatically."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        latex = table.to_latex(index=False, caption=caption, label=label, escape=False)
    except ImportError:
        # Some pandas versions route to_latex through Styler/Jinja2. Keep this
        # lightweight fallback so the project does not require an extra runtime
        # dependency just to export simple final tables.
        lines = ["\\begin{table}", "\\centering"]
        if caption is not None:
            lines.append(f"\\caption{{{caption}}}")
        if label is not None:
            lines.append(f"\\label{{{label}}}")
        alignment = "l" * len(table.columns)
        lines.append(f"\\begin{{tabular}}{{{alignment}}}")
        lines.append("\\toprule")
        lines.append(" & ".join(map(str, table.columns)) + " \\\\")
        lines.append("\\midrule")
        for row in table.itertuples(index=False):
            lines.append(" & ".join(map(str, row)) + " \\\\")
        lines.append("\\bottomrule")
        lines.append("\\end{tabular}")
        lines.append("\\end{table}")
        latex = "\n".join(lines)
    output.write_text(latex, encoding="utf-8")
