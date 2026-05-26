import pandas as pd

from virialpy.workflows import run_multisystem_comparison_workflow


def _write_system_results(base, fit_rmse: float, b2_rmse: float, partitioned_rmse: float) -> None:
    base.mkdir(parents=True)
    pd.DataFrame(
        {
            "model": ["lj"],
            "potential": ["lj"],
            "rmse": [fit_rmse],
            "mae": [fit_rmse / 2],
            "r2": [0.99],
            "success": [True],
        }
    ).to_csv(base / "fit_comparison_metrics.csv", index=False)
    pd.DataFrame(
        {
            "potential": ["lj"],
            "integrator": ["scipy_quad"],
            "mae": [b2_rmse / 2],
            "rmse": [b2_rmse],
            "max_error": [b2_rmse],
            "mape": [10.0],
            "r2": [0.9],
        }
    ).to_csv(base / "b2_experiment_metrics.csv", index=False)
    pd.DataFrame(
        {
            "potential": ["lj", "lj"],
            "method": ["direct", "partitioned"],
            "mae": [b2_rmse / 2, partitioned_rmse / 2],
            "rmse": [b2_rmse, partitioned_rmse],
            "max_error": [b2_rmse, partitioned_rmse],
            "mape": [10.0, 8.0],
            "r2": [0.9, 0.95],
        }
    ).to_csv(base / "b2_method_experiment_metrics.csv", index=False)


def test_run_multisystem_comparison_workflow_creates_outputs(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mplconfig"))
    system_a = tmp_path / "a"
    system_b = tmp_path / "b"
    _write_system_results(system_a, fit_rmse=1.0, b2_rmse=10.0, partitioned_rmse=6.0)
    _write_system_results(system_b, fit_rmse=2.0, b2_rmse=5.0, partitioned_rmse=8.0)

    outputs = run_multisystem_comparison_workflow(
        systems=[
            {"system": "A", "results_dir": system_a},
            {"system": "B", "results_dir": system_b},
        ],
        results_dir=tmp_path / "results",
        figures_dir=tmp_path / "figures",
        reports_dir=tmp_path / "reports",
    )

    assert (tmp_path / "results" / "best_b2_model_by_system.csv").exists()
    assert (tmp_path / "figures" / "system_ranking.png").exists()
    assert (tmp_path / "reports" / "tables" / "system_ranking.tex").exists()
    assert outputs["tables_dir"].endswith("tables")
