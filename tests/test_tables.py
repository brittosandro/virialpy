import pandas as pd

from virialpy.analysis import (
    create_b2_metrics_table,
    create_fit_summary_table,
    save_table_csv,
    save_table_latex,
)


def test_create_fit_summary_table_returns_dataframe(tmp_path) -> None:
    path = tmp_path / "fit_metrics.csv"
    pd.DataFrame(
        {
            "potential": ["lj", "ilj"],
            "rmse": [2.0, 1.0],
            "mae": [1.5, 0.8],
            "r2": [0.9, 0.95],
        }
    ).to_csv(path, index=False)

    table = create_fit_summary_table(path)

    assert isinstance(table, pd.DataFrame)
    assert table.loc[0, "Modelo"] == "ILJ"


def test_create_b2_metrics_table_returns_dataframe(tmp_path) -> None:
    path = tmp_path / "b2_metrics.csv"
    pd.DataFrame(
        {
            "potential": ["lj"],
            "integrator": ["scipy_quad"],
            "mae": [2.0],
            "rmse": [3.0],
            "max_error": [4.0],
            "mape": [5.0],
            "r2": [0.8],
        }
    ).to_csv(path, index=False)

    table = create_b2_metrics_table(path)

    assert isinstance(table, pd.DataFrame)


def test_create_b2_metrics_table_creates_model_column(tmp_path) -> None:
    path = tmp_path / "b2_metrics.csv"
    pd.DataFrame(
        {
            "potential": ["lj"],
            "method": ["partitioned"],
            "mae": [2.0],
            "rmse": [3.0],
            "max_error": [4.0],
            "mape": [5.0],
            "r2": [0.8],
        }
    ).to_csv(path, index=False)

    table = create_b2_metrics_table(path)

    assert "Modelo" in table.columns
    assert table.loc[0, "Modelo"] == "LJ | particionado"


def test_save_table_csv_saves_file(tmp_path) -> None:
    output = tmp_path / "table.csv"

    save_table_csv(pd.DataFrame({"a": [1]}), output)

    assert output.exists()


def test_save_table_latex_saves_file(tmp_path) -> None:
    output = tmp_path / "table.tex"

    save_table_latex(pd.DataFrame({"R²": [0.9]}), output)

    assert output.exists()


def test_table_savers_create_missing_directories(tmp_path) -> None:
    csv_output = tmp_path / "reports" / "tables" / "table.csv"
    tex_output = tmp_path / "reports" / "tables" / "table.tex"

    save_table_csv(pd.DataFrame({"a": [1]}), csv_output)
    save_table_latex(pd.DataFrame({"a": [1]}), tex_output)

    assert csv_output.exists()
    assert tex_output.exists()

