import pandas as pd
import pytest

from virialpy.datasets import (
    load_potential_data,
    load_virial_data,
    validate_potential_data,
    validate_virial_data,
)


def test_load_potential_data_with_standard_columns(tmp_path) -> None:
    csv_path = tmp_path / "potential.csv"
    pd.DataFrame(
        {
            "r": [3.0, 3.5, None, 4.0],
            "energy": ["10.0", "-2.0", "-3.0", None],
            "extra": [1, 2, 3, 4],
        }
    ).to_csv(csv_path, index=False)

    data = load_potential_data(csv_path)

    assert list(data.columns) == ["r", "energy"]
    assert data["r"].tolist() == [3.0, 3.5]
    assert data["energy"].tolist() == [10.0, -2.0]


def test_load_potential_data_with_custom_columns(tmp_path) -> None:
    csv_path = tmp_path / "potential_custom.csv"
    pd.DataFrame(
        {
            "r(angstrom)": [3.0, 3.5, 4.0],
            "E_int_CP(kcal/mol)": [1.5, -2.0, -1.0],
        }
    ).to_csv(csv_path, index=False)

    data = load_potential_data(
        csv_path,
        r_column="r(angstrom)",
        energy_column="E_int_CP(kcal/mol)",
    )

    assert list(data.columns) == ["r", "energy"]
    assert data["r"].tolist() == [3.0, 3.5, 4.0]
    assert data["energy"].tolist() == [1.5, -2.0, -1.0]


def test_load_virial_data_with_standard_columns(tmp_path) -> None:
    csv_path = tmp_path / "virial.csv"
    pd.DataFrame(
        {
            "temperature": [100, 150, None, 200],
            "b2": ["-120.0", "-80.0", "-70.0", None],
            "source": ["a", "b", "c", "d"],
        }
    ).to_csv(csv_path, index=False)

    data = load_virial_data(csv_path)

    assert list(data.columns) == ["temperature", "b2"]
    assert data["temperature"].tolist() == [100.0, 150.0]
    assert data["b2"].tolist() == [-120.0, -80.0]


def test_loaders_raise_error_when_required_column_is_missing(tmp_path) -> None:
    csv_path = tmp_path / "missing.csv"
    pd.DataFrame({"distance": [3.0, 3.5], "energy": [-1.0, -2.0]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing required column"):
        load_potential_data(csv_path)

    with pytest.raises(ValueError, match="Missing required column"):
        load_virial_data(csv_path)


def test_validate_potential_data_accepts_valid_dataframe() -> None:
    data = pd.DataFrame({"r": [3.0, 3.5, 4.0], "energy": [1.0, -2.0, -1.0]})

    validate_potential_data(data)


def test_validate_potential_data_rejects_non_positive_distances() -> None:
    data = pd.DataFrame({"r": [3.0, 0.0, -1.0], "energy": [1.0, -2.0, -1.0]})

    with pytest.raises(ValueError, match="must be positive"):
        validate_potential_data(data)


def test_validate_virial_data_rejects_non_positive_temperatures() -> None:
    data = pd.DataFrame({"temperature": [100.0, 0.0, -10.0], "b2": [-120.0, -80.0, -70.0]})

    with pytest.raises(ValueError, match="must be positive"):
        validate_virial_data(data)

