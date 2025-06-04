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

def get_sts_client():
    return boto3.client('sts')

@app.command()
def assume_root(
    target_principal: str = typer.Argument(..., help="The target principal to assume"),
    task_policy: TaskPolicy = typer.Argument(..., help="The task policy to use"),
    duration_seconds: Optional[int] = typer.Option(3600, help="Duration in seconds for the assumed role"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
):
    """
    Assume root privileges for a specific task on a member account.
    """
    try:
        sts_client = get_sts_client()
        
        if verbose:
            console.print(f"[bold blue]Attempting to assume root privileges[/bold blue]")
            console.print(f"Target Principal: {target_principal}")
            console.print(f"Task Policy: {task_policy}")
            console.print(f"Duration: {duration_seconds} seconds")

        response = sts_client.assume_root(
            TargetPrincipal=target_principal,
            TaskPolicyArn=task_policy,
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