"""Validation helpers for virialpy datasets."""

from __future__ import annotations

import pandas as pd
from pandas.api.types import is_numeric_dtype


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Raise a clear error when one or more required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")


def _require_numeric_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Raise a clear error when required columns are not numeric."""
    non_numeric = [column for column in columns if not is_numeric_dtype(data[column])]
    if non_numeric:
        raise ValueError(f"Column(s) must be numeric: {', '.join(non_numeric)}")


def validate_potential_data(data: pd.DataFrame) -> None:
    """Validate standardized potential-energy data.

    A valid potential dataset must contain numeric columns ``r`` and
    ``energy``, at least three rows, no missing values in those columns, and
    strictly positive distances.

    Parameters
    ----------
    data:
        DataFrame to validate.

    Raises
    ------
    ValueError
        If any validation rule fails.
    """
    columns = ["r", "energy"]
    _require_columns(data, columns)

    if len(data) < 3:
        raise ValueError("Potential data must contain at least 3 points.")
    if data[columns].isna().any().any():
        raise ValueError("Potential data must not contain missing values.")

    _require_numeric_columns(data, columns)

    if (data["r"] <= 0).any():
        raise ValueError("Potential distances in column 'r' must be positive.")


def validate_virial_data(data: pd.DataFrame) -> None:
    """Validate standardized second virial coefficient data.

    A valid virial dataset must contain numeric columns ``temperature`` and
    ``b2``, at least one row, no missing values in those columns, and strictly
    positive temperatures.

    Parameters
    ----------
    data:
        DataFrame to validate.

    Raises
    ------
    ValueError
        If any validation rule fails.
    """
    columns = ["temperature", "b2"]
    _require_columns(data, columns)

    if len(data) < 1:
        raise ValueError("Virial data must contain at least 1 point.")
    if data[columns].isna().any().any():
        raise ValueError("Virial data must not contain missing values.")

    _require_numeric_columns(data, columns)

    if (data["temperature"] <= 0).any():
        raise ValueError("Temperatures in column 'temperature' must be positive.")

