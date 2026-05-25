"""Metrics for validating calculated second virial coefficients."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def calculate_b2_metrics(
    y_true: Sequence[float] | pd.Series | np.ndarray,
    y_pred: Sequence[float] | pd.Series | np.ndarray,
) -> dict[str, float]:
    """Calculate regression-style metrics for B2 validation.

    Parameters
    ----------
    y_true:
        Experimental or reference B2 values.
    y_pred:
        Calculated B2 values.

    Returns
    -------
    dict[str, float]
        Dictionary containing ``mae``, ``rmse``, ``max_error``, ``mape``, and
        ``r2``.
    """
    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)

    if true.shape[0] != pred.shape[0]:
        raise ValueError("y_true and y_pred must have the same length.")

    residual = pred - true
    mae = float(np.mean(np.abs(residual)))
    rmse = float(np.sqrt(np.mean(residual**2)))
    max_error = float(np.max(np.abs(residual)))

    nonzero = true != 0
    if np.any(nonzero):
        mape = float(np.mean(np.abs(residual[nonzero] / true[nonzero])) * 100.0)
    else:
        mape = float(np.nan)

    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((true - np.mean(true)) ** 2))
    r2 = 1.0 if ss_tot == 0.0 and ss_res == 0.0 else 1.0 - ss_res / ss_tot

    return {
        "mae": mae,
        "rmse": rmse,
        "max_error": max_error,
        "mape": mape,
        "r2": float(r2),
    }


def calculate_grouped_b2_metrics(
    data: pd.DataFrame,
    group_columns: Sequence[str],
) -> pd.DataFrame:
    """Calculate B2 metrics for each group in a comparison table."""
    required = ["b2_exp", "b2_calc", *group_columns]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    rows = []
    for group_key, group in data.groupby(list(group_columns), dropna=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        metrics = calculate_b2_metrics(group["b2_exp"], group["b2_calc"])
        row = dict(zip(group_columns, group_key, strict=True))
        row.update(metrics)
        rows.append(row)

    return pd.DataFrame(rows, columns=[*group_columns, "mae", "rmse", "max_error", "mape", "r2"])

