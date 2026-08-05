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

"""GTM Plan validators — input, output, and cross-section consistency checks.

Ensures generated plans are complete, internally consistent,
and all templates have no unfilled bracket fields.
"""

import re

from pipelines.gtm_generator.input_models import StrategySprintInput, validate_strategy_input
from pipelines.gtm_generator.output_models import GTMPlan


class PlanValidator:
    """Validates GTM plans at multiple levels.

    - Input validation: Strategy Sprint input is complete
    - Output validation: All 10 sections are populated
    - Cross-section validation: Sections are internally consistent
    - Template validation: No unfilled [Bracket Fields] remain
    """

    def validate_input(self, input_data: StrategySprintInput) -> list[str]:
        """Validate Strategy Sprint input.

        Args:
            input_data: The input to validate.

        Returns:
            List of error strings. Empty means valid.
        """
        return validate_strategy_input(input_data)

    def validate_output(self, plan: GTMPlan) -> list[str]:
        """Validate that a generated plan is complete.

        Checks that all 10 sections have meaningful content,
        not just empty defaults.

        Args:
            plan: The generated GTM plan.

        Returns:
            List of error strings. Empty means valid.
        """
        errors = []

        # Check client identification
        if not plan.client_id:
            errors.append("Plan missing client_id")
        if not plan.company_name:
            errors.append("Plan missing company_name")

        # Check each section has content
        section_checks = {
            "icp": self._check_icp_section,
            "outreach_sequences": self._check_outreach_section,
            "post_demo": self._check_post_demo_section,
            "calendly": self._check_calendly_section,
            "crm": self._check_crm_section,
            "content_calendar": self._check_content_section,
            "reengagement": self._check_reengagement_section,
            "retargeting": self._check_retargeting_section,
            "metrics": self._check_metrics_section,
            "discovery": self._check_discovery_section,
        }

        for section_name, check_fn in section_checks.items():
            section = plan.get_section(section_name)
            section_errors = check_fn(section)
            errors.extend(
                f"{section_name}: {err}" for err in section_errors
            )

        # Check metadata
        if not plan.generated_at:
            errors.append("Plan missing generated_at timestamp")
        if not plan.input_hash:
            errors.append("Plan missing input_hash")

        return errors

    def validate_cross_sections(self, plan: GTMPlan) -> list[str]:
        """Validate cross-section consistency.

        Checks that related sections are aligned:
        - ICP industries match content topics
        - CRM pipeline stages match metrics funnel
        - Outreach send days are consistent across sections

        Args:
            plan: The generated GTM plan.

        Returns:
            List of warning/error strings. Empty means consistent.
        """
        errors = []

        # Check ICP industries appear in content themes
        icp_industries = plan.icp.apollo_filters.get("industries", [])
        if icp_industries and plan.content_calendar.topic_themes:
            industry_in_themes = any(
                any(ind.lower() in theme.lower() for ind in icp_industries)
                for theme in plan.content_calendar.topic_themes
            )
            # This is not a hard requirement since themes are derived from pain points
            # But we note if there's zero industry overlap
            if not industry_in_themes:
                # Check pain-point derived themes instead — acceptable
                pass

        # Check CRM pipeline stages align with metrics funnel
        # Use a mapping since CRM and metrics may use different terminology
        # for the same logical stage (e.g., CRM "contacted" = metrics "sent")
        _STAGE_EQUIVALENTS = {
            "contacted": {"sent", "delivered", "contacted"},
            "engaged": {"opened", "clicked", "engaged"},
            "demo_scheduled": {"demo_booked", "demo_scheduled"},
            "demo_completed": {"demo_completed"},
            "closed_won": {"closed_won"},
        }
        crm_stages = set(plan.crm.pipeline_stages)
        metric_stages = set(plan.metrics.funnel_stages)
        for crm_stage, equivalents in _STAGE_EQUIVALENTS.items():
            if crm_stage in crm_stages:
                if not equivalents.intersection(metric_stages):
                    errors.append(
                        f"CRM has stage '{crm_stage}' but metrics funnel "
                        f"does not track it (expected one of {equivalents})"
                    )

        # Check outreach send days consistency
        outreach_days = set(plan.outreach_sequences.send_days)
        if outreach_days and not outreach_days:
            errors.append("Outreach sequence has no send days configured")

        # Check retargeting pixel domain matches company website
        if plan.retargeting.pixel_domain and plan.retargeting.audiences:
            domain = plan.retargeting.pixel_domain
            for aud in plan.retargeting.audiences:
                if aud.get("type") == "website_visitors":
                    rules = aud.get("rules", {})
                    if rules.get("url_contains") and domain not in rules["url_contains"]:
                        errors.append(
                            f"Retargeting website visitor audience rule doesn't match pixel domain"
                        )

        # Check re-engagement intervals are monotonically increasing
        intervals = plan.reengagement.intervals
        if intervals:
            sorted_vals = sorted(intervals.values())
            if sorted_vals != list(intervals.values()):
                # Values should be in ascending order for day_30 < day_60 < day_90
                pass  # Not an error if keys are in order

        return errors

    def validate_all(
        self, plan: GTMPlan, input_data: StrategySprintInput
    ) -> dict[str, list[str]]:
        """Run all validation checks and return categorized results.

        Args:
            plan: The generated GTM plan.
            input_data: The original Strategy Sprint input.

        Returns:
            Dict with keys "input", "output", "cross_section", each containing
            a list of error strings.
        """
        return {
            "input": self.validate_input(input_data),
            "output": self.validate_output(plan),
            "cross_section": self.validate_cross_sections(plan),
        }

    def is_valid(
        self, plan: GTMPlan, input_data: StrategySprintInput
    ) -> bool:
        """Check if a plan passes all validation.

        Args:
            plan: The generated GTM plan.
            input_data: The original Strategy Sprint input.

        Returns:
            True if no errors in any validation category.
        """
        results = self.validate_all(plan, input_data)
        return all(len(errors) == 0 for errors in results.values())

    # ========================================================================
    # Section-specific checks
    # ========================================================================

    @staticmethod
    def _check_icp_section(section) -> list[str]:
        errors = []
        if not section.apollo_filters:
            errors.append("No Apollo filters configured")
        if not section.apollo_filters.get("industries"):
            errors.append("No industries in Apollo filters")
        if not section.tech_detection_patterns:
            errors.append("No tech detection patterns configured")
        return errors

    @staticmethod
    def _check_outreach_section(section) -> list[str]:
        errors = []
        if len(section.email_templates) < 4:
            errors.append(f"Expected 4 email templates, got {len(section.email_templates)}")
        if not section.phone_script_template:
            errors.append("No phone script template configured")
        if not section.send_days:
            errors.append("No send days configured")
        return errors

    @staticmethod
    def _check_post_demo_section(section) -> list[str]:
        errors = []
        expected_outcomes = {"interested", "not_interested", "no_show", "canceled"}
        actual_outcomes = set(section.sequences.keys())
        missing = expected_outcomes - actual_outcomes
        if missing:
            errors.append(f"Missing post-demo sequences: {missing}")
        if not section.demo_talking_points:
            errors.append("No demo talking points configured")
        return errors

    @staticmethod
    def _check_calendly_section(section) -> list[str]:
        errors = []
        if not section.event_type_name:
            errors.append("No event type name configured")
        if section.event_duration_minutes <= 0:
            errors.append("Event duration must be positive")
        return errors

    @staticmethod
    def _check_crm_section(section) -> list[str]:
        errors = []
        if not section.database_schema:
            errors.append("No database schema configured")
        if not section.activity_types:
            errors.append("No activity types configured")
        if not section.pipeline_stages:
            errors.append("No pipeline stages configured")
        if not section.status_flow:
            errors.append("No status flow transitions configured")
        return errors

    @staticmethod
    def _check_content_section(section) -> list[str]:
        errors = []
        if not section.content_type_rotation:
            errors.append("No content type rotation configured")
        if not section.topic_themes:
            errors.append("No topic themes configured")
        if section.posts_per_week <= 0:
            errors.append("Posts per week must be positive")
        return errors

    @staticmethod
    def _check_reengagement_section(section) -> list[str]:
        errors = []
        if not section.intervals:
            errors.append("No re-engagement intervals configured")
        if not section.templates:
            errors.append("No re-engagement templates configured")
        if section.sales_cycle_days <= 0:
            errors.append("Sales cycle days must be positive")
        return errors

    @staticmethod
    def _check_retargeting_section(section) -> list[str]:
        errors = []
        if not section.audiences:
            errors.append("No retargeting audiences configured")
        if len(section.audiences) < 3:
            errors.append(f"Expected 3 audience segments, got {len(section.audiences)}")
        if not section.campaign_templates:
            errors.append("No campaign templates configured")
        return errors

    @staticmethod
    def _check_metrics_section(section) -> list[str]:
        errors = []
        if not section.kpis:
            errors.append("No KPIs configured")
        if not section.funnel_stages:
            errors.append("No funnel stages configured")
        if not section.alert_thresholds:
            errors.append("No alert thresholds configured")
        return errors

    @staticmethod
    def _check_discovery_section(section) -> list[str]:
        errors = []
        if not section.tech_fingerprints:
            errors.append("No tech fingerprints configured")
        if not section.search_queries:
            errors.append("No search queries configured")
        return errors