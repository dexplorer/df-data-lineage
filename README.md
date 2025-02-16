# df-data-lineage

### Install

- **Install via Makefile and pip**:
  ```sh
    make install
  ```

### Usage Examples

- **Capture data lineage relationships for a workflow via CLI**:
  ```sh
    dl-app-cli capture-relationships --workflow_id "1" --env "dev"
    dl-app-cli capture-relationships --workflow_id "2" --env "dev"
    dl-app-cli capture-relationships --workflow_id "11" --env "dev"
  ```

- **Capture data lineage relationships for a workflow via CLI with cycle date override**:
  ```sh
    dl-app-cli capture-relationships --workflow_id "1" --env "dev" --cycle_date "2024-12-24"
    dl-app-cli capture-relationships --workflow_id "2" --env "dev" --cycle_date "2024-12-24"
    dl-app-cli capture-relationships --workflow_id "11" --env "dev" --cycle_date "2024-12-24"
  ```

- **Capture data lineage relationships for a workflow via API**:
  ##### Start the API server
  ```sh
    dl-app-api --env "dev"
  ```
  ##### Invoke the API endpoint
  ```sh
    https://<host name with port number>/capture-relationships/?workflow_id=<value>
    https://<host name with port number>/capture-relationships/?workflow_id=<value>&cycle_date=<value>

    /capture-relationships/?workflow_id=1
    /capture-relationships/?workflow_id=2
    /capture-relationships/?workflow_id=11
    /capture-relationships/?workflow_id=1&cycle_date=2024-12-26
    /capture-relationships/?workflow_id=2&cycle_date=2024-12-26
    /capture-relationships/?workflow_id=11&cycle_date=2024-12-26
  ```
  ##### Invoke the API from Swagger Docs interface
  ```sh
    https://<host name with port number>/docs

  ```

### Sample Input
Not applicable


### API Data (simulated)
These are metadata that would be captured via the metadata management application UI and stored in a database.

##### integration_tasks
```
{
    "integration_tasks": [
      {
        "task_id": "1",
        "task_type": "ingestion",
        "source_dataset_id": "1",
        "target_dataset_id": "11",
        "ingestion_pattern": {
            "loader": "spark",
            "source_type": "local delim file", 
            "target_type": "spark table", 
            "load_type": "full", 
            "idempotent": true 
        } 
      },
      {
        "task_id": "2",
        "task_type": "ingestion",
        "source_dataset_id": "2",
        "target_dataset_id": "12",
        "ingestion_pattern": {
            "loader": "spark",
            "source_type": "local delim file", 
            "target_type": "spark table", 
            "load_type": "incremental", 
            "idempotent": true 
        } 
      },
      {
        "task_id": "3",
        "task_type": "ingestion",
        "source_dataset_id": "3",
        "target_dataset_id": "13",
        "ingestion_pattern": {
            "loader": "spark",
            "source_type": "local delim file", 
            "target_type": "spark table", 
            "load_type": "incremental", 
            "idempotent": true 
        } 
      },
      {
        "task_id": "11",
        "task_type": "distribution",
        "source_dataset_id": "4",
        "target_dataset_id": "14",
        "distribution_pattern": {
            "extracter": "spark",
            "source_type": "spark sql file", 
            "target_type": "local delim file" 
        } 
      }      
    ]
  }
    
```

### Sample Output 

```
Data lineage relationships for workflow 1

{
  "results": [
    {
      "parent_node": {
        "object_name": "/workspaces/df-data-lineage/data/in/assets_20241226.csv",
        "object_type": "local delim file",
        "complex_object": false,
        "node_type": "dataset"
      },
      "child_node": {
        "object_name": "1",
        "object_type": "ingestion",
        "complex_object": false,
        "node_type": "process"
      }
    },
    {
      "parent_node": {
        "object_name": "1",
        "object_type": "ingestion",
        "complex_object": false,
        "node_type": "process"
      },
      "child_node": {
        "object_name": "dl_asset_mgmt.tasset",
        "object_type": "spark table",
        "complex_object": false,
        "node_type": "dataset"
      }
    }
  ]
}

Data lineage relationships for workflow 2

{
  "results": [
    {
      "parent_node": {
        "object_name": "/workspaces/df-data-lineage/data/in/acct_positions_20241226.csv",
        "object_type": "local delim file",
        "complex_object": false,
        "node_type": "dataset"
      },
      "child_node": {
        "object_name": "2",
        "object_type": "ingestion",
        "complex_object": false,
        "node_type": "process"
      }
    },
    {
      "parent_node": {
        "object_name": "2",
        "object_type": "ingestion",
        "complex_object": false,
        "node_type": "process"
      },
      "child_node": {
        "object_name": "dl_asset_mgmt.tacct_pos",
        "object_type": "spark table",
        "complex_object": false,
        "node_type": "dataset"
      }
    }
  ]
}

Data lineage relationships for workflow 11

{
  "results": [
    {
      "parent_node": {
        "object_name": "/workspaces/df-data-lineage/sql/ext_asset_value_agg.sql",
        "object_type": "spark sql file",
        "complex_object": true,
        "node_type": "dataset"
      },
      "child_node": {
        "object_name": "11",
        "object_type": "distribution",
        "complex_object": false,
        "node_type": "process"
      }
    },
    {
      "parent_node": {
        "object_name": "11",
        "object_type": "distribution",
        "complex_object": false,
        "node_type": "process"
      },
      "child_node": {
        "object_name": "/workspaces/df-data-lineage/data/out/asset_value_agg_20241226.dat",
        "object_type": "local delim file",
        "complex_object": false,
        "node_type": "dataset"
      }
    },
    {
      "parent_node": {
        "object_name": "dl_asset_mgmt.tasset",
        "object_type": "",
        "complex_object": false,
        "node_type": "dataset"
      },
      "child_node": {
        "object_name": "/workspaces/df-data-lineage/sql/ext_asset_value_agg.sql",
        "object_type": "spark sql file",
        "complex_object": true,
        "node_type": "dataset"
      }
    },
    {
      "parent_node": {
        "object_name": "dl_asset_mgmt.tacct_pos",
        "object_type": "",
        "complex_object": false,
        "node_type": "dataset"
      },
      "child_node": {
        "object_name": "/workspaces/df-data-lineage/sql/ext_asset_value_agg.sql",
        "object_type": "spark sql file",
        "complex_object": true,
        "node_type": "dataset"
      }
    }
  ]
}

```
