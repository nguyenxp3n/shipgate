from pathlib import Path

from project_finalizer.generators.adapters import generate_adapters
from project_finalizer.validators import ValidationContext
from project_finalizer.validators.adapters import AdapterValidator


def test_adapter_unique_product_truth_is_rejected(tmp_path: Path) -> None:
    generated = generate_adapters(tmp_path, project_name="Demo", version="1.0.0")
    target = next(path for path in generated if path.name == "AGENTS.md")
    target.write_text(
        target.read_text(encoding="utf-8") + "\nGuests may access premium billing without login.\n",
        encoding="utf-8",
    )
    report = AdapterValidator().validate(ValidationContext(project_root=tmp_path))
    assert "ADAPTER_NONCANONICAL_TRUTH" in {issue.code for issue in report.issues}
