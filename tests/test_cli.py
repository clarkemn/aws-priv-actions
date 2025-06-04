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

    # Test without verbose flag - using arguments
    result = runner.invoke(app, [
        "assume-root",
        "arn:aws:iam::123456789012:root",
        "IAMAuditRootUserCredentials"
    ])

    assert result.exit_code == 0
    assert "Successfully assumed root privileges" in result.stdout

    # Test with verbose flag - using arguments
    result = runner.invoke(app, [
        "assume-root",
        "arn:aws:iam::123456789012:root",
        "IAMAuditRootUserCredentials",
        "--verbose"
    ])

    assert result.exit_code == 0
    assert "Attempting to assume root privileges" in result.stdout
    assert "Target Principal: arn:aws:iam::123456789012:root" in result.stdout
    # Check for either format of the task policy output
    assert any(
        policy_text in result.stdout
        for policy_text in [
            "Task Policy: TaskPolicy.IAM_AUDIT",
            "Task Policy: IAMAuditRootUser"
        ]
    )

    # Test interactive mode
    result = runner.invoke(
        app,
        ["assume-root"],
        input="arn:aws:iam::123456789012:root\n1\n"  # target_principal and policy choice
    )

    assert result.exit_code == 0
    assert "Successfully assumed root privileges" in result.stdout

@patch("aws_priv_actions.cli.get_sts_client")
def test_assume_root_error(mock_get_sts_client):
    mock_client = MagicMock()
    mock_client.assume_root.side_effect = Exception("Access denied")
    mock_get_sts_client.return_value = mock_client

    # Test error with arguments
    result = runner.invoke(app, [
        "assume-root",
        "arn:aws:iam::123456789012:root",
        "IAMAuditRootUserCredentials"
    ])

    assert result.exit_code == 1
    assert "Error: Access denied" in result.stdout

    # Test error in interactive mode
    result = runner.invoke(
        app,
        ["assume-root"],
        input="arn:aws:iam::123456789012:root\n1\n"  # target_principal and policy choice
    )

    assert result.exit_code == 1
    assert "Error: Access denied" in result.stdout

@patch("aws_priv_actions.cli.get_sts_client")
def test_assume_root_invalid_policy_choice(mock_get_sts_client):
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

    # Test invalid policy choice in interactive mode
    result = runner.invoke(
        app,
        ["assume-root"],
        input="arn:aws:iam::123456789012:root\ninvalid\n1\n"  # invalid choice then valid choice
    )

    assert result.exit_code == 0
    assert "Invalid choice" in result.stdout
    assert "Successfully assumed root privileges" in result.stdout 