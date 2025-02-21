import networkx as nx

# import itertools
from functools import lru_cache
import pydot
from dl_app.model import models as mm
from utils import csv_io as ufc
import logging


@lru_cache(maxsize=1)
def create_nx_graph(lineage_data_file_path: str):
    logging.info("Reading lineage relationships file %s.", lineage_data_file_path)
    lineage_relationships = ufc.uf_read_delim_file_to_list_of_dict(
        file_path=lineage_data_file_path
    )

    logging.info("Generating lineage graph")
    nx_graph = nx.DiGraph()
    nodes, edges = generate_graph_nodes_and_edges(
        lineage_relationships=lineage_relationships
    )
    nx_graph.add_nodes_from(nodes)
    nx_graph.add_edges_from(edges)
    logging.info("Generated lineage graph has %d nodes.", len(nx_graph))
    return nx_graph


def generate_graph_nodes_and_edges(
    lineage_relationships: list[mm.LineageRelationship | dict],
):
    node_ids = []
    nodes = []
    edges = []
    for relationship in lineage_relationships:

        try:
            if isinstance(relationship, mm.LineageRelationship):
                parent_node = relationship.parent_node
                child_node = relationship.child_mode
            elif isinstance(relationship, dict):
                relationship = mm.LineageRelationship.from_dict(relationship)
                parent_node = relationship.parent_node
                child_node = relationship.child_node
            else:
                raise RuntimeError(
                    "Relationship data should either be of type LineageRelationship or dict."
                )
        except RuntimeError as error:
            logging.error(error)

        if parent_node.object_name not in node_ids:
            nodes.append(build_graph_node(lineage_node=parent_node))
            node_ids.append(parent_node.object_name)

        if child_node.object_name not in node_ids:
            nodes.append(build_graph_node(lineage_node=child_node))
            node_ids.append(child_node.object_name)

        edges.append(build_graph_edge(lineage_relationship=relationship))
    return nodes, edges


def build_graph_node(lineage_node: mm.LineageNode):
    node_id = lineage_node.object_name
    node_attributes = {"category": lineage_node.node_type}
    return (node_id, node_attributes)


def build_graph_edge(lineage_relationship: mm.LineageRelationship):
    parent_node_id = lineage_relationship.parent_node.object_name
    child_node_id = lineage_relationship.child_node.object_name
    edge_attributes = {}
    return (parent_node_id, child_node_id, edge_attributes)


def draw_graph(nx_graph, root_node: str, lineage_graph_file_path: str):
    dot_graph = networkx_to_dot(nx_graph, root_node)

    dot_graph.write_svg(lineage_graph_file_path)  # pylint: disable=E1101
    return dot_graph.create_svg()  # pylint: disable=E1101


def networkx_to_dot(nx_graph, root_node):
    strict = nx.number_of_selfloops(nx_graph) == 0 and not nx_graph.is_multigraph()
    dot_graph = pydot.Dot(graph_type="digraph", strict=strict)
    dot_graph.graph_defaults = nx_graph.graph.get("graph", {})
    dot_graph.set_node_defaults(
        shape="box",
        style="filled",
        color="black",
        fillcolor="lightgoldenrod",
        fontname="Microsoft JhengHei",
        labelfontsize="10.0",
    )
    dot_graph.set_edge_defaults(
        style="solid", fontname="Microsoft JhengHei", labelfontsize="10.0"
    )

    for n, node_data in nx_graph.nodes(data=True):
        if n:
            # node label
            node_label = build_node_label(n, node_data)

            # node style
            if n == root_node:
                node_style = "bold"
            else:
                node_style = "filled"

            # node shape and fill color
            if node_data["category"] == "process":
                node_shape = "ellipse"
                node_fill_color = "gray80"
            elif node_data["category"] == "feed":
                node_shape = "note"
                node_fill_color = "snow"
            elif node_data["category"] == "partner":
                node_shape = "oval"
                node_fill_color = "plum"
            elif node_data["category"] == "dataset":
                node_shape = "box"
                node_fill_color = "lightseagreen"
            else:
                node_shape = "box"
                node_fill_color = "lightgoldenrod"

            dot_node = pydot.Node(
                n,
                label=node_label,
                shape=node_shape,
                fillcolor=node_fill_color,
                style=node_style,
            )
            dot_graph.add_node(dot_node)

    for u, v, edge_data in nx_graph.edges(data=True):
        if v:
            edge_style = "solid"
            edge_label = build_edge_label(edge_data)

            dot_edge = pydot.Edge(str(u), str(v), label=edge_label, style=edge_style)
            dot_graph.add_edge(dot_edge)
    return dot_graph


def build_node_label(node, node_data):
    label_items = [node, node_data["category"]]
    node_label = "\n".join(label_items)
    return node_label


def build_edge_label(_edge_data):
    edge_label = ""
    return edge_label


# def transform_node_id(qual_object_name: str):
#     node_id = ''
#     prefix, delim, ext = qual_object_name.rpartition('.')

#     if ext in ['xml', 'XML']:
#         node_id = prefix
#     else:
#         node_id = qual_object_name
#     return node_id
