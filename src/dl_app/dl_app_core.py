from metadata import dataset as ds
from metadata import workflow as wf
from metadata import integration_task as it
from app_calendar import eff_date as ed
from dl_app.regex_parser import parser as rp
from dl_app.lineage import models as lm

from config.settings import ConfigParms as sc
from utils import file_io as uff

import logging


def capture_relationships(workflow_id: str, cycle_date: str) -> list:
    # Simulate getting the cycle date from API
    # Run this from the parent app
    if not cycle_date:
        cycle_date = ed.get_cur_cycle_date()

    # Simulate getting the workflow metadata from API
    logging.info("Get workflow metadata")
    workflow = wf.get_workflow_from_json(workflow_id=workflow_id)

    # Simulate getting the task metadata from API
    logging.info("Get task metadata")
    if isinstance(workflow, wf.IngestionWorkflow):
        task = it.get_integration_task_from_json(task_id=workflow.ingestion_task_id)
    elif isinstance(workflow, wf.DistributionWorkflow):
        task = it.get_integration_task_from_json(task_id=workflow.distribution_task_id)
    else:
        raise RuntimeError("Workflow type is not expected.")

    # Simulate getting the source dataset metadata from API
    logging.info("Get source dataset metadata")
    source_dataset = ds.get_dataset_from_json(dataset_id=task.source_dataset_id)

    # Get current effective date
    cur_eff_date = ed.get_cur_eff_date(
        schedule_id=source_dataset.schedule_id, cycle_date=cycle_date
    )
    cur_eff_date_yyyymmdd = ed.fmt_date_str_as_yyyymmdd(cur_eff_date)

    if source_dataset.dataset_type == ds.DatasetType.LOCAL_DELIM_FILE:
        source_file_path = sc.resolve_app_path(
            source_dataset.resolve_file_path(cur_eff_date_yyyymmdd)
        )
        source_node = lm.LineageNode(
            object_name=source_file_path,
            object_type=source_dataset.dataset_type,
            complex_object=False,
            node_type=lm.LineageNodeType.DATASET,
        )

    elif source_dataset.dataset_type == ds.DatasetType.SPARK_SQL_FILE:
        # elif isinstance(source_dataset, ds.SparkSqlFileDataset):
        # Prepare the sql file name
        sql_file_path = sc.resolve_app_path(
            source_dataset.sql_file_path
        )  # pylint: disable=E1101
        source_node = lm.LineageNode(
            object_name=sql_file_path,
            object_type=source_dataset.dataset_type,
            complex_object=True,
            node_type=lm.LineageNodeType.DATASET,
        )

    else:
        raise RuntimeError("Source dataset type is not expected.")

    # Simulate getting the source dataset metadata from API
    logging.info("Get source dataset metadata")
    target_dataset = ds.get_dataset_from_json(dataset_id=task.target_dataset_id)

    # Get current effective date
    cur_eff_date = ed.get_cur_eff_date(
        schedule_id=target_dataset.schedule_id, cycle_date=cycle_date
    )
    cur_eff_date_yyyymmdd = ed.fmt_date_str_as_yyyymmdd(cur_eff_date)

    if target_dataset.dataset_type == ds.DatasetType.LOCAL_DELIM_FILE:
        target_file_path = sc.resolve_app_path(
            target_dataset.resolve_file_path(cur_eff_date_yyyymmdd)
        )
        target_node = lm.LineageNode(
            object_name=target_file_path,
            object_type=target_dataset.dataset_type,
            complex_object=False,
            node_type=lm.LineageNodeType.DATASET,
        )

    elif target_dataset.dataset_type == ds.DatasetType.SPARK_TABLE:
        qual_target_table_name = target_dataset.get_qualified_table_name()
        target_node = lm.LineageNode(
            object_name=qual_target_table_name,
            object_type=target_dataset.dataset_type,
            complex_object=False,
            node_type=lm.LineageNodeType.DATASET,
        )

    else:
        raise RuntimeError("Target dataset type is not expected.")

    process_node = lm.LineageNode(
        object_name=workflow_id,
        object_type=workflow.workflow_type,
        complex_object=False,
        node_type=lm.LineageNodeType.PROCESS,
    )

    lineage_relationships = []
    lineage_relationships.append(
        lm.LineageRelationship(parent_node=source_node, child_node=process_node)
    )

    lineage_relationships.append(
        lm.LineageRelationship(parent_node=process_node, child_node=target_node)
    )

    other_relationships = []
    if source_node.complex_object:
        if source_node.object_type == ds.DatasetType.SPARK_SQL_FILE:
            other_relationships = capture_dl_for_spark_sql_file(node=source_node)

    lineage_relationships += other_relationships
    return lineage_relationships


def capture_dl_for_spark_sql_file(node: lm.LineageNode) -> list:
    relationships = []
    catalog_objects = [
        "dl_asset_mgmt.tasset",
        "dl_asset_mgmt.tacct_pos",
        "dl_asset_mgmt.tcustomer",
    ]
    sql_file_path = node.object_name
    code = uff.uf_read_file_to_str(file_path=sql_file_path)
    ref_object_token_gen = rp.get_ref_object_gen(
        data_platform=lm.TechPlatformType.SPARK,
        qual_obj_name=sql_file_path,
        code=code,
    )
    ref_object_roles = rp.get_ref_object_roles_for_object(
        token_gen=ref_object_token_gen,
        catalog_objects=catalog_objects,
        cat_all_views=catalog_objects,
    )
    print(ref_object_roles)

    for obj in ref_object_roles:
        parent_node = lm.LineageNode(
            object_name=obj.object_name,
            object_type=lm.get_code_type(qual_object_name=obj.object_name),
            complex_object=False,
            node_type=lm.LineageNodeType.DATASET,
        )
        child_node = node
        relationship = lm.LineageRelationship(
            parent_node=parent_node, child_node=child_node
        )
        relationships.append(relationship)
    # print(relationships)
    return relationships
