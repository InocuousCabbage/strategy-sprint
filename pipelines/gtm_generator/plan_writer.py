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

"""Plan writer — writes GTM plans to disk as JSON files and markdown summary.

Outputs a complete client onboarding package to .state/{client_id}/gtm-plan/
containing individual section JSON files and a human-readable PLAN.md.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pipelines.gtm_generator.output_models import GTMPlan


class PlanWriter:
    """Writes GTM plans to the filesystem.

    Output structure:
        .state/{client_id}/gtm-plan/
            plan.json          # Full plan as single JSON
            icp.json           # Section 1: ICP Configuration
            outreach.json      # Section 2: Outreach Sequences
            post_demo.json     # Section 3: Post-Demo Config
            calendly.json      # Section 4: Calendly Config
            crm.json           # Section 5: CRM Config
            content.json       # Section 6: Content Calendar
            reengagement.json  # Section 7: Re-engagement
            retargeting.json   # Section 8: Retargeting
            metrics.json       # Section 9: Metrics
            discovery.json     # Section 10: Discovery
            PLAN.md            # Human-readable summary
    """

    # Map section names to output filenames
    _SECTION_FILES = {
        "icp": "icp.json",
        "outreach_sequences": "outreach.json",
        "post_demo": "post_demo.json",
        "calendly": "calendly.json",
        "crm": "crm.json",
        "content_calendar": "content.json",
        "reengagement": "reengagement.json",
        "retargeting": "retargeting.json",
        "metrics": "metrics.json",
        "discovery": "discovery.json",
    }

    def __init__(self, base_path: Optional[str] = None):
        """Initialize the plan writer.

        Args:
            base_path: Base directory for .state/ output. If None,
                uses the project root auto-detection.
        """
        if base_path:
            self._base = Path(base_path)
        else:
            self._base = self._find_project_root()

    def write(self, plan: GTMPlan) -> Path:
        """Write a complete GTM plan to disk.

        Creates the output directory and writes all files.

        Args:
            plan: The GTM plan to write.

        Returns:
            Path to the output directory.
        """
        output_dir = self._base / ".state" / plan.client_id / "gtm-plan"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write full plan JSON
        self._write_json(output_dir / "plan.json", plan.to_dict())

        # Write individual section files
        for section_name, filename in self._SECTION_FILES.items():
            section = plan.get_section(section_name)
            self._write_json(output_dir / filename, section.to_dict())

        # Write markdown summary
        markdown = self._generate_markdown(plan)
        (output_dir / "PLAN.md").write_text(markdown)

        return output_dir

    def write_plan_only(self, plan: GTMPlan) -> Path:
        """Write only the full plan.json (no individual sections or markdown).

        Useful for quick serialization without the full output structure.

        Args:
            plan: The GTM plan to write.

        Returns:
            Path to the plan.json file.
        """
        output_dir = self._base / ".state" / plan.client_id / "gtm-plan"
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "plan.json"
        self._write_json(path, plan.to_dict())
        return path

    # ========================================================================
    # Internal helpers
    # ========================================================================

    @staticmethod
    def _write_json(path: Path, data: dict) -> None:
        """Write a dictionary as formatted JSON to a file."""
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    @staticmethod
    def _find_project_root() -> Path:
        """Find the project root by walking up from this file."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / ".git").exists() or (current / "data").exists():
                return current
            current = current.parent
        return Path.cwd()

    @staticmethod
    def _generate_markdown(plan: GTMPlan) -> str:
        """Generate a human-readable markdown summary of the plan."""
        lines = []
        lines.append(f"# GTM Plan: {plan.company_name}")
        lines.append("")
        lines.append(f"**Client ID**: {plan.client_id}")
        lines.append(f"**Generated**: {plan.generated_at}")
        lines.append(f"**Generator Version**: {plan.generator_version}")
        lines.append(f"**Input Hash**: {plan.input_hash}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Section 1: ICP
        lines.append("## 1. ICP Configuration")
        icp = plan.icp
        industries = icp.apollo_filters.get("industries", [])
        lines.append(f"- **Target Industries**: {', '.join(industries)}")
        lines.append(f"- **Tech Detection Patterns**: {len(icp.tech_detection_patterns)} platforms")
        lines.append(f"- **Review Pain Categories**: {len(icp.review_pain_categories)}")
        lines.append(f"- **Min Qualification Score**: {icp.min_qualification_score}")
        lines.append("")

        # Section 2: Outreach
        lines.append("## 2. Outreach Sequences")
        outreach = plan.outreach_sequences
        lines.append(f"- **Email Templates**: {len(outreach.email_templates)}")
        lines.append(f"- **Phone Script**: {'Configured' if outreach.phone_script_template else 'Not configured'}")
        lines.append(f"- **Send Days**: {', '.join(outreach.send_days)}")
        lines.append(f"- **Send Window**: {outreach.send_window_start}:00-{outreach.send_window_end}:00")
        lines.append("")

        # Section 3: Post-Demo
        lines.append("## 3. Post-Demo Sequences")
        pd = plan.post_demo
        for outcome, seq in pd.sequences.items():
            lines.append(f"- **{outcome}**: {len(seq)} emails")
        lines.append(f"- **Talking Points**: {len(pd.demo_talking_points)}")
        lines.append("")

        # Section 4: Calendly
        lines.append("## 4. Calendly Configuration")
        cal = plan.calendly
        lines.append(f"- **Event**: {cal.event_type_name} ({cal.event_duration_minutes} min)")
        lines.append(f"- **UTM Campaign**: {cal.utm_campaign}")
        lines.append("")

        # Section 5: CRM
        lines.append("## 5. CRM Configuration")
        crm = plan.crm
        lines.append(f"- **Database Properties**: {len(crm.database_schema)}")
        lines.append(f"- **Activity Types**: {len(crm.activity_types)}")
        lines.append(f"- **Pipeline Stages**: {' -> '.join(crm.pipeline_stages)}")
        lines.append("")

        # Section 6: Content Calendar
        lines.append("## 6. Content Calendar")
        cc = plan.content_calendar
        lines.append(f"- **Posts/Week**: {cc.posts_per_week}")
        lines.append(f"- **Post Days**: {', '.join(cc.post_days)}")
        lines.append(f"- **Content Types**: {', '.join(cc.content_type_rotation)}")
        lines.append(f"- **Topic Themes**: {len(cc.topic_themes)}")
        lines.append("")

        # Section 7: Re-engagement
        lines.append("## 7. Re-engagement Triggers")
        re = plan.reengagement
        lines.append(f"- **Sales Cycle**: {re.sales_cycle_days} days")
        lines.append(f"- **Intervals**: {re.intervals}")
        lines.append(f"- **Adjusted for Sales Cycle**: {'Yes' if re.adjusted_intervals else 'No'}")
        lines.append("")

        # Section 8: Retargeting
        lines.append("## 8. Retargeting Setup")
        rt = plan.retargeting
        lines.append(f"- **Pixel Domain**: {rt.pixel_domain}")
        lines.append(f"- **Audiences**: {len(rt.audiences)}")
        lines.append(f"- **Campaign Templates**: {len(rt.campaign_templates)}")
        budget_total = sum(rt.daily_budget_cents.values()) if rt.daily_budget_cents else 0
        lines.append(f"- **Daily Budget**: ${budget_total / 100:.0f}/day")
        lines.append("")

        # Section 9: Metrics
        lines.append("## 9. Metrics & Dashboard")
        met = plan.metrics
        lines.append(f"- **KPIs**: {len(met.kpis)}")
        lines.append(f"- **Funnel Stages**: {' -> '.join(met.funnel_stages)}")
        lines.append(f"- **Alert Thresholds**: {len(met.alert_thresholds)}")
        lines.append("")

        # Section 10: Discovery
        lines.append("## 10. Discovery Configuration")
        disc = plan.discovery
        lines.append(f"- **Tech Fingerprints**: {len(disc.tech_fingerprints)}")
        lines.append(f"- **URL Scan Patterns**: {len(disc.url_scan_patterns)}")
        lines.append(f"- **Search Queries**: {len(disc.search_queries)}")
        lines.append(f"- **Geographic Filters**: {', '.join(disc.geographic_filters)}")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*This plan was generated automatically by the GTM Plan Generator.*")
        lines.append("*Review all sections before activation.*")
        lines.append("")

        return "\n".join(lines)