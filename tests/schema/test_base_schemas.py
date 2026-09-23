import json

from jsonschema import Draft202012Validator


def test_every_root_schema_is_valid(repo_root):
    for path in sorted((repo_root / "schemas").glob("*.schema.json")):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
