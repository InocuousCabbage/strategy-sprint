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

"""GTM Plan output models — 10 configuration sections plus the GTMPlan wrapper.

Each section corresponds to a group of features from Sprints 1-5.
All models follow the project pattern: dataclasses with to_dict()/from_dict().
"""

from dataclasses import dataclass, field
from typing import Optional


# ============================================================================
# Section 1: ICP Configuration (F1, F2, F3, F4, F5)
# ============================================================================


@dataclass
class ICPConfig:
    """ICP configuration for prospect identification and qualification.

    Configures Apollo search filters, tech detection patterns,
    and review scraper pain signal categories.
    """

    # Apollo search filters (F4)
    apollo_filters: dict = field(default_factory=dict)
    # e.g. {"industries": [...], "employee_count": "1-50", "technologies": [...]}

    # Technology detection patterns (F1)
    tech_detection_patterns: list[dict] = field(default_factory=list)
    # e.g. [{"platform": "Buildium", "url_patterns": [...], "html_signatures": [...]}]

    # Review scraper pain categories (F5)
    review_pain_categories: list[str] = field(default_factory=list)
    # e.g. ["maintenance delays", "communication issues", "billing problems"]

    # CSV import column mappings (F2)
    csv_column_mappings: dict = field(default_factory=dict)

    # Qualification criteria
    min_qualification_score: int = 60
    qualification_weights: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "apollo_filters": self.apollo_filters,
            "tech_detection_patterns": self.tech_detection_patterns,
            "review_pain_categories": self.review_pain_categories,
            "csv_column_mappings": self.csv_column_mappings,
            "min_qualification_score": self.min_qualification_score,
            "qualification_weights": self.qualification_weights,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ICPConfig":
        return cls(
            apollo_filters=data.get("apollo_filters", {}),
            tech_detection_patterns=data.get("tech_detection_patterns", []),
            review_pain_categories=data.get("review_pain_categories", []),
            csv_column_mappings=data.get("csv_column_mappings", {}),
            min_qualification_score=data.get("min_qualification_score", 60),
            qualification_weights=data.get("qualification_weights", {}),
        )


# ============================================================================
# Section 2: Outreach Sequence Configuration (F6, F15)
# ============================================================================


