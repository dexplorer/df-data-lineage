from metadata import dataset as ds
from metadata import data_source as dsrc
from metadata import workflow as wf
from metadata import integration_task as it
from app_calendar import eff_date as ed
from dl_app.regex_parser import parser as rp
from dl_app.model import models as mm
from dl_app.graph import draw as gd

from config.settings import ConfigParms as sc
from utils import file_io as uff
from utils import csv_io as ufc
from utils.enums import StoragePlatform
from utils import aws_s3_io as ufas

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

    # Simulate getting the data source metadata from API
    data_source = dsrc.get_data_source_from_json(
        data_source_id=source_dataset.data_source_id
    )

    # Get current effective date
    cur_eff_date = ed.get_cur_eff_date(
        schedule_id=source_dataset.schedule_id, cycle_date=cycle_date
    )
    cur_eff_date_yyyymmdd = ed.fmt_date_str_as_yyyymmdd(cur_eff_date)

    if source_dataset.dataset_type == ds.DatasetType.LOCAL_DELIM_FILE:
        source_file_path = sc.resolve_app_path(
            source_dataset.resolve_file_path(
                date_str=cur_eff_date_yyyymmdd,
                data_source_user=data_source.data_source_user,
            )
        )
        source_node = mm.LineageNode(
            object_name=source_file_path,
            object_type=source_dataset.dataset_type,
            complex_object=False,
            node_type=mm.LineageNodeType.FEED.value,
        )

    elif source_dataset.dataset_type == ds.DatasetType.SPARK_SQL_FILE:
        # elif isinstance(source_dataset, ds.SparkSqlFileDataset):
        # Prepare the sql file name
        sql_file_path = sc.resolve_app_path(
            source_dataset.sql_file_path
        )  # pylint: disable=E1101
        source_node = mm.LineageNode(
            object_name=sql_file_path,
            object_type=source_dataset.dataset_type,
            complex_object=True,
            node_type=mm.LineageNodeType.DATASET.value,
        )

    elif source_dataset.dataset_type == ds.DatasetType.AWS_S3_DELIM_FILE:
        source_file_uri = sc.resolve_app_path(
            source_dataset.resolve_file_uri(
                date_str=cur_eff_date_yyyymmdd,
                data_source_user=data_source.data_source_user,
            )
        )
        source_node = mm.LineageNode(
            object_name=source_file_uri,
            object_type=source_dataset.dataset_type,
            complex_object=False,
            node_type=mm.LineageNodeType.FEED.value,
        )

    else:
        raise RuntimeError("Source dataset type is not expected.")

    # Simulate getting the source dataset metadata from API
    logging.info("Get source dataset metadata")
    target_dataset = ds.get_dataset_from_json(dataset_id=task.target_dataset_id)

    # Simulate getting the data source metadata from API
    data_source = dsrc.get_data_source_from_json(
        data_source_id=target_dataset.data_source_id
    )

    # Get current effective date
    cur_eff_date = ed.get_cur_eff_date(
        schedule_id=target_dataset.schedule_id, cycle_date=cycle_date
    )
    cur_eff_date_yyyymmdd = ed.fmt_date_str_as_yyyymmdd(cur_eff_date)

    if target_dataset.dataset_type == ds.DatasetType.LOCAL_DELIM_FILE:
        target_file_path = sc.resolve_app_path(
            target_dataset.resolve_file_path(
                date_str=cur_eff_date_yyyymmdd,
                data_source_user=data_source.data_source_user,
            )
        )
        target_node = mm.LineageNode(
            object_name=target_file_path,
            object_type=target_dataset.dataset_type,
            complex_object=False,
            node_type=mm.LineageNodeType.FEED.value,
        )

    elif target_dataset.dataset_type == ds.DatasetType.SPARK_TABLE:
        qual_target_table_name = target_dataset.get_qualified_table_name()
        target_node = mm.LineageNode(
            object_name=qual_target_table_name,
            object_type=target_dataset.dataset_type,
            complex_object=False,
            node_type=mm.LineageNodeType.DATASET.value,
        )

    elif target_dataset.dataset_type == ds.DatasetType.AWS_S3_DELIM_FILE:
        target_file_uri = sc.resolve_app_path(
            target_dataset.resolve_file_uri(
                date_str=cur_eff_date_yyyymmdd,
                data_source_user=data_source.data_source_user,
            )
        )
        target_node = mm.LineageNode(
            object_name=target_file_uri,
            object_type=target_dataset.dataset_type,
            complex_object=False,
            node_type=mm.LineageNodeType.FEED.value,
        )

    else:
        raise RuntimeError("Target dataset type is not expected.")

    process_node = mm.LineageNode(
        object_name=workflow_id,
        object_type=workflow.workflow_type,
        complex_object=False,
        node_type=mm.LineageNodeType.PROCESS.value,
    )

    lineage_relationships = []
    lineage_relationships.append(
        mm.LineageRelationship(parent_node=source_node, child_node=process_node)
    )

    lineage_relationships.append(
        mm.LineageRelationship(parent_node=process_node, child_node=target_node)
    )

    other_relationships = []
    if source_node.complex_object:
        if source_node.object_type == ds.DatasetType.SPARK_SQL_FILE:
            other_relationships = capture_dl_for_spark_sql_file(node=source_node)

    lineage_relationships += other_relationships

    if sc.data_out_storage_platform == StoragePlatform.AWS_S3_STORAGE:
        s3_client = ufas.get_s3_client(s3_region=sc.s3_region)
    else:
        s3_client = None

    lineage_data_file_path = (
        f"{sc.app_data_out_path}/lineage_relationships_{workflow_id}.csv"
    )
    logging.info(
        "Writing the lineage relationships to file %s.", lineage_data_file_path
    )
    if sc.data_out_storage_platform == StoragePlatform.NAS_STORAGE:
        ufc.uf_write_list_of_data_cls_obj_to_delim_file(
            dataclass_obj_list=lineage_relationships, file_path=lineage_data_file_path
        )

    elif sc.data_out_storage_platform == StoragePlatform.AWS_S3_STORAGE:
        ufas.uf_write_list_of_data_cls_obj_to_delim_file(
            dataclass_obj_list=lineage_relationships,
            file_uri=lineage_data_file_path,
            s3_client=s3_client,
        )

    else:
        raise RuntimeError(
            "Data out storage platform is invalid. Unable to write the lineage relationships."
        )

    all_lineage_data_file_path = f"{sc.app_data_out_path}/lineage_relationships.csv"
    logging.info(
        "Merging the lineage relationships to file %s.", all_lineage_data_file_path
    )
    if sc.data_out_storage_platform == StoragePlatform.NAS_STORAGE:
        ufc.uf_merge_csv_files(
            in_file_dir_path=sc.app_data_out_path,
            out_file=all_lineage_data_file_path,
            in_file_pattern="lineage_relationships_workflow*",
        )
    elif sc.data_out_storage_platform == StoragePlatform.AWS_S3_STORAGE:
        ufas.uf_merge_csv_files(
            out_s3_obj_uri=all_lineage_data_file_path,
            in_s3_bucket=sc.s3_data_out_bucket,
            in_s3_prefix=f"{sc.app_name}/lineage_relationships_workflow",
            # in_s3_prefix=sc.app_name,
            s3_client=s3_client,
        )

    logging.info("Reading lineage relationships file %s.", all_lineage_data_file_path)
    if sc.data_out_storage_platform == StoragePlatform.NAS_STORAGE:
        lineage_relationships = ufc.uf_read_delim_file_to_list_of_dict(
            file_path=all_lineage_data_file_path
        )
    elif sc.data_out_storage_platform == StoragePlatform.AWS_S3_STORAGE:
        lineage_relationships = ufas.uf_read_delim_file_to_list_of_dict(
            s3_obj_uri=all_lineage_data_file_path, s3_client=s3_client
        )

    lineage_graph_file_path = f"{sc.app_img_out_path}/lineage_graph.svg"
    logging.info(
        "Saving the lineage relationship plots to file %s.", lineage_graph_file_path
    )
    nx_graph = gd.create_nx_graph(lineage_relationships=lineage_relationships)
    dot_graph = gd.convert_to_dot_graph(nx_graph=nx_graph, root_node=workflow_id)

    if sc.data_out_storage_platform == StoragePlatform.NAS_STORAGE:
        dot_graph.write_svg(lineage_graph_file_path)  # pylint: disable=E1101
    elif sc.data_out_storage_platform == StoragePlatform.AWS_S3_STORAGE:
        # return dot_graph.create_svg()  # pylint: disable=E1101
        ufas.uf_write_image_file(
            image_content=dot_graph.create_svg(),
            file_uri=lineage_graph_file_path,
            s3_client=s3_client,
        )

    return lineage_relationships


def capture_dl_for_spark_sql_file(node: mm.LineageNode) -> list:
    relationships = []
    catalog_objects = [
        "dl_asset_mgmt.tasset",
        "dl_asset_mgmt.tacct_pos",
        "dl_asset_mgmt.tcustomer",
    ]
    sql_file_path = node.object_name
    code = uff.uf_read_file_to_str(file_path=sql_file_path)
    ref_object_token_gen = rp.get_ref_object_gen(
        data_platform=mm.TechPlatformType.SPARK,
        qual_obj_name=sql_file_path,
        code=code,
    )
    ref_object_roles = rp.get_ref_object_roles_for_object(
        token_gen=ref_object_token_gen,
        catalog_objects=catalog_objects,
        cat_all_views=catalog_objects,
    )
    # print(ref_object_roles)

    for obj in ref_object_roles:
        parent_node = mm.LineageNode(
            object_name=obj.object_name,
            object_type=mm.get_code_type(qual_object_name=obj.object_name),
            complex_object=False,
            node_type=mm.LineageNodeType.DATASET.value,
        )
        child_node = node
        relationship = mm.LineageRelationship(
            parent_node=parent_node, child_node=child_node
        )
        relationships.append(relationship)
    # print(relationships)
    return relationships
