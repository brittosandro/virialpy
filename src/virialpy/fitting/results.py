"""Backend-independent fitting results."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class FitResult:
    """Result of an intermolecular-potential fit.

    The fields are intentionally independent of any fitting backend so SciPy,
    lmfit, or future optimizers can return the same public result structure.
    """

    potential_name: str
    parameter_names: list[str]
    parameter_values: dict[str, float]
    covariance: object | None
    residuals: np.ndarray
    rmse: float
    mae: float
    r2: float
    success: bool
    message: str
    r_values: np.ndarray | None = None
    observed_values: np.ndarray | None = None
    fitted_values: np.ndarray | None = None
