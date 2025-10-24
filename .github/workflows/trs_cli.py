import click
import subprocess
# ... (rest of the existing imports and helper functions)

# Define the list of repositories in the fleet for reference
TRS_REPOSITORIES = [
    "trs-alliance-system",
    "potential-chainsaw",
    "trs-alliance-v2.3",
    "probable-adventure",
    "scaling-carnival"
]

# ... (rest of the existing CLI group and decorator code)

@cli.command()
@click.argument('workflow_name')
@click.option('--repo', default='all', help='Target repository (e.g., trs-alliance-system) or "all" for the fleet.')
@click.option('--inputs', default='', help='JSON string of inputs for the remote workflow.')
@requires_role(['operator', 'sentinel'])
def dispatch_workflow(ctx, workflow_name, repo, inputs):
    """Coordinates multi-agent tasks across the TRS repository fleet."""
    
    targets = []
    if repo.lower() == 'all':
        click.echo(f"🚨 WARNING: Dispatching '{workflow_name}' across the entire TRS Fleet.")
        targets = TRS_REPOSITORIES
    elif repo in TRS_REPOSITORIES:
        targets = [repo]
    else:
        click.echo(f"❌ Error: Repository '{repo}' not recognized in the TRS Fleet.")
        return

    success_count = 0
    fail_count = 0

    for target_repo in targets:
        full_repo_path = f"trs-alliance/{target_repo}"
        click.echo(f"\nDispatching to {target_repo}...")
        
        # Build the gh CLI command
        command = [
            'gh', 'workflow', 'run', workflow_name,
            '--repo', full_repo_path,
            '-f', f'actor={ctx.obj["user"]}',
        ]
        
        # Add inputs to the command
        try:
            input_dict = json.loads(inputs) if inputs else {}
            for k, v in input_dict.items():
                command.extend(['-f', f'{k}={v}'])
        except json.JSONDecodeError:
            click.echo("❌ Error: Invalid JSON format for inputs.")
            fail_count += 1
            log_audit(f"dispatch-workflow failed (JSON) on {target_repo}", ctx.obj['user'], ctx.obj['role'], success=False)
            continue
            
        try:
            # Execute the gh command
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            click.echo(f"✅ Success. Workflow initiated on {full_repo_path}.")
            click.echo(f"   GitHub Output: {result.stdout.strip()}")
            success_count += 1
            log_audit(f"dispatch-workflow: {workflow_name} successful on {target_repo}", ctx.obj['user'], ctx.obj['role'])

        except subprocess.CalledProcessError as e:
            click.echo(f"❌ Failure. Could not dispatch to {target_repo}.")
            click.echo(f"   Error: {e.stderr.strip()}")
            fail_count += 1
            log_audit(f"dispatch-workflow failed (GH CLI) on {target_repo}", ctx.obj['user'], ctx.obj['role'], success=False)
        except FileNotFoundError:
            click.echo("❌ Error: GitHub CLI ('gh') not found. Please install and authenticate.")
            log_audit(f"dispatch-workflow failed (GH CLI missing)", ctx.obj['user'], ctx.obj['role'], success=False)
            return

    click.echo(f"\n--- Fleet Dispatch Summary ---")
    click.echo(f"🟢 Successful Dispatches: {success_count}")
    click.echo(f"🔴 Failed Dispatches: {fail_count}")
