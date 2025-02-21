import logging
import os

import click
from config.settings import ConfigParms as sc
from config import settings as scg
from dl_app import dl_app_core as dlc
from utils import logger as ufl
from utils import csv_io as ufc

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
    lineage_data_file_path = (
        f"{sc.data_out_file_path}/lineage_relationships_{workflow_id}.csv"
    )
    dl_relationships = dlc.capture_relationships(
        workflow_id=workflow_id,
        cycle_date=cycle_date,
        lineage_data_file_path=lineage_data_file_path,
    )
    all_lineage_data_file_path = f"{sc.data_out_file_path}/lineage_relationships.csv"
    ufc.uf_merge_csv_files(
        in_file_dir_path=sc.data_out_file_path,
        out_file=all_lineage_data_file_path,
        in_file_pattern="lineage_relationships_workflow*",
    )
    lineage_graph_file_path = f"{sc.img_out_file_path}/lineage_graph.svg"
    _lineage_graph_img = dlc.plot_lineage_graph(
        lineage_data_file_path=all_lineage_data_file_path,
        workflow_id=workflow_id,
        lineage_graph_file_path=lineage_graph_file_path,
    )

    logging.info("Data lineage relationships for workflow %s", workflow_id)
    logging.info(dl_relationships)
    # print("\n".join([str(r) for r in dl_relationships]))

    logging.info(
        "Finished capturing data lineage relationships for the workflow %s", workflow_id
    )


def main():
    cli()


if __name__ == "__main__":
    main()
