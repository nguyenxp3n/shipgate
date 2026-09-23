from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from project_finalizer.models import ValidationReport
from project_finalizer.validators import ValidationContext, Validator, ValidatorRegistry
from project_finalizer.validators.api import ApiValidator
from project_finalizer.validators.audit import AuditValidator
from project_finalizer.validators.authority import AuthorityValidator
from project_finalizer.validators.feasibility import FeasibilityValidator
from project_finalizer.validators.ownership import OwnershipValidator
from project_finalizer.validators.references import ReferenceValidator
from project_finalizer.validators.structure import StructureValidator
from project_finalizer.validators.syntax import SyntaxValidator
from project_finalizer.validators.work_packages import WorkPackageValidator


def build_default_registry() -> ValidatorRegistry:
    return ValidatorRegistry(
        (
            SyntaxValidator(),
            StructureValidator(),
            ReferenceValidator(),
            OwnershipValidator(),
            AuthorityValidator(),
            ApiValidator(),
            FeasibilityValidator(),
            WorkPackageValidator(),
            AuditValidator(),
        )
    )


def run_validators(
    project_root: Path, validators: Iterable[Validator] | None = None
) -> ValidationReport:
    registry = ValidatorRegistry(validators) if validators is not None else build_default_registry()
    return registry.run(ValidationContext(project_root=project_root.resolve()))
