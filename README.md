# df-data-lineage

This application captures the data lineage relationships at the dataset level as the pipelines run to ingest or distribute data.

Users can view the lineage relationships as a graph which shows the feeds, datasets and processes in the image.

Application can be invoked using CLI or REST API end points. This allows the app to be integrated into a larger data ingestion / distribution framework.

### Define the Environment Variables

Update one of the following .env files which is appropriate for the application hosting pattern.

```
.env.on_prem_vm_native
.env.aws_ec2_native
.env.aws_ec2_container
.env.aws_ecs_container
```

### Install

- **Install via Makefile and pip**:
  ```sh
    make install-dev
  ```

- **Install dot provided by graphviz (in Ubuntu Linux machine)**:
  ```sh
    sudo apt-get update
    sudo apt-get install graphviz
  ```

- **Install dot provided by graphviz (in AWS EC2 AMI Linux machine)**:
  ```sh
    sudo dnf update
    sudo dnf install graphviz
  ```

### Usage Examples

#### App Hosted Natively on a VM/EC2

- **via CLI**:
  ```sh
    dl-app-cli --app_host_pattern "aws_ec2_native" capture-relationships --workflow_id "workflow_1"
    dl-app-cli --app_host_pattern "aws_ec2_native" capture-relationships --workflow_id "workflow_2"
    dl-app-cli --app_host_pattern "aws_ec2_native" capture-relationships --workflow_id "workflow_11"
  ```

- **via CLI with Cycle Date Override**:
  ```sh
    dl-app-cli --app_host_pattern "aws_ec2_native" capture-relationships --workflow_id "workflow_1" --cycle_date "2024-12-26"
    dl-app-cli --app_host_pattern "aws_ec2_native" capture-relationships --workflow_id "workflow_2" --cycle_date "2024-12-26"
    dl-app-cli --app_host_pattern "aws_ec2_native" capture-relationships --workflow_id "workflow_11" --cycle_date "2024-12-26"
  ```

- **via API**:
  ##### Start the API Server
  ```sh
    dl-app-api --app_host_pattern "aws_ec2_native"
  ```
  ##### Invoke the API Endpoint
  ```sh
    https://<host name with port number>/capture-relationships/?workflow_id=<value>
    https://<host name with port number>/capture-relationships/?workflow_id=<value>&cycle_date=<value>

    /capture-relationships/?workflow_id='workflow_1'
    /capture-relationships/?workflow_id='workflow_2'
    /capture-relationships/?workflow_id='workflow_11'
    /capture-relationships/?workflow_id='workflow_1'&cycle_date=2024-12-26
    /capture-relationships/?workflow_id='workflow_2'&cycle_date=2024-12-26
    /capture-relationships/?workflow_id='workflow_11'&cycle_date=2024-12-26
  ```
  ##### Invoke the API from Swagger Docs interface
  ```sh
    https://<host name with port number>/docs
  ```

#### App Hosted as Container on a VM/EC2

- **via CLI**:
  ```sh
    docker run \
    --mount=type=bind,src=/home/ec2-user/workspaces/nas,dst=/nas \
    --rm -it df-data-lineage \
    dl-app-cli --app_host_pattern "aws_ec2_container" capture-relationships --workflow_id "workflow_1"
  ```

- **via CLI with Cycle Date Override**:
  ```sh
    docker run \
    --mount=type=bind,src=/home/ec2-user/workspaces/nas,dst=/nas \
    --rm -it df-data-lineage:latest \
    dl-app-cli --app_host_pattern "aws_ec2_container" capture-relationships --workflow_id "workflow_1" --cycle_date "2024-12-26"
  ```

- **via API**:
  ##### Start the API server
  ```sh
    docker run \
    --mount=type=bind,src=/home/ec2-user/workspaces/nas,dst=/nas \
    -p 9090:9090 \
    --rm -it df-data-lineage:latest \
    dl-app-api --app_host_pattern "aws_ec2_container"
  ```

#### App Hosted as a Container on AWS ECS

- **via CLI**:
  ##### Invoke CLI App by Deploying ECS Task using ECS Task Definition 
  Enter the following command override under 'Container Overrides'. 
  ```sh
    "dl-app-cli", "--app_host_pattern", "aws_ecs_container", "capture-relationships", "--workflow_id", "workflow_101", "--cycle_date", "2024-12-26"
  ```

- **via API**:
  ##### Invoke API App by Deploying ECS Task using ECS Task Definition 
  Enter the following command override under 'Container Overrides'. 
  ```sh
    "dl-app-api", "--app_host_pattern", "aws_ecs_container"
  ```

### Sample Input
Not applicable


### API Data (simulated)
These are metadata that would be captured via the metadata management application UI and stored in a database.

