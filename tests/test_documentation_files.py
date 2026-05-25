from pathlib import Path


def test_readme_exists() -> None:
    assert Path("README.md").exists()


def test_workflow_ar2_doc_exists() -> None:
    assert Path("docs/workflow_ar2.md").exists()


def test_data_format_doc_exists() -> None:
    assert Path("docs/data_format.md").exists()


def test_developer_notes_doc_exists() -> None:
    assert Path("docs/developer_notes.md").exists()


def test_configuration_doc_exists() -> None:
    assert Path("docs/configuration.md").exists()


def test_ar2_config_exists() -> None:
    assert Path("configs/ar2.yaml").exists()


def test_full_pipeline_script_exists() -> None:
    assert Path("scripts/run_ar2_full_pipeline.py").exists()


def test_main_ar2_scripts_exist() -> None:
    scripts = [
        "scripts/run_compare_potentials_ar2.py",
        "scripts/run_b2_comparison_ar2.py",
        "scripts/run_b2_validation_ar2.py",
        "scripts/run_partitioned_b2_ar2.py",
        "scripts/run_b2_method_comparison_ar2.py",
        "scripts/run_monte_carlo_comparison_ar2.py",
    ]
    for script in scripts:
        assert Path(script).exists()
