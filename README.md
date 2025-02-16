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
  ```

- **Capture data lineage relationships for a workflow via CLI with cycle date override**:
  ```sh
    dl-app-cli capture-relationships --workflow_id "1" --env "dev" --cycle_date "2024-12-24"
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

    /capture-relationships/?workflow_id=2
    /capture-relationships/?workflow_id=2&cycle_date=2024-12-26
  ```
  ##### Invoke the API from Swagger Docs interface
  ```sh
    https://<host name with port number>/docs

  ```

### Sample Input
Not applicable


### API Data (simulated)
These are metadata that would be captured via the metadata management application UI and stored in a database.

##### ingestion_tasks
```
{
    "ingestion_tasks": [
      {
        "ingestion_task_id": "1",
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
        "ingestion_task_id": "2",
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
        "ingestion_task_id": "3",
        "source_dataset_id": "3",
        "target_dataset_id": "13",
        "ingestion_pattern": {
            "loader": "spark",
            "source_type": "local delim file", 
            "target_type": "spark table", 
            "load_type": "incremental", 
            "idempotent": true 
        } 
      }
    ]
  }
  
```

##### distribution_tasks
```
{
    "distribution_tasks": [
      {
        "distribution_task_id": "1",
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
      "rule_id": "1",
      "result": "Pass",
      "expectation": "ExpectColumnValuesCountToMatch",
      "expected": {
        "group_by_column_values": [
          "all"
        ],
        "measure_value": [
          9
        ]
      },
      "actual": {
        "group_by_column_values": [
          "all"
        ],
        "measure_value": [
          9
        ]
      }
    },
    {
      "rule_id": "2",
      "result": "Pass",
      "expectation": "ExpectColumnValueCountsMedianToMatch",
      "expected": {
        "group_by_column_values": [
          "all"
        ],
        "measure_value": [
          "2"
        ]
      },
      "actual": {
        "group_by_column_values": [
          "all"
        ],
        "measure_value": [
          "2"
        ]
      }
    },
    {
      "rule_id": "3",
      "result": "Pass",
      "expectation": "ExpectColumnValuesSumToMatch",
      "expected": {
        "group_by_column_values": [
          "1",
          "2"
        ],
        "measure_value": [
          -65000.0,
          -5000.0
        ]
      },
      "actual": {
        "group_by_column_values": [
          "1",
          "2"
        ],
        "measure_value": [
          -65000.0,
          -5000.0
        ]
      }
    },
    {
      "rule_id": "4",
      "result": "Pass",
      "expectation": "ExpectColumnUniqueValuesCountToMatch",
      "expected": {
        "group_by_column_values": [
          "1",
          "2"
        ],
        "measure_value": [
          7,
          2
        ]
      },
      "actual": {
        "group_by_column_values": [
          "1",
          "2"
        ],
        "measure_value": [
          7,
          2
        ]
      }
    }
  ]
}

```
