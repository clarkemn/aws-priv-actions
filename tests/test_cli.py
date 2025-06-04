import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from aws_priv_actions.cli import app, TaskPolicy

runner = CliRunner()

def test_list_policies():
    result = runner.invoke(app, ["list-policies"])
    assert result.exit_code == 0
    assert "Available Task Policies" in result.stdout
    assert "IAMAuditRootUserCredentials" in result.stdout

@patch("aws_priv_actions.cli.get_sts_client")
def test_assume_root_success(mock_get_sts_client):
    mock_client = MagicMock()
    mock_client.assume_root.return_value = {
        "Credentials": {
            "AccessKeyId": "test-key",
            "SecretAccessKey": "test-secret",
            "SessionToken": "test-token",
            "Expiration": "2024-01-01T00:00:00Z"
        }
    }
    mock_get_sts_client.return_value = mock_client

    result = runner.invoke(app, [
        "assume-root",
        "arn:aws:iam::123456789012:root",
        TaskPolicy.IAM_AUDIT.value,
        "--verbose"
    ])

    assert result.exit_code == 0
    assert "Successfully assumed root privileges" in result.stdout
    mock_client.assume_root.assert_called_once()

@patch("aws_priv_actions.cli.get_sts_client")
def test_assume_root_error(mock_get_sts_client):
    mock_client = MagicMock()
    mock_client.assume_root.side_effect = Exception("Access denied")
    mock_get_sts_client.return_value = mock_client

    result = runner.invoke(app, [
        "assume-root",
        "arn:aws:iam::123456789012:root",
        TaskPolicy.IAM_AUDIT.value
    ])

    assert result.exit_code == 1
    assert "Error: Access denied" in result.stdout 