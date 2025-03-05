import os
import logging
from dotenv import load_dotenv
from config.settings import ConfigParms as sc
from dl_app import dl_app_core as dlc
from utils import logger as ufl

from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    """
    Default route

    Args:
        none

    Returns:
        A default message.
    """

    return {"message": "Data Lineage App"}


@app.get("/capture-relationships/")
async def capture_relationships(workflow_id: str, cycle_date: str = ""):
    """
    Capture data lineage relationships for the workflow.


    Args:
        workflow_id: Id of the workflow.
        cycle_date: Cycle date

    Returns:
        Data lineage relationships.
    """

    logging.info(
        "Start capturing data lineage relationships for the workflow %s", workflow_id
    )
    dl_relationships = dlc.capture_relationships(
        workflow_id=workflow_id,
        cycle_date=cycle_date
    )
    logging.info(
        "Finished capturing data lineage relationships for the workflow %s", workflow_id
    )

    return {"results": dl_relationships}


def main():
    # Load the environment variables from .env file
    load_dotenv()

    # Fail if env variable is not set
    sc.env = os.environ["ENV"]
    sc.app_root_dir = os.environ["APP_ROOT_DIR"]
    sc.load_config()

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    ufl.config_logger(log_file_path_name=f"{sc.log_file_path}/{script_name}.log")
    logging.info("Configs are set")
    logging.info(os.environ)
    logging.info(sc.config)
    logging.info(vars(sc))

    logging.info("Starting the API service")

    uvicorn.run(
        app,
        port=8080,
        host="0.0.0.0",
        log_config=f"{sc.cfg_file_path}/api_log.ini",
    )


if __name__ == "__main__":
    main()
