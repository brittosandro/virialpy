from pathlib import Path


def test_streamlit_app_file_exists() -> None:
    assert Path("app/streamlit_app.py").exists()


def test_streamlit_app_readme_exists() -> None:
    assert Path("app/README.md").exists()


def test_streamlit_app_references_run_from_config() -> None:
    content = Path("app/streamlit_app.py").read_text(encoding="utf-8")

    assert "run_from_config" in content


def test_streamlit_app_references_streamlit() -> None:
    content = Path("app/streamlit_app.py").read_text(encoding="utf-8")

    assert "streamlit" in content
