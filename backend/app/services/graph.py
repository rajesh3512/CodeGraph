import networkx as nx

from app.models.graph import GraphEdge, GraphNode


class CodeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: GraphNode):
        self.graph.add_node(
            node.id,
            type=node.type,
            name=node.name,
            file=node.file,
            line=node.line,
            metadata=node.metadata,
        )

    def add_edge(self, edge: GraphEdge):
        self.graph.add_edge(
            edge.source,
            edge.target,
            type=edge.type,
            metadata=edge.metadata,
        )

    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    def edge_count(self) -> int:
        return self.graph.number_of_edges()

    def to_dict(self) -> dict:
        nodes = []

        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                **data,
            })

        edges = []

        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                **data,
            })

        return {
            "nodes": nodes,
            "edges": edges,
        }