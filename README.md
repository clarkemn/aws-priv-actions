# AWS Privileged Actions CLI

A command-line interface for performing privileged actions on AWS member accounts in an organization.

## Installation

```bash
pip install aws-priv-actions
```

## Prerequisites

- Python 3.8 or higher
- AWS CLI configured with appropriate credentials
- Required IAM permissions to perform privileged actions

## Usage

### List Available Task Policies

```bash
aws-priv-actions list-policies
```

### Assume Root Privileges

```bash
aws-priv-actions assume-root <target-principal> <task-policy> [--duration-seconds SECONDS] [--verbose]
```

Example:

```bash
aws-priv-actions assume-root arn:aws:iam::123456789012:root IAMAuditRootUserCredentials --verbose
```

### Available Task Policies

- `IAMAuditRootUserCredentials`: Audit root user credentials
- `IAMCreateRootUserPassword`: Create root user password
- `IAMDeleteRootUserCredentials`: Delete root user credentials
- `S3UnlockBucketPolicy`: Unlock S3 bucket policy
- `SQSUnlockQueuePolicy`: Unlock SQS queue policy

## Development

1. Clone the repository
2. Install UV (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install development dependencies:

   ```bash
   uv pip install -e .
   ```

4. Run tests:

   ```bash
   pytest
   ```

## License

MIT License
