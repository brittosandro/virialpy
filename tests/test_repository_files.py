from pathlib import Path


def test_repository_public_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]

    for relative_path in [
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "CITATION.cff",
        "pyproject.toml",
    ]:
        assert (root / relative_path).exists()
