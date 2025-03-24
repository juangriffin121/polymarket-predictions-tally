from datetime import datetime
import click

from click.testing import CliRunner
from polymarket_predictions_tally.cli.user_input import get_amount


@click.command()
def max_1000():
    max_amount = 1000
    amount = get_amount(max_amount)
    click.echo()
    click.echo(f"Output: {amount}")


def test_get_amount():
    runner = CliRunner()
    result = runner.invoke(max_1000, input="100\n")
    print(result.output)
    assert result.exit_code == 0
    assert "Output: 100.0" in result.output


def test_get_amount_invalid_amount():
    runner = CliRunner()
    result = runner.invoke(max_1000, input="1001\nn")
    print(result.output)
    assert result.exit_code == 0
    assert "Output: None" in result.output


def test_get_amount_invalid_amount_and_fix():
    runner = CliRunner()
    result = runner.invoke(max_1000, input="1001\ny\n999")
    print(result.output)
    assert result.exit_code == 0
    assert "Output: 999.0" in result.output
