import os

from dagster import solid, pipeline, Failure
from dagster_shell.utils import execute


@solid
def run_shell_command(context, shell_command: str, env=None):
    """Generic solid for running shell commands.

    Args:
        shell_command (str): The shell command to execute
        env (Dict[str, str], optional): Environment dictionary to pass to ``subprocess.Popen``.
    Returns:
        str: The combined stdout/stderr output of running the shell command.
    """
    if env is None:
        env = {}
    elif not isinstance(env, dict):
        raise Failure(description=f"Shell command execution failed with non-conforming env dict: {env}")

    # meltano needs the `PATH` env var
    env_merged = {**os.environ.copy(), **env} if env else os.environ.copy()

    output, return_code = execute(
        shell_command=shell_command,
        log=context.log,
        output_logging="STREAM",
        env=env_merged,
        cwd=os.path.join(os.getcwd(), 'meltano')  # replace `meltano` with the name of the meltano dir if different
    )

    if return_code:
        raise Failure(description="Shell command execution failed with output: {output}".format(output=output))

    return output


@solid
def meltano_earthquakes_elt_cmd() -> str:
    """Generates a meltano elt command for the earthquakes pipeline."""
    return "meltano elt tap-rest-api target-jsonl --job_id=earthquakes"


@pipeline
def earthquakes_pipeline():
    run_shell_command(meltano_earthquakes_elt_cmd())
