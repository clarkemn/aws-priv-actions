import typer
import boto3
from rich.console import Console
from rich.table import Table
from typing import Optional
from enum import Enum

app = typer.Typer(help="CLI for privileged actions on AWS member accounts")
console = Console()

class TaskPolicy(str, Enum):
    IAM_AUDIT = "IAMAuditRootUserCredentials"
    IAM_CREATE = "IAMCreateRootUserPassword"
    IAM_DELETE = "IAMDeleteRootUserCredentials"
    S3_UNLOCK = "S3UnlockBucketPolicy"
    SQS_UNLOCK = "SQSUnlockQueuePolicy"

# Mapping from TaskPolicy to full policy ARN (with /root-task/ path)
TASK_POLICY_ARN_MAP = {
    TaskPolicy.IAM_AUDIT: "arn:aws:iam::aws:policy/root-task/IAMAuditRootUserCredentials",
    TaskPolicy.IAM_CREATE: "arn:aws:iam::aws:policy/root-task/IAMCreateRootUserPassword",
    TaskPolicy.IAM_DELETE: "arn:aws:iam::aws:policy/root-task/IAMDeleteRootUserCredentials",
    TaskPolicy.S3_UNLOCK: "arn:aws:iam::aws:policy/root-task/S3UnlockBucketPolicy",
    TaskPolicy.SQS_UNLOCK: "arn:aws:iam::aws:policy/root-task/SQSUnlockQueuePolicy",
}

def get_sts_client(region_name=None):
    if not region_name:
        raise ValueError("A region must be specified for assume-root (global endpoint is not supported).")
    endpoint_url = f"https://sts.{region_name}.amazonaws.com"
    return boto3.client('sts', region_name=region_name, endpoint_url=endpoint_url)

def get_policy_choices():
    return {
        "1": (TaskPolicy.IAM_AUDIT, "Audit root user credentials"),
        "2": (TaskPolicy.IAM_CREATE, "Create root user password"),
        "3": (TaskPolicy.IAM_DELETE, "Delete root user credentials"),
        "4": (TaskPolicy.S3_UNLOCK, "Unlock S3 bucket policy"),
        "5": (TaskPolicy.SQS_UNLOCK, "Unlock SQS queue policy")
    }

@app.command()
def assume_root(
    target_principal: Optional[str] = typer.Argument(
        None,
        help="The target principal to assume (e.g., arn:aws:iam::123456789012:root)"
    ),
    task_policy: Optional[TaskPolicy] = typer.Argument(
        None,
        help="The task policy to use"
    ),
    duration_seconds: Optional[int] = typer.Option(900, help="Duration in seconds for the assumed role (max 900)"),
    region: Optional[str] = typer.Option(None, help="AWS region to use for STS (must be regional endpoint)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
):
    """
    Assume root privileges for a specific task on a member account.
    """
    try:
        # Interactive prompts if arguments are not provided
        if not target_principal:
            target_principal = typer.prompt(
                "Enter the target principal ARN",
                default="arn:aws:iam::123456789012:root"
            )

        if not task_policy:
            console.print("\n[bold blue]Available Task Policies:[/bold blue]")
            choices = get_policy_choices()
            for key, (policy, description) in choices.items():
                console.print(f"{key}. {policy.value} - {description}")
            
            while True:
                try:
                    choice = typer.prompt(
                        "\nSelect a task policy (1-5)",
                        type=str
                    )
                    if choice in choices:
                        task_policy = choices[choice][0]
                        break
                    console.print("[red]Invalid choice. Please select a number between 1 and 5.[/red]")
                except typer.Abort:
                    raise typer.Exit(0)

        if not region:
            region = typer.prompt(
                "Enter the AWS region to use for STS (must be a regional endpoint)",
                default="us-east-1"
            )

        sts_client = get_sts_client(region)
        
        if verbose:
            console.print(f"[bold blue]Attempting to assume root privileges[/bold blue]")
            console.print(f"Target Principal: {target_principal}")
            console.print(f"Task Policy: {task_policy.value}")
            console.print(f"Duration: {duration_seconds} seconds")

        response = sts_client.assume_root(
            TargetPrincipal=target_principal,
            TaskPolicyArn={"arn": TASK_POLICY_ARN_MAP[task_policy]},  # Pass as dict per AWS docs
            DurationSeconds=duration_seconds
        )

        if verbose:
            table = Table(title="Assumed Role Information")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in response.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:
            console.print("[green]Successfully assumed root privileges[/green]")
            console.print(f"Credentials will expire in {duration_seconds} seconds")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def list_policies():
    """
    List all available task policies.
    """
    table = Table(title="Available Task Policies")
    table.add_column("Policy Name", style="cyan")
    table.add_column("Description", style="green")
    
    policies = {
        TaskPolicy.IAM_AUDIT: "Audit root user credentials",
        TaskPolicy.IAM_CREATE: "Create root user password",
        TaskPolicy.IAM_DELETE: "Delete root user credentials",
        TaskPolicy.S3_UNLOCK: "Unlock S3 bucket policy",
        TaskPolicy.SQS_UNLOCK: "Unlock SQS queue policy"
    }
    
    for policy, description in policies.items():
        table.add_row(policy.value, description)
    
    console.print(table)

if __name__ == "__main__":
    app() 