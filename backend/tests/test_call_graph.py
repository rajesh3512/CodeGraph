
from app.services.graph_builder import build_repository_graph


def call_edges(graph):
    return [
        edge
        for edge in graph.to_dict()["edges"]
        if edge["type"] == "calls"
    ]


def test_call_edges_are_extracted_from_multiple_files(tmp_path):
    (tmp_path / "target.py").write_text(
        "def target():\n    return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "first.py").write_text(
        "def first():\n    target()\n",
        encoding="utf-8",
    )
    (tmp_path / "second.py").write_text(
        "def second():\n    target()\n",
        encoding="utf-8",
    )

    graph = build_repository_graph(str(tmp_path))
    edges = call_edges(graph)

    assert len(edges) == 2
    assert {
        (edge["source"], edge["target"])
        for edge in edges
    } == {
        ("function:first.py:first", "function:target.py:target"),
        ("function:second.py:second", "function:target.py:target"),
    }


def test_self_method_call_creates_method_edge(tmp_path):
    (tmp_path / "worker.py").write_text(
        "class Worker:\n"
        "    def run(self):\n"
        "        self.work()\n"
        "\n"
        "    def work(self):\n"
        "        return 1\n",
        encoding="utf-8",
    )

    graph = build_repository_graph(str(tmp_path))
    edges = call_edges(graph)

    assert any(
        edge["source"] == "method:worker.py:Worker:run"
        and edge["target"] == "method:worker.py:Worker:work"
        for edge in edges
    )
