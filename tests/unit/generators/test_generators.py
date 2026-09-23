from pathlib import Path

from project_finalizer.artifacts import ArtifactGraph, ArtifactRecord
from project_finalizer.generators.module_index import generate_module_index
from project_finalizer.io import ProjectFS


def _graph() -> ArtifactGraph:
    return ArtifactGraph(
        (ArtifactRecord("MODULE_SOURCE", "modules.yaml", (), {}, generated=False),)
    )


def test_module_index_is_deterministic_across_input_order(tmp_path: Path) -> None:
    fs = ProjectFS(tmp_path)
    fs.write_yaml_atomic("modules.yaml", {"modules": ["a", "b"]})
    modules_a = [{"id": "z", "owned_data": ["z"]}, {"id": "a", "owned_data": ["a"]}]
    modules_b = list(reversed(modules_a))
    graph = generate_module_index(
        fs, _graph(), modules_a, output="module-index.md", source_ids=("MODULE_SOURCE",)
    )
    first = (tmp_path / "module-index.md").read_bytes()
    generate_module_index(
        fs, graph, modules_b, output="module-index.md", source_ids=("MODULE_SOURCE",)
    )
    assert (tmp_path / "module-index.md").read_bytes() == first


def test_generation_registers_exact_source_hashes(tmp_path: Path) -> None:
    fs = ProjectFS(tmp_path)
    fs.write_yaml_atomic("modules.yaml", {"modules": ["a"]})
    graph = generate_module_index(
        fs,
        _graph(),
        [{"id": "a", "owned_data": ["users"]}],
        output="module-index.md",
        source_ids=("MODULE_SOURCE",),
    )
    record = next(record for record in graph.records if record.artifact_id == "MODULE_INDEX")
    assert record.built_from_hashes == {"MODULE_SOURCE": fs.sha256("modules.yaml")}
