import re
from dl_app.model import models as mm


def get_ref_object_gen(
    data_platform: str,
    qual_obj_name: str,
    code: str,
):
    td_token_specification = [
        ("TARGET_OBJECT_INSERT", r"insert into [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+"),
        ("TARGET_OBJECT_UPDATE", r"update [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+"),
        ("TARGET_OBJECT_DELETE_1", r"delete from [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+"),
        ("TARGET_OBJECT_DELETE_2", r"delete [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+"),
    ]

    hive_token_specification = [
        (
            "TARGET_OBJECT_INSERT",
            r"insert overwrite table [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+",
        ),
    ]

    spark_token_specification = [
        (
            "TARGET_OBJECT_INSERT",
            r".write.insertInto(tableName\=\'[A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+\'",
        ),
        (
            "TARGET_OBJECT_INSERT",
            r".write.saveAsTable(name\=\'[A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+\'",
        ),
    ]

    spark_sql_token_specification = [
        (
            "TARGET_OBJECT_INSERT",
            r"insert overwrite table [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+",
        ),
    ]

    infa_token_specification = [
        ("TARGET_OBJECT_INFA", r"<target [^\n]+ name \=\"[A-Za-z0-9_]+\""),
        ("SOURCE_OBJECT_INFA", r"<target [^\n]+ name \=\"[A-Za-z0-9_]+\""),
        ("TARGET_OBJECT_INSERT", r"insert into [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+"),
        ("TARGET_OBJECT_UPDATE", r"update [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+"),
        ("TARGET_OBJECT_DELETE_1", r"delete from [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+"),
        ("TARGET_OBJECT_DELETE_2", r"delete [A-Za-z0-9_/\$]+.[A-Za-z0-9_/\$]+"),
    ]

    std_token_specification = [
        ("OBJECT", r"[A-Za-z0-9_/\$]+\.[A-Za-z0-9_/\$]+"),
    ]

    code_type = mm.get_code_type(qual_obj_name)
    token_specification = []
    if (
        data_platform == mm.TechPlatformType.TERADATA
        and code_type == mm.CodeObjectType.SQL_SCRIPT
    ):
        token_specification = td_token_specification
    elif (
        data_platform == mm.TechPlatformType.HIVE
        and code_type == mm.CodeObjectType.HIVEQL_SCRIPT
    ):
        token_specification = hive_token_specification
    elif (
        data_platform == mm.TechPlatformType.SPARK
        and code_type == mm.CodeObjectType.PYSPARK_SCRIPT
    ):
        token_specification = spark_token_specification
    elif (
        data_platform == mm.TechPlatformType.SPARK
        and code_type == mm.CodeObjectType.SQL_SCRIPT
    ):
        token_specification = spark_sql_token_specification
    elif (
        data_platform == mm.TechPlatformType.INFORMATICA
        and code_type == mm.CodeObjectType.INFA_WORKFLOW
    ):
        token_specification = infa_token_specification

    token_specification += std_token_specification

    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_specification)

    line_num = 1
    line_start = 0
    for mo in re.finditer(pattern=tok_regex, string=code, flags=re.IGNORECASE):
        kind = mo.lastgroup
        value = mo.group()
        line_column = mo.start() - line_start

        if kind.startswith("TARGET_OBJECT"):
            yield mm.RefObjectToken(kind, value, line_num, line_column)
        elif kind == "OBJECT":
            yield mm.RefObjectToken(kind, value, line_num, line_column)
        elif kind == "NEWLINE":
            line_start = mo.end()
            line_num += 1
            continue


def get_ref_object_roles_for_object(
    token_gen, catalog_objects: list, cat_all_views: list
) -> list:
    prog = re.compile(
        pattern="^(insert into |update |delete from |delete |insert overwrite table |<target [^\n]+ name =)",
        flags=re.IGNORECASE,
    )
    ref_objects = []
    for token in token_gen:
        object_name = prog.sub(repl="", string=token.value)
        if object_name in catalog_objects or object_name in cat_all_views:
            object_role = "source"
            if token.kind.startswith("TARGET_OBJECT"):
                object_role = "target"

            ref_object = mm.RefObject(
                object_name=object_name,
                object_role=object_role,
            )
            ref_objects.append(ref_object)
    return dedupe_object_roles(ref_objects)


def dedupe_object_roles(ref_objects: list) -> list:
    ref_objects_uniq = []
    target_roles = {
        obj.object_name: obj for obj in ref_objects if obj.object_role == "target"
    }
    source_roles = {
        obj.object_name: obj for obj in ref_objects if obj.object_role == "source"
    }

    for obj in target_roles.values():
        ref_objects_uniq.append(obj)

    for obj in source_roles.values():
        ref_objects_uniq.append(obj)

    return ref_objects_uniq


def get_role_for_ref_object(object_name: str, ref_objects: list) -> str:
    for obj in ref_objects:
        if obj["object name"] == object_name:
            return obj["object role"]
