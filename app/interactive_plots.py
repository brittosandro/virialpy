"""Plotly figures used only for interactive Streamlit visualization."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


POTENTIAL_LABELS = {"lj": "LJ", "ilj": "ILJ", "ryd6": "Rydberg 6"}
INTEGRATOR_LABELS = {
    "scipy_quad": "SciPy quad",
    "gaussian": "Gauss-Legendre",
    "simpson": "Simpson",
    "trapezoid": "Trapézio",
    "monte_carlo": "Monte Carlo",
}
METHOD_LABELS = {"direct": "direto", "partitioned": "particionado"}


def _label(value: object, mapping: dict[str, str]) -> str:
    text = str(value)
    return mapping.get(text, text)


def _model_label(row: pd.Series) -> str:
    parts: list[str] = []
    if "model" in row and pd.notna(row["model"]):
        parts.append(_label(row["model"], POTENTIAL_LABELS))
    if "potential" in row:
        parts.append(_label(row["potential"], POTENTIAL_LABELS))
    if "integrator" in row:
        parts.append(_label(row["integrator"], INTEGRATOR_LABELS))
    if "reference_integrator" in row:
        parts.append(_label(row["reference_integrator"], INTEGRATOR_LABELS))
    if "method" in row:
        parts.append(_label(row["method"], METHOD_LABELS))
    return " | ".join(parts) if parts else "model"


def plotly_fit_comparison(data_df: pd.DataFrame, fitted_curves_df: pd.DataFrame | None = None) -> go.Figure:
    """Create an interactive U(r) fit comparison figure."""
    fig = go.Figure()
    if {"r", "energy"}.issubset(data_df.columns):
        fig.add_trace(
            go.Scatter(
                x=data_df["r"],
                y=data_df["energy"],
                mode="markers",
                name="Observed",
                hovertemplate="r=%{x}<br>energy=%{y}<extra></extra>",
            )
        )
    if fitted_curves_df is not None and {"r", "energy_fitted"}.issubset(fitted_curves_df.columns):
        group_column = "potential" if "potential" in fitted_curves_df.columns else None
        groups = fitted_curves_df.groupby(group_column) if group_column else [("Fitted", fitted_curves_df)]
        for name, group in groups:
            ordered = group.sort_values("r")
            fig.add_trace(
                go.Scatter(
                    x=ordered["r"],
                    y=ordered["energy_fitted"],
                    mode="lines",
                    name=_label(name, POTENTIAL_LABELS),
                )
            )
    fig.update_layout(xaxis_title="r", yaxis_title="Energy", template="plotly_white")
    return fig


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    fig.update_layout(template="plotly_white")
    return fig


def plotly_fit_curves(
    potential_data_df: pd.DataFrame,
    fitted_curves_df: pd.DataFrame,
    r_column: str = "r",
    energy_column: str = "energy",
    potential: str | None = None,
) -> go.Figure:
    """Create an interactive plot of observed U(r) points and fitted curves."""
    if r_column not in potential_data_df.columns or energy_column not in potential_data_df.columns:
        return _empty_figure("Observed potential data columns were not found.")
    curves = fitted_curves_df.copy()
    if potential is not None and "potential" in curves.columns:
        curves = curves[curves["potential"] == potential]
    fig = go.Figure()
    observed = potential_data_df.sort_values(r_column)
    fig.add_trace(
        go.Scatter(
            x=observed[r_column],
            y=observed[energy_column],
            mode="markers",
            name="Observed",
            hovertemplate="r=%{x}<br>U(r)=%{y}<extra></extra>",
        )
    )
    if {"r", "energy_fit", "potential"}.issubset(curves.columns):
        for potential_name, group in curves.groupby("potential"):
            ordered = group.sort_values("r")
            fig.add_trace(
                go.Scatter(
                    x=ordered["r"],
                    y=ordered["energy_fit"],
                    mode="lines",
                    name=_label(potential_name, POTENTIAL_LABELS),
                    hovertemplate="r=%{x}<br>Ufit(r)=%{y}<extra></extra>",
                )
            )
    title = f"{_label(potential, POTENTIAL_LABELS)} fit" if potential else None
    fig.update_layout(title=title, xaxis_title="r", yaxis_title="U(r)", template="plotly_white")
    return fig


def plotly_fit_residuals(residuals_df: pd.DataFrame, potential: str | None = None) -> go.Figure:
    """Create an interactive residual-vs-r fit plot."""
    data = residuals_df.copy()
    if potential is not None and "potential" in data.columns:
        data = data[data["potential"] == potential]
    if not {"r", "residual", "potential"}.issubset(data.columns):
        return _empty_figure("Fit residual columns were not found.")
    fig = go.Figure()
    for potential_name, group in data.groupby("potential"):
        ordered = group.sort_values("r")
        fig.add_trace(
            go.Scatter(
                x=ordered["r"],
                y=ordered["residual"],
                mode="lines+markers",
                name=_label(potential_name, POTENTIAL_LABELS),
                hovertemplate="r=%{x}<br>residual=%{y}<extra></extra>",
            )
        )
    fig.add_hline(y=0, line_dash="dash")
    title = f"{_label(potential, POTENTIAL_LABELS)} residuals" if potential else None
    fig.update_layout(title=title, xaxis_title="r", yaxis_title="Residual", template="plotly_white")
    return fig


def plotly_fit_observed_vs_predicted(residuals_df: pd.DataFrame, potential: str | None = None) -> go.Figure:
    """Create an interactive observed-vs-fitted energy plot."""
    data = residuals_df.copy()
    if potential is not None and "potential" in data.columns:
        data = data[data["potential"] == potential]
    required = {"energy_observed", "energy_fitted", "potential"}
    if not required.issubset(data.columns):
        return _empty_figure("Observed and fitted energy columns were not found.")
    fig = go.Figure()
    values = pd.concat([data["energy_observed"], data["energy_fitted"]]).dropna()
    if values.empty:
        return _empty_figure("Observed and fitted energy values are empty.")
    min_value = float(values.min())
    max_value = float(values.max())
    fig.add_trace(
        go.Scatter(
            x=[min_value, max_value],
            y=[min_value, max_value],
            mode="lines",
            name="y = x",
            line={"dash": "dash"},
        )
    )
    for potential_name, group in data.groupby("potential"):
        fig.add_trace(
            go.Scatter(
                x=group["energy_observed"],
                y=group["energy_fitted"],
                mode="markers",
                name=_label(potential_name, POTENTIAL_LABELS),
                hovertemplate="Observed=%{x}<br>Fitted=%{y}<extra></extra>",
            )
        )
    title = f"{_label(potential, POTENTIAL_LABELS)} observed vs fitted" if potential else None
    fig.update_layout(title=title, xaxis_title="Observed energy", yaxis_title="Fitted energy", template="plotly_white")
    return fig


def plotly_fit_metric_ranking(metrics_df: pd.DataFrame, metric: str = "rmse") -> go.Figure:
    """Create an interactive ranking for fit metrics."""
    return plotly_metric_ranking(metrics_df, metric=metric)


def plotly_b2_comparison(comparison_df: pd.DataFrame, integrator: str = "scipy_quad") -> go.Figure:
    """Create an interactive calculated-vs-experimental B(T) comparison."""
    data = comparison_df.copy()
    if "integrator" in data.columns:
        data = data[data["integrator"] == integrator]
    fig = go.Figure()
    if {"temperature", "b2_exp"}.issubset(data.columns) and not data.empty:
        exp_data = data[["temperature", "b2_exp"]].drop_duplicates().sort_values("temperature")
        fig.add_trace(
            go.Scatter(
                x=exp_data["temperature"],
                y=exp_data["b2_exp"],
                mode="markers",
                name="Experimental",
                hovertemplate="T=%{x}<br>B exp=%{y}<extra></extra>",
            )
        )
    if {"temperature", "b2_calc", "potential"}.issubset(data.columns):
        for potential, group in data.groupby("potential"):
            ordered = group.sort_values("temperature")
            custom = ordered[[col for col in ["potential", "integrator", "b2_exp", "b2_calc", "residual"] if col in ordered.columns]]
            fig.add_trace(
                go.Scatter(
                    x=ordered["temperature"],
                    y=ordered["b2_calc"],
                    mode="lines+markers",
                    name=_label(potential, POTENTIAL_LABELS),
                    customdata=custom,
                    hovertemplate="T=%{x}<br>B calc=%{y}<extra></extra>",
                )
            )
    fig.update_layout(xaxis_title="T / K", yaxis_title="B(T) / cm³ mol⁻¹", template="plotly_white")
    return fig


def plotly_b2_residuals(comparison_df: pd.DataFrame, integrator: str = "scipy_quad") -> go.Figure:
    """Create an interactive B(T) residual figure."""
    data = comparison_df.copy()
    if "integrator" in data.columns:
        data = data[data["integrator"] == integrator]
    fig = go.Figure()
    if {"temperature", "residual", "potential"}.issubset(data.columns):
        for potential, group in data.groupby("potential"):
            ordered = group.sort_values("temperature")
            fig.add_trace(
                go.Scatter(
                    x=ordered["temperature"],
                    y=ordered["residual"],
                    mode="lines+markers",
                    name=_label(potential, POTENTIAL_LABELS),
                    customdata=ordered[[col for col in ["potential", "residual", "abs_error", "percent_error"] if col in ordered.columns]],
                    hovertemplate="T=%{x}<br>residual=%{y}<extra></extra>",
                )
            )
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(xaxis_title="T / K", yaxis_title="Bcalc - Bexp / cm³ mol⁻¹", template="plotly_white")
    return fig


def plotly_b2_by_integrator(b2_df: pd.DataFrame, integrator: str | None = None) -> go.Figure:
    """Create an interactive preview of calculated B(T) by potential and integrator."""
    data = b2_df.copy()
    if integrator is not None and "integrator" in data.columns:
        data = data[data["integrator"] == integrator]
    fig = go.Figure()
    required = {"temperature", "b2", "potential", "integrator"}
    if required.issubset(data.columns):
        for (potential, integrator_name), group in data.groupby(["potential", "integrator"]):
            ordered = group.sort_values("temperature")
            name = f"{_label(potential, POTENTIAL_LABELS)} | {_label(integrator_name, INTEGRATOR_LABELS)}"
            fig.add_trace(
                go.Scatter(
                    x=ordered["temperature"],
                    y=ordered["b2"],
                    mode="lines+markers",
                    name=name,
                    hovertemplate="T=%{x}<br>B(T)=%{y}<extra></extra>",
                )
            )
    fig.update_layout(xaxis_title="T / K", yaxis_title="B(T) / cm³ mol⁻¹", template="plotly_white")
    return fig


def plotly_metric_ranking(metrics_df: pd.DataFrame, metric: str = "rmse") -> go.Figure:
    """Create an interactive horizontal ranking for a selected metric."""
    if metric not in metrics_df.columns:
        raise ValueError(f"Metric column not found: {metric}")
    data = metrics_df.copy().sort_values(metric, ascending=True)
    data["model_label"] = data.apply(_model_label, axis=1)
    hover_columns = [
        col
        for col in [
            "mae",
            "rmse",
            "max_error",
            "mape",
            "r2",
            "success",
            "mean_abs_difference",
            "max_abs_difference",
            "rmse_difference",
            "mean_percent_difference",
        ]
        if col in data.columns
    ]
    fig = go.Figure(
        go.Bar(
            x=data[metric],
            y=data["model_label"],
            orientation="h",
            customdata=data[hover_columns] if hover_columns else None,
            hovertemplate=f"{metric}=%{{x}}<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title=metric, yaxis_title="Modelo", template="plotly_white", yaxis={"categoryorder": "total ascending"})
    return fig


def plotly_method_comparison(method_df: pd.DataFrame) -> go.Figure:
    """Create an interactive direct-vs-partitioned B(T) comparison."""
    fig = go.Figure()
    data = method_df.copy()
    if {"temperature", "b2_exp"}.issubset(data.columns) and not data.empty:
        exp_data = data[["temperature", "b2_exp"]].drop_duplicates().sort_values("temperature")
        fig.add_trace(go.Scatter(x=exp_data["temperature"], y=exp_data["b2_exp"], mode="markers", name="Experimental"))
    if {"temperature", "b2_calc", "potential", "method"}.issubset(data.columns):
        for (potential, method), group in data.groupby(["potential", "method"]):
            ordered = group.sort_values("temperature")
            name = f"{_label(potential, POTENTIAL_LABELS)} | {_label(method, METHOD_LABELS)}"
            fig.add_trace(go.Scatter(x=ordered["temperature"], y=ordered["b2_calc"], mode="lines+markers", name=name))
    fig.update_layout(xaxis_title="T / K", yaxis_title="B(T) / cm³ mol⁻¹", template="plotly_white")
    return fig


def plotly_monte_carlo_difference(mc_comparison_df: pd.DataFrame, reference_integrator: str = "scipy_quad") -> go.Figure:
    """Create an interactive Monte Carlo minus reference difference figure."""
    data = mc_comparison_df.copy()
    if "reference_integrator" in data.columns:
        data = data[data["reference_integrator"] == reference_integrator]
    fig = go.Figure()
    if {"temperature", "difference", "potential"}.issubset(data.columns):
        for potential, group in data.groupby("potential"):
            ordered = group.sort_values("temperature")
            fig.add_trace(
                go.Scatter(
                    x=ordered["temperature"],
                    y=ordered["difference"],
                    mode="lines+markers",
                    name=_label(potential, POTENTIAL_LABELS),
                )
            )
    fig.add_hline(y=0, line_dash="dash")
    ref_label = _label(reference_integrator, INTEGRATOR_LABELS)
    fig.update_layout(
        xaxis_title="T / K",
        yaxis_title=f"Monte Carlo - {ref_label} / cm³ mol⁻¹",
        template="plotly_white",
    )
    return fig
