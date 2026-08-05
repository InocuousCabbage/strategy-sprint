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

"""Strategy Sprint input models and YAML schema validation.

Defines the StrategySprintInput dataclass that represents the
standardized output of a Strategy Sprint. Includes YAML parsing
and comprehensive schema validation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


# ============================================================================
# Sub-models for Strategy Sprint input
# ============================================================================


@dataclass
class TargetMarket:
    """Target market definition from Strategy Sprint."""

    industries: list[str] = field(default_factory=list)
    company_sizes: list[str] = field(default_factory=list)  # e.g. ["1-50", "51-200"]
    geographies: list[str] = field(default_factory=list)     # e.g. ["Northeast US"]
    annual_revenue_range: str = ""                           # e.g. "$1M-$10M"

    def to_dict(self) -> dict:
        return {
            "industries": self.industries,
            "company_sizes": self.company_sizes,
            "geographies": self.geographies,
            "annual_revenue_range": self.annual_revenue_range,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TargetMarket":
        return cls(
            industries=data.get("industries", []),
            company_sizes=data.get("company_sizes", []),
            geographies=data.get("geographies", []),
            annual_revenue_range=data.get("annual_revenue_range", ""),
        )


@dataclass
class ICPDefinition:
    """Ideal Customer Profile from Strategy Sprint."""

    criteria: list[str] = field(default_factory=list)     # Key qualification criteria
    titles: list[str] = field(default_factory=list)       # Target job titles
    signals: list[str] = field(default_factory=list)      # Buying signals to watch for
    disqualifiers: list[str] = field(default_factory=list)  # Reasons to exclude

    def to_dict(self) -> dict:
        return {
            "criteria": self.criteria,
            "titles": self.titles,
            "signals": self.signals,
            "disqualifiers": self.disqualifiers,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ICPDefinition":
        return cls(
            criteria=data.get("criteria", []),
            titles=data.get("titles", []),
            signals=data.get("signals", []),
            disqualifiers=data.get("disqualifiers", []),
        )


@dataclass
class ValueProposition:
    """Value proposition and positioning from Strategy Sprint."""

    headline: str = ""
    sub_points: list[str] = field(default_factory=list)
    differentiators: list[str] = field(default_factory=list)
    proof_points: list[str] = field(default_factory=list)   # Case studies, metrics, etc.

    def to_dict(self) -> dict:
        return {
            "headline": self.headline,
            "sub_points": self.sub_points,
            "differentiators": self.differentiators,
            "proof_points": self.proof_points,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ValueProposition":
        return cls(
            headline=data.get("headline", ""),
            sub_points=data.get("sub_points", []),
            differentiators=data.get("differentiators", []),
            proof_points=data.get("proof_points", []),
        )


@dataclass
class Competitor:
    """A competitor from the competitive landscape analysis."""

    name: str = ""
    weakness: str = ""
    positioning: str = ""  # How they position themselves

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "weakness": self.weakness,
            "positioning": self.positioning,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Competitor":
        return cls(
            name=data.get("name", ""),
            weakness=data.get("weakness", ""),
            positioning=data.get("positioning", ""),
        )


@dataclass
class PricingContext:
    """Pricing and packaging context from Strategy Sprint."""

    model: str = ""             # e.g. "subscription", "per-seat", "usage-based"
    range: str = ""             # e.g. "$99-$499/mo"
    positioning: str = ""       # e.g. "premium", "mid-market", "value"
    free_trial: bool = False

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "range": self.range,
            "positioning": self.positioning,
            "free_trial": self.free_trial,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PricingContext":
        return cls(
            model=data.get("model", ""),
            range=data.get("range", ""),
            positioning=data.get("positioning", ""),
            free_trial=data.get("free_trial", False),
        )


@dataclass
class BrandVoice:
    """Brand voice guidelines from Strategy Sprint."""

    tone: str = ""                                          # e.g. "direct, knowledgeable"
    banned_words: list[str] = field(default_factory=list)
    preferred_phrases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tone": self.tone,
            "banned_words": self.banned_words,
            "preferred_phrases": self.preferred_phrases,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BrandVoice":
        return cls(
            tone=data.get("tone", ""),
            banned_words=data.get("banned_words", []),
            preferred_phrases=data.get("preferred_phrases", []),
        )


@dataclass
class TechnologyFocus:
    """Technology stack targeting from Strategy Sprint."""

    platforms: list[str] = field(default_factory=list)          # Platforms to target/detect
    detection_patterns: list[str] = field(default_factory=list)  # URL/HTML patterns
    integrations: list[str] = field(default_factory=list)        # Key integrations

    def to_dict(self) -> dict:
        return {
            "platforms": self.platforms,
            "detection_patterns": self.detection_patterns,
            "integrations": self.integrations,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TechnologyFocus":
        return cls(
            platforms=data.get("platforms", []),
            detection_patterns=data.get("detection_patterns", []),
            integrations=data.get("integrations", []),
        )


# ============================================================================
# Main Strategy Sprint Input model
# ============================================================================


@dataclass
class StrategySprintInput:
    """Complete Strategy Sprint output as structured input for the GTM Generator.

    This is the standardized format that captures everything from a Strategy
    Sprint that the GTM Plan Generator needs to produce a complete plan.
    """

    # Core identification
    company_name: str = ""
    industry: str = ""
    website: str = ""

    # Strategy Sprint sections
    target_market: TargetMarket = field(default_factory=TargetMarket)
    icp: ICPDefinition = field(default_factory=ICPDefinition)
    value_proposition: ValueProposition = field(default_factory=ValueProposition)
    competitive_landscape: list[Competitor] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    pricing_context: PricingContext = field(default_factory=PricingContext)
    brand_voice: BrandVoice = field(default_factory=BrandVoice)
    technology_focus: TechnologyFocus = field(default_factory=TechnologyFocus)

    # Optional enrichment
    case_studies: list[dict] = field(default_factory=list)
    sales_cycle_days: int = 30  # Average sales cycle length

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "company_name": self.company_name,
            "industry": self.industry,
            "website": self.website,
            "target_market": self.target_market.to_dict(),
            "icp": self.icp.to_dict(),
            "value_proposition": self.value_proposition.to_dict(),
            "competitive_landscape": [c.to_dict() for c in self.competitive_landscape],
            "pain_points": self.pain_points,
            "pricing_context": self.pricing_context.to_dict(),
            "brand_voice": self.brand_voice.to_dict(),
            "technology_focus": self.technology_focus.to_dict(),
            "case_studies": self.case_studies,
            "sales_cycle_days": self.sales_cycle_days,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StrategySprintInput":
        """Deserialize from a dictionary."""
        return cls(
            company_name=data.get("company_name", ""),
            industry=data.get("industry", ""),
            website=data.get("website", ""),
            target_market=TargetMarket.from_dict(data.get("target_market", {})),
            icp=ICPDefinition.from_dict(data.get("icp", {})),
            value_proposition=ValueProposition.from_dict(data.get("value_proposition", {})),
            competitive_landscape=[
                Competitor.from_dict(c)
                for c in data.get("competitive_landscape", [])
            ],
            pain_points=data.get("pain_points", []),
            pricing_context=PricingContext.from_dict(data.get("pricing_context", {})),
            brand_voice=BrandVoice.from_dict(data.get("brand_voice", {})),
            technology_focus=TechnologyFocus.from_dict(data.get("technology_focus", {})),
            case_studies=data.get("case_studies", []),
            sales_cycle_days=data.get("sales_cycle_days", 30),
        )

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "StrategySprintInput":
        """Load and parse a Strategy Sprint YAML file.

        Args:
            yaml_path: Path to the YAML file.

        Returns:
            Parsed StrategySprintInput instance.

        Raises:
            FileNotFoundError: If the YAML file doesn't exist.
            yaml.YAMLError: If the file contains invalid YAML.
            ValueError: If required fields are missing.
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Strategy Sprint input not found: {yaml_path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Strategy Sprint input must be a YAML mapping, got {type(data).__name__}")

        return cls.from_dict(data)

    @classmethod
    def from_yaml_string(cls, yaml_string: str) -> "StrategySprintInput":
        """Parse a Strategy Sprint from a YAML string.

        Args:
            yaml_string: YAML content as a string.

        Returns:
            Parsed StrategySprintInput instance.

        Raises:
            yaml.YAMLError: If the string contains invalid YAML.
            ValueError: If required fields are missing.
        """
        data = yaml.safe_load(yaml_string)
        if not isinstance(data, dict):
            raise ValueError(f"Strategy Sprint input must be a YAML mapping, got {type(data).__name__}")
        return cls.from_dict(data)


# ============================================================================
# Input Schema Validation
# ============================================================================

# Required top-level fields
_REQUIRED_FIELDS = ["company_name", "industry", "target_market", "icp", "value_proposition", "pain_points"]

# Required sub-fields per section
_REQUIRED_SUB_FIELDS = {
    "target_market": ["industries"],
    "icp": ["criteria", "titles"],
    "value_proposition": ["headline"],
}


def validate_strategy_input(input_data: "StrategySprintInput") -> list[str]:
    """Validate a StrategySprintInput for completeness and correctness.

    Checks:
    - Required top-level fields are non-empty
    - Required sub-fields are present and non-empty
    - Lists have at least one item where required
    - Value types are correct

    Args:
        input_data: The input to validate.

    Returns:
        List of validation error strings. Empty list means valid.
    """
    errors = []

    # Check required top-level fields
    if not input_data.company_name.strip():
        errors.append("Missing required field: company_name")
    if not input_data.industry.strip():
        errors.append("Missing required field: industry")
    if not input_data.pain_points:
        errors.append("Missing required field: pain_points (must have at least 1)")

    # Check target_market
    if not input_data.target_market.industries:
        errors.append("target_market.industries must have at least 1 entry")

    # Check ICP
    if not input_data.icp.criteria:
        errors.append("icp.criteria must have at least 1 entry")
    if not input_data.icp.titles:
        errors.append("icp.titles must have at least 1 entry")

    # Check value proposition
    if not input_data.value_proposition.headline.strip():
        errors.append("value_proposition.headline is required")

    # Check sales_cycle_days is positive
    if input_data.sales_cycle_days <= 0:
        errors.append("sales_cycle_days must be positive")

    # Validate competitive_landscape entries if present
    for i, comp in enumerate(input_data.competitive_landscape):
        if not comp.name.strip():
            errors.append(f"competitive_landscape[{i}].name is required")

    return errors