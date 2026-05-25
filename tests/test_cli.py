from typer.testing import CliRunner

from virialpy.cli.main import app


runner = CliRunner()


def test_cli_help_works() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "ar2" in result.output


def test_cli_ar2_help_works() -> None:
    result = runner.invoke(app, ["ar2", "--help"])

    assert result.exit_code == 0


def test_cli_ar2_help_lists_main_commands() -> None:
    result = runner.invoke(app, ["ar2", "--help"])

    assert result.exit_code == 0
    for command in [
        "fit",
        "b2",
        "validate",
        "partitioned",
        "methods",
        "monte-carlo",
        "figures",
        "full-pipeline",
    ]:
        assert command in result.output

