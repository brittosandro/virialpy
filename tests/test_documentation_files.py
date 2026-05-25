from pathlib import Path


def test_readme_exists() -> None:
    assert Path("README.md").exists()


def test_workflow_ar2_doc_exists() -> None:
    assert Path("docs/workflow_ar2.md").exists()


def test_data_format_doc_exists() -> None:
    assert Path("docs/data_format.md").exists()


def test_developer_notes_doc_exists() -> None:
    assert Path("docs/developer_notes.md").exists()


def test_full_pipeline_script_exists() -> None:
    assert Path("scripts/run_ar2_full_pipeline.py").exists()