##### Workflows
```json
{
    "workflows": [
      {
        "workflow_id": "workflow_1",
        "workflow_type": "ingestion", 
        "ingestion_task_id": "1",
        "pre_tasks": [
          {
            "name": "data quality",
            "required_parameters": {
              "dataset_id": "1"
            }
          },
          {
            "name": "data profile",
            "required_parameters": {
              "dataset_id": "1"
            }
          }
        ],
        "post_tasks": [
        ]
      },
      {
        "workflow_id": "workflow_2",
        "workflow_type": "ingestion", 
        "ingestion_task_id": "2",
        "pre_tasks": [
          {
            "name": "data quality",
            "required_parameters": {
              "dataset_id": "2"
            }
          },
          {
            "name": "data quality ml",
            "required_parameters": {
              "dataset_id": "2"
            }
          },
          {
            "name": "data profile",
            "required_parameters": {
              "dataset_id": "2"
            }
          }
        ],
        "post_tasks": [
          {
            "name": "data reconciliation",
            "required_parameters": {
              "dataset_id": "12"
            }
          }
        ]
      },
      {
        "workflow_id": "workflow_3",
        "workflow_type": "ingestion", 
        "ingestion_task_id": "3",
        "pre_tasks": [
          {
            "name": "data quality",
            "required_parameters": {
              "dataset_id": "3"
            }
          },
          {
            "name": "data profile",
            "required_parameters": {
              "dataset_id": "3"
            }
          }
        ],
        "post_tasks": [
        ]
      },
      {
        "workflow_id": "workflow_11",
        "workflow_type": "distribution", 
        "distribution_task_id": "11",
        "pre_tasks": [
        ],
        "post_tasks": [
          {
            "name": "data quality",
            "required_parameters": {
              "dataset_id": "14"
            }
          },
          {
            "name": "data quality ml",
            "required_parameters": {
              "dataset_id": "14"
            }
          }
        ]
      }
    ]
  }
    
```

### Sample Output 

Data lineage relationships for workflow 1

```
parent_node,child_node
"{'object_name': '/workspaces/df-data-lineage/data/in/assets_20241226.csv', 'object_type': 'local delim file', 'complex_object': False, 'node_type': 'feed'}","{'object_name': 'workflow_1', 'object_type': 'ingestion', 'complex_object': False, 'node_type': 'process'}"
"{'object_name': 'workflow_1', 'object_type': 'ingestion', 'complex_object': False, 'node_type': 'process'}","{'object_name': 'dl_asset_mgmt.tasset', 'object_type': 'spark table', 'complex_object': False, 'node_type': 'dataset'}"
```

Data lineage relationships for workflow 2

```
parent_node,child_node
"{'object_name': '/workspaces/df-data-lineage/data/in/acct_positions_20241226.csv', 'object_type': 'local delim file', 'complex_object': False, 'node_type': 'feed'}","{'object_name': 'workflow_2', 'object_type': 'ingestion', 'complex_object': False, 'node_type': 'process'}"
"{'object_name': 'workflow_2', 'object_type': 'ingestion', 'complex_object': False, 'node_type': 'process'}","{'object_name': 'dl_asset_mgmt.tacct_pos', 'object_type': 'spark table', 'complex_object': False, 'node_type': 'dataset'}"
```

Data lineage relationships for workflow 11

```
parent_node,child_node
"{'object_name': '/workspaces/df-data-lineage/sql/ext_asset_value_agg.sql', 'object_type': 'spark sql file', 'complex_object': True, 'node_type': 'dataset'}","{'object_name': 'workflow_11', 'object_type': 'distribution', 'complex_object': False, 'node_type': 'process'}"
"{'object_name': 'workflow_11', 'object_type': 'distribution', 'complex_object': False, 'node_type': 'process'}","{'object_name': '/workspaces/df-data-lineage/data/out/asset_value_agg_20241226.dat', 'object_type': 'local delim file', 'complex_object': False, 'node_type': 'feed'}"
"{'object_name': 'dl_asset_mgmt.tasset', 'object_type': '', 'complex_object': False, 'node_type': 'dataset'}","{'object_name': '/workspaces/df-data-lineage/sql/ext_asset_value_agg.sql', 'object_type': 'spark sql file', 'complex_object': True, 'node_type': 'dataset'}"
"{'object_name': 'dl_asset_mgmt.tacct_pos', 'object_type': '', 'complex_object': False, 'node_type': 'dataset'}","{'object_name': '/workspaces/df-data-lineage/sql/ext_asset_value_agg.sql', 'object_type': 'spark sql file', 'complex_object': True, 'node_type': 'dataset'}"
```

Data lineage graph for workflow 11

![Lineage Graph](docs/lineage_graph.svg?raw=true "Lineage Graph")
