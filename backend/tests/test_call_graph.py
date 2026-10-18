
from app.services.graph_builder import build_repository_graph
from app.services.call_resolver import build_symbol_index


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


def test_same_named_functions_in_different_modules_are_not_all_targets(tmp_path):
    (tmp_path / "alpha.py").write_text(
        "def process():\n"
        "    return 'alpha'\n",
        encoding="utf-8",
    )
    (tmp_path / "beta.py").write_text(
        "def process():\n"
        "    return 'beta'\n",
        encoding="utf-8",
    )
    (tmp_path / "caller.py").write_text(
        "from alpha import process\n"
        "\n"
        "def run():\n"
        "    process()\n",
        encoding="utf-8",
    )

    graph = build_repository_graph(str(tmp_path))
    edges = call_edges(graph)

    run_edges = [
        edge
        for edge in edges
        if edge["source"] == "function:caller.py:run"
    ]

    assert [
        edge["target"] for edge in run_edges
    ] == ["function:alpha.py:process"]

def test_unresolved_import_does_not_match_unrelated_function(tmp_path):
    (tmp_path / "beta.py").write_text(
        "def process():\n"
        "    return 'beta'\n",
        encoding="utf-8",
    )

    (tmp_path / "caller.py").write_text(
        "from missing_module import process\n"
        "\n"
        "def run():\n"
        "    process()\n",
        encoding="utf-8",
    )

    graph = build_repository_graph(str(tmp_path))
    edges = call_edges(graph)

    run_edges = [
        edge
        for edge in edges
        if edge["source"] == "function:caller.py:run"
    ]

    assert all(
        edge["target"] != "function:beta.py:process"
        for edge in run_edges
    )



def test_top_level_function_after_class_is_indexed_as_function(tmp_path):
    (tmp_path / "example.py").write_text(
        "class Worker:\n"
        "    def work(self):\n"
        "        return 1\n"
        "\n"
        "def standalone():\n"
        "    return 2\n",
        encoding="utf-8",
    )

    graph = build_repository_graph(str(tmp_path))
    nodes = graph.to_dict()["nodes"]

    standalone_nodes = [
        node for node in nodes
        if node["id"] == "function:example.py:standalone"
    ]

    assert len(standalone_nodes) == 1

    index = build_symbol_index(str(tmp_path))
    standalone = index["standalone"]

    assert len(standalone) == 1
    assert standalone[0]["type"] == "function"
    assert standalone[0].get("class") is None
def test_attribute_call_does_not_target_unrelated_same_named_methods(tmp_path):
    (tmp_path / "requests.py").write_text(
        "class Request:\n"
        "    def prepare(self):\n"
        "        return 1\n"
        "\n"
        "class PreparedRequest:\n"
        "    def prepare(self):\n"
        "        return 2\n"
        "\n"
        "def send(request):\n"
        "    request.prepare()\n",
        encoding="utf-8",
    )

    graph = build_repository_graph(str(tmp_path))
    edges = call_edges(graph)

    send_edges = [
        edge
        for edge in edges
        if edge["source"] == "function:requests.py:send"
    ]

    assert send_edges == []