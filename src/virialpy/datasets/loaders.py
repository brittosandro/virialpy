"""CSV loaders for virialpy datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def _require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Raise a clear error when one or more required columns are missing."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        missing_columns = ", ".join(missing)
        available_columns = ", ".join(map(str, data.columns))
        raise ValueError(
            f"Missing required column(s): {missing_columns}. "
            f"Available columns: {available_columns}"
        )


def load_potential_data(
    path: str | Path,
    r_column: str = "r",
    energy_column: str = "energy",
    **read_csv_kwargs: Any,
) -> pd.DataFrame:
    """Load theoretical potential-energy data from a CSV file.

    Parameters
    ----------
    path:
        Path to the CSV file.
    r_column:
        Name of the column containing intermolecular distances.
    energy_column:
        Name of the column containing potential energies.
    **read_csv_kwargs:
        Optional keyword arguments forwarded to ``pandas.read_csv``.

    Returns
    -------
    pandas.DataFrame
        DataFrame with standardized columns ``r`` and ``energy``. Values are
        converted to numeric data, rows with missing standardized values are
        removed, and the original row order is preserved.
    """
    data = pd.read_csv(path, **read_csv_kwargs)
    _require_columns(data, [r_column, energy_column])

    standardized = data.loc[:, [r_column, energy_column]].copy()
    standardized.columns = ["r", "energy"]
    standardized["r"] = pd.to_numeric(standardized["r"], errors="coerce")
    standardized["energy"] = pd.to_numeric(standardized["energy"], errors="coerce")
    return standardized.dropna(subset=["r", "energy"])


def load_virial_data(
    path: str | Path,
    temperature_column: str = "temperature",
    b_column: str = "b2",
    **read_csv_kwargs: Any,
) -> pd.DataFrame:
    """Load experimental second virial coefficient data from a CSV file.

    Parameters
    ----------
    path:
        Path to the CSV file.
    temperature_column:
        Name of the column containing temperatures.
    b_column:
        Name of the column containing second virial coefficient values.
    **read_csv_kwargs:
        Optional keyword arguments forwarded to ``pandas.read_csv``.

    Returns
    -------
    pandas.DataFrame
        DataFrame with standardized columns ``temperature`` and ``b2``. Values
        are converted to numeric data, rows with missing standardized values
        are removed, and the original row order is preserved.
    """
    data = pd.read_csv(path, **read_csv_kwargs)
    _require_columns(data, [temperature_column, b_column])

    standardized = data.loc[:, [temperature_column, b_column]].copy()
    standardized.columns = ["temperature", "b2"]
    standardized["temperature"] = pd.to_numeric(standardized["temperature"], errors="coerce")
    standardized["b2"] = pd.to_numeric(standardized["b2"], errors="coerce")
    return standardized.dropna(subset=["temperature", "b2"])

