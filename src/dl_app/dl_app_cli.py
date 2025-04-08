import logging
import os

import click

# from dotenv import load_dotenv
from config.settings import ConfigParms as sc
from dl_app import dl_app_core as dlc
from utils import logger as ufl


# Create command group
@click.group()
@click.option(
    "--app_host_pattern",
    required=True,
    default="aws_ec2_native",
    help="Environment where the application is hosted.",
)
@click.option(
    "--debug", required=False, default="n", help="Set the logging level to DEBUG."
)
@click.pass_context
def cli(ctx, app_host_pattern, debug):
    # Store the option in a context in case we need to pass it down to commands
    ctx.obj = {"app_host_pattern": app_host_pattern, "debug": debug}

    # Get the arguments
    if debug == "y":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Set root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(level=log_level)

    # Set env anf cfg variables
    sc.load_config(app_host_pattern)

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    # ufl.config_logger(log_file_path_name=f"{sc.app_log_dir}/{script_name}.log")
    ufl.config_multi_platform_logger(
        log_level=log_level,
        handlers=sc.log_handlers,
        log_file_path_name=f"{sc.app_log_dir}/{script_name}.log",
    )

    logging.info("Configs are set")
    logging.info(os.environ)
    logging.info(sc.config)
    logging.info(vars(sc))


@cli.command()
@click.option(
    "--workflow_id", type=str, default="dev", help="Workflow id", required=True
)
@click.option("--cycle_date", type=str, default="", help="Cycle date")
@click.pass_context
def capture_relationships(ctx, workflow_id: str, cycle_date: str):
    """
    Capture data lineage relationships for the workflow.
    """

    # app_host_pattern = ctx.obj["app_host_pattern"]

    logging.info(
        "Start capturing data lineage relationships for the workflow %s", workflow_id
    )
    dl_relationships = dlc.capture_relationships(
        workflow_id=workflow_id, cycle_date=cycle_date
    )

    logging.info(
        "Finished capturing data lineage relationships for the workflow %s", workflow_id
    )

    return {"results": dl_relationships}


def main():
    cli()  # pylint: disable=E1120


if __name__ == "__main__":
    main()
