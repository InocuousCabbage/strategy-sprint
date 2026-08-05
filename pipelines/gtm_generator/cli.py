# -----------------------------------------------------------------------------
# CLI subprocess entry point for the vendored GTM plan generator.
#
# NOT vendored — this file is strategy-sprint's own wrapper around the
# vendored generator. Owned locally; edit here directly.
#
# Called from Exercise 7's SKILL.md as the final step:
#
#   python3 -m pipelines.gtm_generator.cli \
#     --artifact-dir <dir> \
#     --client-slug <slug> \
#     --strict
#
# Fail-loud-halt behavior per V1+grafts architecture:
#   exit 0  — success, gtm-plan.json written to <artifact-dir>/output/
#   exit 2  — contract violation (missing sidecar, schema-invalid, unsupported CRM, etc)
#   exit 3  — generator internal error (bug, not a contract issue)
#
# Structured error envelopes are written to stderr as single-line JSON so
# operators + downstream tooling can parse them without regex-scraping.
# -----------------------------------------------------------------------------

from __future__ import annotations

import argparse
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

EXIT_OK = 0
EXIT_CONTRACT_VIOLATION = 2
EXIT_GENERATOR_ERROR = 3


@dataclass
class ErrorEnvelope:
    """Single-line JSON error emitted to stderr on any non-zero exit.

    Shape is stable enough for downstream automation to parse; the message
    field carries the human-readable recovery hint. `kind` is one of:
      'contract_violation'  — bad or missing input; operator must fix input
      'generator_error'     — internal bug; operator should file an issue
      'invocation_error'    — bad CLI args; operator must correct invocation
    """

    kind: str
    exit_code: int
    message: str
    detail: dict | None = None

    def emit(self) -> None:
        payload = {"kind": self.kind, "exit_code": self.exit_code, "message": self.message}
        if self.detail is not None:
            payload["detail"] = self.detail
        print(json.dumps(payload), file=sys.stderr)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pipelines.gtm_generator.cli",
        description=(
            "Generate a GTM plan from strategy-sprint output. "
            "Halts loudly on any contract violation or generator error; "
            "never emits a partial plan."
        ),
    )
    parser.add_argument(
        "--artifact-dir",
        required=True,
        type=Path,
        help="Root artifact directory containing sprint exercise outputs + sidecars.",
    )
    parser.add_argument(
        "--client-slug",
        required=True,
        help="Client identifier used to key the output plan file (e.g. 'acme-corp').",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Reserved for future degrade-partial toggle. In V1 the generator is "
            "ALWAYS strict (fail-loud-halt architecture); this flag is accepted "
            "for forward-compat but has no non-strict alternative today."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parse_args(argv)
    except SystemExit as exc:
        # argparse exits with 2 on bad args; emit an envelope for the SystemExit
        # case so downstream automation sees a structured message rather than
        # bare argparse text on stderr.
        ErrorEnvelope(
            kind="invocation_error",
            exit_code=EXIT_CONTRACT_VIOLATION,
            message="Invalid CLI arguments; see argparse output above.",
        ).emit()
        return int(exc.code) if isinstance(exc.code, int) else EXIT_CONTRACT_VIOLATION

    artifact_dir: Path = args.artifact_dir
    if not artifact_dir.is_dir():
        ErrorEnvelope(
            kind="contract_violation",
            exit_code=EXIT_CONTRACT_VIOLATION,
            message=(
                f"--artifact-dir does not exist or is not a directory: {artifact_dir}. "
                f"Recover: pass an existing sprint-artifact directory."
            ),
            detail={"artifact_dir": str(artifact_dir)},
        ).emit()
        return EXIT_CONTRACT_VIOLATION

    # Deferred imports so a bad --artifact-dir fails fast before loading heavy
    # modules; also isolates any import-time error to the generator-error path.
    try:
        from pipelines.gtm_generator.input_models import validate_strategy_input
        from pipelines.gtm_generator.loader import load_from_artifact_dir
        from pipelines.gtm_generator.generator import GTMPlanGenerator
        from pipelines.gtm_generator.plan_writer import PlanWriter
    except ImportError as exc:
        ErrorEnvelope(
            kind="generator_error",
            exit_code=EXIT_GENERATOR_ERROR,
            message=(
                f"Failed to import vendored generator modules: {exc}. "
                f"Recover: verify pipelines/gtm_generator/ is present + re-run "
                f"scripts/sync-from-upstream.sh if you edited vendored files."
            ),
        ).emit()
        return EXIT_GENERATOR_ERROR

    # StrategySprintInput.from_artifact_dir binds against the JSON Schema
    # envelope at schema/strategy_sprint_input.schema.json. It fails with a
    # specific contract-violation shape when a sidecar is missing / envelope
    # header is malformed / payload doesn't match the (progressively-filled)
    # per-exercise schema. Kept behind the try/except so ALL contract failures
    # exit 2, regardless of which validator raised.
    try:
        sprint_input = load_from_artifact_dir(
            artifact_dir, client_slug=args.client_slug, strict=True
        )
        # validate_strategy_input returns a list[str] of errors (vendored
        # from the generator); empty means valid. cli.py earlier ignored
        # the return value which silently accepted invalid input — fixed
        # here to raise a ContractError-shaped exception when non-empty
        # so the same exit-code path handles semantic + envelope failures.
        semantic_errors = validate_strategy_input(sprint_input)
        if semantic_errors:
            from pipelines.gtm_generator.loader import ContractError

            raise ContractError(
                "Cross-section semantic validation failed: "
                + "; ".join(semantic_errors)
            )
    except Exception as exc:  # noqa: BLE001 — envelope classifies below
        # Distinguish contract-violation exceptions (raised by the loader on
        # any bad input) from internal errors (raised by anything else). The
        # loader raises ContractError subclasses for the former; anything else
        # falls to the generator-error bucket. This split is why the exit codes
        # matter: operator response differs (fix your input vs file a bug).
        from pipelines.gtm_generator.loader import ContractError

        if isinstance(exc, ContractError):
            ErrorEnvelope(
                kind="contract_violation",
                exit_code=EXIT_CONTRACT_VIOLATION,
                message=str(exc),
                detail={"exception_type": type(exc).__name__},
            ).emit()
            return EXIT_CONTRACT_VIOLATION

        ErrorEnvelope(
            kind="generator_error",
            exit_code=EXIT_GENERATOR_ERROR,
            message=(
                f"Unexpected input-load error: {type(exc).__name__}: {exc}. "
                f"Recover: file an issue with the traceback above; do not "
                f"work around by weakening validation."
            ),
            detail={"traceback": traceback.format_exc().splitlines()[-8:]},
        ).emit()
        return EXIT_GENERATOR_ERROR

    try:
        # Both of these calls were previously written against an API neither
        # class has: GTMPlanGenerator(sprint_input).generate(), and
        # PlanWriter(plan).write_json(path). Nothing ever reached this block,
        # because the contract check above always failed first, so the wrong
        # signatures sat here unexecuted. The generator's own docstring shows
        # the real shape.
        generator = GTMPlanGenerator()
        plan = generator.generate(sprint_input, client_id=args.client_slug)

        # PlanWriter is VENDORED and always writes to
        # {base}/.state/{client_id}/gtm-plan/plan.json. The documented contract,
        # in the Exercise 7 skill and the orchestrator's backstop check, is
        # output/gtm-plan.json inside the artifact dir. Serialising here rather
        # than editing PlanWriter, because a local edit to a vendored file is
        # reverted by the next sync without anyone noticing.
        #
        # NOT WIRED, flagged rather than silently dropped: PlanWriter.write()
        # also emits ten per-section JSON files and a human-readable PLAN.md.
        # Those may well be worth having; nothing consumes them today.
        output_path = artifact_dir / "output" / "gtm-plan.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(plan.to_dict(), indent=2, default=str))
    except Exception as exc:  # noqa: BLE001
        ErrorEnvelope(
            kind="generator_error",
            exit_code=EXIT_GENERATOR_ERROR,
            message=(
                f"Generator failed after input passed contract checks: "
                f"{type(exc).__name__}: {exc}. Recover: file an issue; input "
                f"is valid so this is an internal bug, not a data issue."
            ),
            detail={"traceback": traceback.format_exc().splitlines()[-8:]},
        ).emit()
        return EXIT_GENERATOR_ERROR

    print(f"OK: wrote {output_path}", file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
