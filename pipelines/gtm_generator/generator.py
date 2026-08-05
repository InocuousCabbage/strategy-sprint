# -----------------------------------------------------------------------------
# VENDORED code. Do NOT edit here; edit upstream and re-sync.
#
# Upstream: GTM plan generator (private repo, path-parameterised via
# UPSTREAM_GTM_GENERATOR_PATH env var; see VENDOR.md).
# Source SHA: ce73ca84f7462b2ca2d701e0c413dec62e94445f
# Sync procedure: scripts/sync-from-upstream.sh
#
# Any change made directly to this file will be overwritten on the next
# sync. If you need to change behavior, change the upstream file first,
# then re-run the sync script.
# -----------------------------------------------------------------------------

"""GTM Plan Generator — orchestrates all section builders to produce a complete plan.

This is the main entry point for generating a GTM plan from Strategy Sprint input.
It coordinates validation, section building, cross-section validation, and output.
"""

import hashlib
import json
from datetime import datetime, timezone

from pipelines.gtm_generator.input_models import StrategySprintInput, validate_strategy_input
from pipelines.gtm_generator.output_models import GTMPlan
from pipelines.gtm_generator.section_builders.icp_discovery import (
    build_icp_config,
    build_discovery_config,
)
from pipelines.gtm_generator.section_builders.outreach import build_outreach_config
from pipelines.gtm_generator.section_builders.post_demo_reengagement import (
    build_post_demo_config,
    build_reengagement_config,
)
from pipelines.gtm_generator.section_builders.calendly_crm import (
    build_calendly_config,
    build_crm_config,
)
from pipelines.gtm_generator.section_builders.content_retargeting_metrics import (
    build_content_calendar_config,
    build_retargeting_config,
    build_metrics_config,
)


class GTMPlanGenerator:
    """Orchestrates GTM plan generation from Strategy Sprint input.

    Coordinates input validation, 10 section builders, cross-section
    validation, and plan output. Designed to be deterministic —
    same input always produces the same output.

    Usage:
        generator = GTMPlanGenerator()
        plan = generator.generate(input_data, client_id="acme")
        # or from YAML:
        plan = generator.generate_from_yaml("path/to/sprint.yaml", client_id="acme")
    """

    VERSION = "1.0.0"

    def generate(
        self,
        input_data: StrategySprintInput,
        client_id: str = "",
    ) -> GTMPlan:
        """Generate a complete GTM plan from Strategy Sprint input.

        Args:
            input_data: Validated Strategy Sprint input.
            client_id: Optional client identifier. If empty, derived from company name.

        Returns:
            Complete GTMPlan instance with all 10 sections configured.

        Raises:
            ValueError: If input validation fails.
        """
        # Step 1: Validate input
        errors = validate_strategy_input(input_data)
        if errors:
            raise ValueError(
                f"Strategy Sprint input validation failed:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

        # Step 2: Derive client_id if not provided
        if not client_id:
            client_id = self._derive_client_id(input_data.company_name)

        # Step 3: Compute input hash for idempotency
        input_hash = self._compute_input_hash(input_data)

        # Step 4: Build all 10 sections
        icp = build_icp_config(input_data)
        discovery = build_discovery_config(input_data)
        outreach = build_outreach_config(input_data)
        post_demo = build_post_demo_config(input_data)
        reengagement = build_reengagement_config(input_data)
        calendly = build_calendly_config(input_data)
        crm = build_crm_config(input_data)
        content_calendar = build_content_calendar_config(input_data)
        retargeting = build_retargeting_config(input_data)
        metrics = build_metrics_config(input_data)

        # Step 5: Assemble the plan
        plan = GTMPlan(
            client_id=client_id,
            company_name=input_data.company_name,
            icp=icp,
            outreach_sequences=outreach,
            post_demo=post_demo,
            calendly=calendly,
            crm=crm,
            content_calendar=content_calendar,
            reengagement=reengagement,
            retargeting=retargeting,
            metrics=metrics,
            discovery=discovery,
            generated_at=datetime.now(timezone.utc).isoformat(),
            generator_version=self.VERSION,
            input_hash=input_hash,
        )

        return plan

    def generate_from_yaml(
        self,
        yaml_path: str,
        client_id: str = "",
    ) -> GTMPlan:
        """Generate a GTM plan from a YAML file.

        Convenience method that loads the YAML and calls generate().

        Args:
            yaml_path: Path to Strategy Sprint YAML file.
            client_id: Optional client identifier.

        Returns:
            Complete GTMPlan instance.

        Raises:
            FileNotFoundError: If the YAML file doesn't exist.
            ValueError: If YAML is invalid or input validation fails.
        """
        input_data = StrategySprintInput.from_yaml(yaml_path)
        return self.generate(input_data, client_id=client_id)

    def generate_from_yaml_string(
        self,
        yaml_string: str,
        client_id: str = "",
    ) -> GTMPlan:
        """Generate a GTM plan from a YAML string.

        Args:
            yaml_string: YAML content as string.
            client_id: Optional client identifier.

        Returns:
            Complete GTMPlan instance.
        """
        input_data = StrategySprintInput.from_yaml_string(yaml_string)
        return self.generate(input_data, client_id=client_id)

    # ========================================================================
    # Internal helpers
    # ========================================================================

    @staticmethod
    def _derive_client_id(company_name: str) -> str:
        """Derive a URL-safe client ID from company name.

        Args:
            company_name: The company name.

        Returns:
            Lowercase, underscore-separated client ID.
        """
        return (
            company_name.lower()
            .replace(" ", "_")
            .replace(".", "")
            .replace(",", "")
            .replace("'", "")
            .replace('"', "")
            .replace("-", "_")
        )

    @staticmethod
    def _compute_input_hash(input_data: StrategySprintInput) -> str:
        """Compute a deterministic hash of the input for idempotency.

        Args:
            input_data: Strategy Sprint input.

        Returns:
            SHA-256 hex digest (first 16 chars).
        """
        # Sort keys for deterministic JSON
        json_str = json.dumps(input_data.to_dict(), sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]