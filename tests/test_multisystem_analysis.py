import pandas as pd

from virialpy.analysis import (
    best_b2_model_by_system,
    best_fit_potential_by_system,
    best_integrator_by_system,
    compare_direct_partitioned_by_system,
)


def test_multisystem_best_tables() -> None:
    fit = pd.DataFrame(
        {
            "system": ["A", "A", "B", "B"],
            "model": ["lj", "ilj", "lj", "ryd6"],
            "potential": ["lj", "ilj", "lj", "ryd6"],
            "rmse": [2.0, 1.0, 3.0, 0.5],
            "mae": [1.5, 0.8, 2.5, 0.4],
            "r2": [0.8, 0.9, 0.7, 0.99],
        }
    )
    b2 = pd.DataFrame(
        {
            "system": ["A", "A", "B", "B"],
            "potential": ["lj", "ilj", "lj", "ryd6"],
            "integrator": ["scipy_quad", "gaussian", "scipy_quad", "monte_carlo"],
            "rmse": [10.0, 8.0, 5.0, 6.0],
            "mae": [9.0, 7.0, 4.0, 5.0],
            "r2": [0.7, 0.8, 0.95, 0.9],
        }
    )
    method = pd.DataFrame(
        {
            "system": ["A", "A", "B", "B"],
            "potential": ["lj", "lj", "lj", "lj"],
            "method": ["direct", "partitioned", "direct", "partitioned"],
            "rmse": [10.0, 6.0, 5.0, 8.0],
            "mae": [9.0, 5.0, 4.0, 7.0],
            "r2": [0.7, 0.85, 0.95, 0.8],
        }
    )

    assert best_fit_potential_by_system(fit).set_index("system").loc["A", "model"] == "ilj"
    assert best_b2_model_by_system(b2).set_index("system").loc["B", "potential"] == "lj"
    assert best_integrator_by_system(b2).set_index("system").loc["A", "integrator"] == "gaussian"
    comparison = compare_direct_partitioned_by_system(method)
    assert set(comparison["method"]) == {"direct", "partitioned"}
