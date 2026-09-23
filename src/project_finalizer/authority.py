from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from project_finalizer.errors import ExitCode, WorkflowError


@dataclass(frozen=True)
class AuthoritySubject:
    subject_type: str
    composition: str
    primary: tuple[str, ...]
    merge_semantics: str | None = None
    authority: str | None = None


@dataclass(frozen=True)
class AuthorityMatrix:
    subjects: dict[str, AuthoritySubject]

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> AuthorityMatrix:
        subjects_raw = raw.get("subjects", {})
        if not isinstance(subjects_raw, dict):
            raise WorkflowError(
                "authority subjects must be a mapping",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="AUTHORITY_MATRIX_INVALID",
            )
        subjects: dict[str, AuthoritySubject] = {}
        for subject_type, value in subjects_raw.items():
            if not isinstance(value, dict):
                raise WorkflowError(
                    f"authority subject {subject_type} must be a mapping",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="AUTHORITY_MATRIX_INVALID",
                )
            composition = str(value.get("composition", ""))
            primary_raw = value.get("primary", [])
            if not isinstance(primary_raw, list):
                raise WorkflowError(
                    f"authority subject {subject_type} primary must be a list",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="AUTHORITY_MATRIX_INVALID",
                )
            primary = tuple(str(item) for item in primary_raw)
            if composition == "single":
                if len(primary) != 1:
                    raise WorkflowError(
                        f"authority subject {subject_type} must have exactly one primary",
                        exit_code=ExitCode.VALIDATION_FAILED,
                        code="AUTHORITY_PRIMARY_INVALID",
                    )
            elif composition == "composed":
                if not primary:
                    raise WorkflowError(
                        f"composed authority subject {subject_type} must have at least one authority",
                        exit_code=ExitCode.VALIDATION_FAILED,
                        code="AUTHORITY_COMPOSED_EMPTY",
                    )
                if not value.get("merge_semantics"):
                    raise WorkflowError(
                        f"composed authority subject {subject_type} requires merge semantics",
                        exit_code=ExitCode.VALIDATION_FAILED,
                        code="AUTHORITY_MERGE_SEMANTICS_MISSING",
                    )
            else:
                raise WorkflowError(
                    f"unknown authority composition: {composition}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="AUTHORITY_COMPOSITION_INVALID",
                )
            subject = AuthoritySubject(
                subject_type=str(subject_type),
                composition=composition,
                primary=primary,
                merge_semantics=(
                    None if value.get("merge_semantics") is None else str(value["merge_semantics"])
                ),
                authority=(None if value.get("authority") is None else str(value["authority"])),
            )
            if subject.authority == "advisory_only" and subject.primary:
                raise WorkflowError(
                    f"advisory-only subject {subject_type} cannot define normative primary authority",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="ADVISORY_AUTHORITY_LEAKAGE",
                )
            for path in subject.primary:
                cls._assert_normative_path(path)
            subjects[str(subject_type)] = subject
        return cls(subjects=subjects)

    @classmethod
    def load(cls, path: Path) -> AuthorityMatrix:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise WorkflowError(
                f"failed to load authority matrix {path}: {exc}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="AUTHORITY_MATRIX_INVALID",
            ) from exc
        if not isinstance(raw, dict):
            raise WorkflowError(
                "authority matrix must be a mapping",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="AUTHORITY_MATRIX_INVALID",
            )
        return cls.from_mapping(raw)

    @staticmethod
    def _assert_normative_path(path: str) -> None:
        normalized = path.replace("\\", "/")
        if (
            normalized.startswith("docs/audits/historical/")
            or "/docs/audits/historical/" in normalized
        ):
            raise WorkflowError(
                f"historical artifact cannot be normative: {path}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="HISTORICAL_AUTHORITY_FORBIDDEN",
            )

    def assert_normative(self, path: str) -> None:
        self._assert_normative_path(path)

    def primary_for(self, subject_type: str) -> tuple[str, ...]:
        try:
            subject = self.subjects[subject_type]
        except KeyError as exc:
            raise WorkflowError(
                f"unknown authority subject: {subject_type}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="AUTHORITY_SUBJECT_UNKNOWN",
            ) from exc
        return subject.primary

    def validate_claim(self, subject_type: str, path: str) -> None:
        self.assert_normative(path)
        if path not in self.primary_for(subject_type):
            raise WorkflowError(
                f"{path} is not authoritative for {subject_type}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="AUTHORITY_CLAIM_INVALID",
            )