@dataclass
class OutreachSequenceConfig:
    """Outreach sequence configuration — email templates + phone scripts.

    Configures the 4-email + phone call cadence with client-specific
    bracket field values pre-filled.
    """

    # Email sequence templates with bracket fields filled
    email_templates: list[dict] = field(default_factory=list)
    # Each: {"position": "email_1", "subject": "...", "body": "...", "day_offset": 0}

    # Phone script template
    phone_script_template: dict = field(default_factory=dict)
    # {"opening": "...", "hook": "...", "bridge": "...", "ask": "...", "voicemail": "..."}

    # Cadence settings
    cadence_day_offsets: dict = field(default_factory=dict)
    send_days: list[str] = field(default_factory=lambda: ["tuesday", "wednesday", "thursday"])
    send_window_start: int = 9
    send_window_end: int = 11

    # Personalization field defaults
    default_field_values: dict = field(default_factory=dict)
    # e.g. {"Sender Name": "Alex", "Company Benefit": "reduce maintenance response time by 40%"}

    def to_dict(self) -> dict:
        return {
            "email_templates": self.email_templates,
            "phone_script_template": self.phone_script_template,
            "cadence_day_offsets": self.cadence_day_offsets,
            "send_days": self.send_days,
            "send_window_start": self.send_window_start,
            "send_window_end": self.send_window_end,
            "default_field_values": self.default_field_values,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OutreachSequenceConfig":
        return cls(
            email_templates=data.get("email_templates", []),
            phone_script_template=data.get("phone_script_template", {}),
            cadence_day_offsets=data.get("cadence_day_offsets", {}),
            send_days=data.get("send_days", ["tuesday", "wednesday", "thursday"]),
            send_window_start=data.get("send_window_start", 9),
            send_window_end=data.get("send_window_end", 11),
            default_field_values=data.get("default_field_values", {}),
        )


# ============================================================================
# Section 3: Post-Demo Configuration (F11)
# ============================================================================


@dataclass
class PostDemoConfig:
    """Post-demo follow-up sequence configuration.

    Configures 4 outcome-based follow-up sequences with client context.
    """

    # Sequence templates per demo outcome
    sequences: dict = field(default_factory=dict)
    # {"interested": [{"position": 1, "subject": "...", "body": "..."}], ...}

    # Day offsets per outcome
    day_offsets: dict = field(default_factory=dict)
    # {"interested": [1, 3, 7], "not_interested": [3, 14, 30], ...}

    # Client-specific context for personalization
    demo_talking_points: list[str] = field(default_factory=list)
    case_study_references: list[dict] = field(default_factory=list)
    proposal_template_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "sequences": self.sequences,
            "day_offsets": self.day_offsets,
            "demo_talking_points": self.demo_talking_points,
            "case_study_references": self.case_study_references,
            "proposal_template_notes": self.proposal_template_notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PostDemoConfig":
        return cls(
            sequences=data.get("sequences", {}),
            day_offsets=data.get("day_offsets", {}),
            demo_talking_points=data.get("demo_talking_points", []),
            case_study_references=data.get("case_study_references", []),
            proposal_template_notes=data.get("proposal_template_notes", ""),
        )


# ============================================================================
# Section 4: Calendly Configuration (F8)
# ============================================================================


@dataclass
class CalendlyConfig:
    """Calendly scheduling configuration.

    Configures scheduling link templates with client branding and UTM setup.
    """

    # Scheduling link configuration
    event_type_name: str = ""          # e.g. "15-Minute Strategy Call"
    event_duration_minutes: int = 15
    booking_url_template: str = ""     # e.g. "https://calendly.com/{slug}"

    # Branding
    confirmation_message: str = ""
    reminder_message: str = ""

    # UTM parameters for tracking
    utm_source: str = "cold_outreach"
    utm_medium: str = "email"
    utm_campaign: str = ""

    # Webhook configuration
    webhook_events: list[str] = field(default_factory=lambda: [
        "invitee.created", "invitee.canceled",
    ])

    def to_dict(self) -> dict:
        return {
            "event_type_name": self.event_type_name,
            "event_duration_minutes": self.event_duration_minutes,
            "booking_url_template": self.booking_url_template,
            "confirmation_message": self.confirmation_message,
            "reminder_message": self.reminder_message,
            "utm_source": self.utm_source,
            "utm_medium": self.utm_medium,
            "utm_campaign": self.utm_campaign,
            "webhook_events": self.webhook_events,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CalendlyConfig":
        return cls(
            event_type_name=data.get("event_type_name", ""),
            event_duration_minutes=data.get("event_duration_minutes", 15),
            booking_url_template=data.get("booking_url_template", ""),
            confirmation_message=data.get("confirmation_message", ""),
            reminder_message=data.get("reminder_message", ""),
            utm_source=data.get("utm_source", "cold_outreach"),
            utm_medium=data.get("utm_medium", "email"),
            utm_campaign=data.get("utm_campaign", ""),
            webhook_events=data.get("webhook_events", [
                "invitee.created", "invitee.canceled",
            ]),
        )


# ============================================================================
# Section 5: CRM Configuration (F10)
# ============================================================================


@dataclass
class CRMConfig:
    """CRM and activity tracking configuration.

    Configures Notion database schema, activity types, and status transitions.
    """

    # Notion database configuration
    database_schema: dict = field(default_factory=dict)
    # Property definitions for the CRM database

    # Activity types to track
    activity_types: list[str] = field(default_factory=list)
    # e.g. ["email_sent", "email_opened", "demo_completed", "follow_up_sent"]

    # Status transitions
    status_flow: list[dict] = field(default_factory=list)
    # [{"from": "scraped", "to": "enriched", "trigger": "enrichment_complete"}, ...]

    # Pipeline stages
    pipeline_stages: list[str] = field(default_factory=list)
    # e.g. ["prospect", "contacted", "engaged", "demo_scheduled", "proposal", "closed"]

    # Custom properties per client
    custom_properties: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "database_schema": self.database_schema,
            "activity_types": self.activity_types,
            "status_flow": self.status_flow,
            "pipeline_stages": self.pipeline_stages,
            "custom_properties": self.custom_properties,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CRMConfig":
        return cls(
            database_schema=data.get("database_schema", {}),
            activity_types=data.get("activity_types", []),
            status_flow=data.get("status_flow", []),
            pipeline_stages=data.get("pipeline_stages", []),
            custom_properties=data.get("custom_properties", {}),
        )


# ============================================================================
# Section 6: Content Calendar Configuration (F13)
# ============================================================================


@dataclass
class ContentCalendarConfig:
    """LinkedIn content calendar configuration.

    Configures posting schedule and content templates for practitioner positioning.
    """

    # Posting schedule
    post_days: list[str] = field(default_factory=lambda: ["monday", "wednesday", "friday"])
    posts_per_week: int = 3

    # Content type rotation
    content_type_rotation: list[str] = field(default_factory=list)
    # e.g. ["insight_post", "case_study_summary", "industry_commentary"]

    # Topic themes derived from value prop and pain points
    topic_themes: list[str] = field(default_factory=list)

    # Hashtag strategy
    default_hashtags: list[str] = field(default_factory=list)
    industry_hashtags: list[str] = field(default_factory=list)

    # Content templates with client context filled
    content_templates: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "post_days": self.post_days,
            "posts_per_week": self.posts_per_week,
            "content_type_rotation": self.content_type_rotation,
            "topic_themes": self.topic_themes,
            "default_hashtags": self.default_hashtags,
            "industry_hashtags": self.industry_hashtags,
            "content_templates": self.content_templates,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentCalendarConfig":
        return cls(
            post_days=data.get("post_days", ["monday", "wednesday", "friday"]),
            posts_per_week=data.get("posts_per_week", 3),
            content_type_rotation=data.get("content_type_rotation", []),
            topic_themes=data.get("topic_themes", []),
            default_hashtags=data.get("default_hashtags", []),
            industry_hashtags=data.get("industry_hashtags", []),
            content_templates=data.get("content_templates", []),
        )


# ============================================================================
# Section 7: Re-engagement Configuration (F12)
# ============================================================================


@dataclass
class ReengagementConfig:
    """Re-engagement trigger configuration.

    Configures trigger intervals and templates customized for client sales cycle.
    """

    # Trigger intervals (days of inactivity)
    intervals: dict = field(default_factory=lambda: {
        "day_30": 30, "day_60": 60, "day_90": 90,
    })

    # Template customizations per interval
    templates: dict = field(default_factory=dict)
    # {"day_30": {"subject": "...", "approach": "value-add"}, ...}

    # Sales cycle awareness
    sales_cycle_days: int = 30
    adjusted_intervals: bool = False  # Whether intervals were adjusted for sales cycle

    # Eligible statuses for re-engagement scanning
    eligible_statuses: list[str] = field(default_factory=lambda: [
        "sent", "no_response", "engaged",
    ])

    def to_dict(self) -> dict:
        return {
            "intervals": self.intervals,
            "templates": self.templates,
            "sales_cycle_days": self.sales_cycle_days,
            "adjusted_intervals": self.adjusted_intervals,
            "eligible_statuses": self.eligible_statuses,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReengagementConfig":
        return cls(
            intervals=data.get("intervals", {"day_30": 30, "day_60": 60, "day_90": 90}),
            templates=data.get("templates", {}),
            sales_cycle_days=data.get("sales_cycle_days", 30),
            adjusted_intervals=data.get("adjusted_intervals", False),
            eligible_statuses=data.get("eligible_statuses", ["sent", "no_response", "engaged"]),
        )


# ============================================================================
# Section 8: Retargeting Configuration (F16)
# ============================================================================


@dataclass
class RetargetingConfig:
    """Retargeting campaign configuration.

    Configures Meta pixel, audience definitions, and campaign templates.
    """

    # Pixel configuration
    pixel_id: str = ""
    pixel_events: list[str] = field(default_factory=lambda: [
        "PageView", "ViewContent", "Lead", "Schedule",
    ])
    pixel_domain: str = ""

    # Audience definitions
    audiences: list[dict] = field(default_factory=list)
    # [{"name": "...", "type": "website_visitors", "retention_days": 180, "rules": {...}}, ...]

    # Campaign templates
    campaign_templates: list[dict] = field(default_factory=list)

    # Budget recommendations
    daily_budget_cents: dict = field(default_factory=dict)
    # {"website_visitors": 1000, "email_engagers": 1500, "demo_bookers": 2000}

    # Setup instructions
    setup_instructions: str = ""

    def to_dict(self) -> dict:
        return {
            "pixel_id": self.pixel_id,
            "pixel_events": self.pixel_events,
            "pixel_domain": self.pixel_domain,
            "audiences": self.audiences,
            "campaign_templates": self.campaign_templates,
            "daily_budget_cents": self.daily_budget_cents,
            "setup_instructions": self.setup_instructions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RetargetingConfig":
        return cls(
            pixel_id=data.get("pixel_id", ""),
            pixel_events=data.get("pixel_events", [
                "PageView", "ViewContent", "Lead", "Schedule",
            ]),
            pixel_domain=data.get("pixel_domain", ""),
            audiences=data.get("audiences", []),
            campaign_templates=data.get("campaign_templates", []),
            daily_budget_cents=data.get("daily_budget_cents", {}),
            setup_instructions=data.get("setup_instructions", ""),
        )


# ============================================================================
# Section 9: Metrics Configuration (F9, F14)
# ============================================================================


@dataclass
class MetricsConfig:
    """Outreach metrics and dashboard configuration.

    Configures dashboard filters and KPIs relevant to client funnel.
    """

    # KPIs to track
    kpis: list[dict] = field(default_factory=list)
    # [{"name": "open_rate", "target": 0.3, "unit": "percent"}, ...]

    # Funnel stages for metrics aggregation
    funnel_stages: list[str] = field(default_factory=list)
    # e.g. ["sent", "opened", "clicked", "replied", "demo_booked", "closed"]

    # Dashboard filters
    dashboard_filters: dict = field(default_factory=dict)
    # {"date_range": "last_30_days", "segment_by": "industry"}

    # Engagement webhook events to track
    webhook_events: list[str] = field(default_factory=lambda: [
        "delivered", "opened", "clicked", "replied", "bounced",
    ])

    # Alert thresholds
    alert_thresholds: dict = field(default_factory=dict)
    # {"bounce_rate_max": 0.05, "open_rate_min": 0.2}

    def to_dict(self) -> dict:
        return {
            "kpis": self.kpis,
            "funnel_stages": self.funnel_stages,
            "dashboard_filters": self.dashboard_filters,
            "webhook_events": self.webhook_events,
            "alert_thresholds": self.alert_thresholds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MetricsConfig":
        return cls(
            kpis=data.get("kpis", []),
            funnel_stages=data.get("funnel_stages", []),
            dashboard_filters=data.get("dashboard_filters", {}),
            webhook_events=data.get("webhook_events", [
                "delivered", "opened", "clicked", "replied", "bounced",
            ]),
            alert_thresholds=data.get("alert_thresholds", {}),
        )


# ============================================================================
# Section 10: Discovery Configuration (F1, F3)
# ============================================================================


@dataclass
class DiscoveryConfig:
    """Prospect discovery configuration.

    Configures technology detection patterns and URL pattern sets
    for finding new prospects.
    """

    # Technology fingerprints to detect (F1)
    tech_fingerprints: list[dict] = field(default_factory=list)
    # [{"name": "Buildium", "url_patterns": [...], "html_signatures": [...], "weight": 1.0}, ...]

    # URL patterns for tenant portal discovery (F3)
    url_scan_patterns: list[dict] = field(default_factory=list)
    # [{"pattern": "*.buildiumresident.com", "platform": "Buildium"}, ...]

    # Search queries for finding prospects
    search_queries: list[str] = field(default_factory=list)

    # Geographic targeting
    geographic_filters: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tech_fingerprints": self.tech_fingerprints,
            "url_scan_patterns": self.url_scan_patterns,
            "search_queries": self.search_queries,
            "geographic_filters": self.geographic_filters,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DiscoveryConfig":
        return cls(
            tech_fingerprints=data.get("tech_fingerprints", []),
            url_scan_patterns=data.get("url_scan_patterns", []),
            search_queries=data.get("search_queries", []),
            geographic_filters=data.get("geographic_filters", []),
        )


# ============================================================================
# GTM Plan wrapper — the top-level container
# ============================================================================


@dataclass
class GTMPlan:
    """Complete GTM Plan containing all 10 configuration sections.

    This is the top-level output of the GTM Plan Generator. It bundles
    all section configurations into a single deliverable that can be
    written to disk as JSON files and a markdown summary.
    """

    # Client identification
    client_id: str = ""
    company_name: str = ""

    # 10 configuration sections
    icp: ICPConfig = field(default_factory=ICPConfig)
    outreach_sequences: OutreachSequenceConfig = field(default_factory=OutreachSequenceConfig)
    post_demo: PostDemoConfig = field(default_factory=PostDemoConfig)
    calendly: CalendlyConfig = field(default_factory=CalendlyConfig)
    crm: CRMConfig = field(default_factory=CRMConfig)
    content_calendar: ContentCalendarConfig = field(default_factory=ContentCalendarConfig)
    reengagement: ReengagementConfig = field(default_factory=ReengagementConfig)
    retargeting: RetargetingConfig = field(default_factory=RetargetingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    discovery: DiscoveryConfig = field(default_factory=DiscoveryConfig)

    # Metadata
    generated_at: str = ""
    generator_version: str = "1.0.0"
    input_hash: str = ""  # For idempotency verification

    def to_dict(self) -> dict:
        """Serialize the entire plan to a JSON-compatible dictionary."""
        return {
            "client_id": self.client_id,
            "company_name": self.company_name,
            "icp": self.icp.to_dict(),
            "outreach_sequences": self.outreach_sequences.to_dict(),
            "post_demo": self.post_demo.to_dict(),
            "calendly": self.calendly.to_dict(),
            "crm": self.crm.to_dict(),
            "content_calendar": self.content_calendar.to_dict(),
            "reengagement": self.reengagement.to_dict(),
            "retargeting": self.retargeting.to_dict(),
            "metrics": self.metrics.to_dict(),
            "discovery": self.discovery.to_dict(),
            "generated_at": self.generated_at,
            "generator_version": self.generator_version,
            "input_hash": self.input_hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GTMPlan":
        """Deserialize from a dictionary."""
        return cls(
            client_id=data.get("client_id", ""),
            company_name=data.get("company_name", ""),
            icp=ICPConfig.from_dict(data.get("icp", {})),
            outreach_sequences=OutreachSequenceConfig.from_dict(
                data.get("outreach_sequences", {})
            ),
            post_demo=PostDemoConfig.from_dict(data.get("post_demo", {})),
            calendly=CalendlyConfig.from_dict(data.get("calendly", {})),
            crm=CRMConfig.from_dict(data.get("crm", {})),
            content_calendar=ContentCalendarConfig.from_dict(
                data.get("content_calendar", {})
            ),
            reengagement=ReengagementConfig.from_dict(data.get("reengagement", {})),
            retargeting=RetargetingConfig.from_dict(data.get("retargeting", {})),
            metrics=MetricsConfig.from_dict(data.get("metrics", {})),
            discovery=DiscoveryConfig.from_dict(data.get("discovery", {})),
            generated_at=data.get("generated_at", ""),
            generator_version=data.get("generator_version", "1.0.0"),
            input_hash=data.get("input_hash", ""),
        )

    @property
    def section_names(self) -> list[str]:
        """Return the names of all 10 configuration sections."""
        return [
            "icp",
            "outreach_sequences",
            "post_demo",
            "calendly",
            "crm",
            "content_calendar",
            "reengagement",
            "retargeting",
            "metrics",
            "discovery",
        ]

    def get_section(self, name: str):
        """Get a section by name.

        Args:
            name: Section name (must be one of section_names).

        Returns:
            The section dataclass instance.

        Raises:
            ValueError: If name is not a valid section.
        """
        if name not in self.section_names:
            raise ValueError(f"Unknown section: {name}. Valid: {self.section_names}")
        return getattr(self, name)

    def sections_dict(self) -> dict[str, dict]:
        """Return all sections as a dict of section_name -> section.to_dict()."""
        return {name: self.get_section(name).to_dict() for name in self.section_names}
