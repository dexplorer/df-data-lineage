import logging
import os

import click
from config.settings import ConfigParms as sc
from config import settings as scg
from dl_app import dl_app_core as dlc
from utils import logger as ufl

#
APP_ROOT_DIR = "/workspaces/df-data-lineage"


# Create command group
@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--workflow_id", type=str, default="dev", help="Workflow id", required=True
)
@click.option("--env", type=str, default="dev", help="Environment")
@click.option("--cycle_date", type=str, default="", help="Cycle date")
def capture_relationships(workflow_id: str, env: str, cycle_date: str):
    """
    Capture data lineage relationships for the workflow.
    """

    scg.APP_ROOT_DIR = APP_ROOT_DIR
    sc.load_config(env=env)

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    ufl.config_logger(log_file_path_name=f"{sc.log_file_path}/{script_name}.log")
    logging.info("Configs are set")

    logging.info(
        "Start capturing data lineage relationships for the workflow %s", workflow_id
    )
    dl_relationships = dlc.capture_relationships(
        workflow_id=workflow_id, cycle_date=cycle_date
    )

    logging.info("Data lineage relationships for workflow %s", workflow_id)
    logging.info(dl_relationships)
    print("\n".join([str(r) for r in dl_relationships]))

    logging.info(
        "Finished capturing data lineage relationships for the workflow %s", workflow_id
    )


def main():
    cli()


if __name__ == "__main__":
    main()
