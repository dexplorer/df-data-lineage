from enum import StrEnum
from dataclasses import dataclass


class TechPlatformType(StrEnum):
    TERADATA = "teradata"
    HIVE = "hive"
    INFORMATICA = "informatica"
    SPARK = "spark"


class CodePlatformType(StrEnum):
    DATABASE = "database"
    GIT = "git"


class CodeObjectType(StrEnum):
    SQL_SCRIPT = "sql script"
    PYSPARK_SCRIPT = "pyspark script"
    HIVEQL_SCRIPT = "hql script"
    INFA_WORKFLOW = "xml file"
    JSON_FILE = "json file"


class LineageNodeType(StrEnum):
    DATASET = "dataset"
    PROCESS = "process"


@dataclass
class LineageNode:
    object_name: str
    object_type: str
    complex_object: bool
    node_type: str

    def __init__(
        self,
        object_name: str,
        object_type: str,
        complex_object: bool,
        node_type: str,
    ):
        self.object_name = object_name
        self.object_type = object_type
        self.complex_object = complex_object
        self.node_type = node_type

    # def __repr__(self):
    #     return str(self)


@dataclass
class LineageRelationship:
    parent_node: LineageNode
    child_node: LineageNode

    def __init__(self, parent_node: LineageNode, child_node: LineageNode):
        self.parent_node = parent_node
        self.child_node = child_node

    # def __repr__(self):
    #     return str(self)


@dataclass
class RefObjectToken:
    kind: str
    value: str
    line: int
    line_column: int

    def __repr__(self):
        return str(self)


@dataclass
class RefObject:
    object_name: str
    object_role: str

    # def __repr__(self):
    #     return str(self)


def get_code_type(qual_object_name: str) -> str:
    code_type = ""
    if qual_object_name.endswith(".sql"):
        code_type = CodeObjectType.SQL_SCRIPT

    return code_type
