import logging
import os

import click
from dotenv import load_dotenv
from config.settings import ConfigParms as sc
from dl_app import dl_app_core as dlc
from utils import logger as ufl


# Create command group
@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--workflow_id", type=str, default="dev", help="Workflow id", required=True
)
@click.option("--cycle_date", type=str, default="", help="Cycle date")
def capture_relationships(workflow_id: str, cycle_date: str):
    """
    Capture data lineage relationships for the workflow.
    """

    logging.info(
        "Start capturing data lineage relationships for the workflow %s", workflow_id
    )
    dl_relationships = dlc.capture_relationships(
        workflow_id=workflow_id, cycle_date=cycle_date
    )

    logging.info("Data lineage relationships for workflow %s", workflow_id)
    logging.info(dl_relationships)
    # print("\n".join([str(r) for r in dl_relationships]))

    logging.info(
        "Finished capturing data lineage relationships for the workflow %s", workflow_id
    )


def main():
    # Load the environment variables from .env file
    load_dotenv()

    # Fail if env variable is not set
    sc.load_config()

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    ufl.config_logger(log_file_path_name=f"{sc.app_log_dir}/{script_name}.log")
    logging.info("Configs are set")
    logging.info(os.environ)
    logging.info(sc.config)
    logging.info(vars(sc))

    cli()


if __name__ == "__main__":
    main()
