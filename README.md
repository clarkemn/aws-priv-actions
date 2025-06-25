# AWS Privileged Actions CLI

A command-line interface for performing privileged actions on AWS member accounts in an organization, when [Centralized Root Management](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-enable-root-access.html) is enabled.

## Why?

As of the time of writing, there is no AWS API to fetch the list of available task policies. This is a workaround to allow you to perform privileged actions on AWS member accounts in an organization.

This was built as a simple tool to allow Operators to use the `assume-root` feature of AWS Centralized Root Management in critical situations requring root access, without having to pour over AWS CLI documentation.

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
aws-priv-actions assume-root <target-principal> <task-policy> [--duration-seconds SECONDS] [--region REGION] [--verbose]
```

- The `--region` flag is required for the `assume-root` command, as the AWS global STS endpoint is not supported for this operation. If not provided, you will be prompted interactively (default: `us-east-1`).
- The CLI always uses the correct regional STS endpoint (e.g., `sts.us-east-1.amazonaws.com`).

Example (with region flag):

```bash
aws-priv-actions assume-root arn:aws:iam::123456789012:root IAMAuditRootUserCredentials --region us-east-1 --verbose
```

Example (interactive region prompt):

```bash
aws-priv-actions assume-root arn:aws:iam::123456789012:root IAMAuditRootUserCredentials
Enter the AWS region to use for STS (must be a regional endpoint) [us-east-1]:
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
