import pytest
import yaml

from virialpy.config import load_config, validate_run_config


def valid_config() -> dict:
    return {
        "system": "test",
        "data": {
            "potential_data": "potential.csv",
            "experimental_data": "experimental.csv",
            "r_column": "r",
            "energy_column": "energy",
            "temperature_column": "temperature",
            "b2_column": "b2",
        },
        "models": {"potentials": ["lj"]},
        "integrators": {"names": ["scipy_quad"]},
        "units": {"distance_unit": "angstrom", "energy_unit": "kcal/mol"},
        "b2": {"r_min": 2.5, "r_max": 8.0},
        "outputs": {
            "results_dir": "results",
            "figures_dir": "figures",
            "reports_dir": "reports",
        },
        "run": {"fit": True, "b2": True, "validate": True},
    }


def test_load_config_reads_valid_yaml(tmp_path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(valid_config()), encoding="utf-8")

    config = load_config(path)

    assert config["system"] == "test"


def test_load_config_raises_for_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "missing.yaml")


def test_load_config_raises_for_empty_yaml(tmp_path) -> None:
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_config(path)


def test_validate_run_config_accepts_valid_minimal_config() -> None:
    validate_run_config(valid_config())


def test_validate_run_config_rejects_missing_required_section() -> None:
    config = valid_config()
    del config["data"]

    with pytest.raises(ValueError, match="section"):
        validate_run_config(config)


def test_validate_run_config_rejects_data_without_potential_data() -> None:
    config = valid_config()
    del config["data"]["potential_data"]

    with pytest.raises(ValueError, match="potential_data"):
        validate_run_config(config)


def test_validate_run_config_rejects_non_list_potentials() -> None:
    config = valid_config()
    config["models"]["potentials"] = "lj"

    with pytest.raises(ValueError, match="models.potentials"):
        validate_run_config(config)


def test_validate_run_config_rejects_non_list_integrators() -> None:
    config = valid_config()
    config["integrators"]["names"] = "scipy_quad"

    with pytest.raises(ValueError, match="integrators.names"):
        validate_run_config(config)


def test_validate_run_config_rejects_invalid_b2_bounds() -> None:
    config = valid_config()
    config["b2"]["r_max"] = config["b2"]["r_min"]

    with pytest.raises(ValueError, match="r_max"):
        validate_run_config(config)


@pytest.mark.parametrize("field", ["fit", "b2", "validate"])
def test_validate_run_config_rejects_non_boolean_run_flags(field: str) -> None:
    config = valid_config()
    config["run"][field] = "yes"

    with pytest.raises(ValueError, match=field):
        validate_run_config(config)
