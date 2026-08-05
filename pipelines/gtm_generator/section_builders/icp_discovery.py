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

"""Section builders for ICP Configuration and Discovery Configuration.

Maps Strategy Sprint input to F1 (Platform Detection), F2 (CSV Adapter),
F3 (URL Pattern Scraper), F4 (Apollo Enrichment), and F5 (Reviews Scraper).
"""

from pipelines.gtm_generator.input_models import StrategySprintInput
from pipelines.gtm_generator.output_models import ICPConfig, DiscoveryConfig


def build_icp_config(input_data: StrategySprintInput) -> ICPConfig:
    """Build ICP configuration from Strategy Sprint input.

    Generates Apollo search filters, tech detection patterns,
    review scraper categories, and qualification criteria.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured ICPConfig instance.
    """
    # Build Apollo search filters from target market and ICP
    apollo_filters = {
        "industries": input_data.target_market.industries,
        "employee_counts": input_data.target_market.company_sizes,
        "locations": input_data.target_market.geographies,
        "job_titles": input_data.icp.titles,
    }

    # Add technology filters if platforms are specified
    if input_data.technology_focus.platforms:
        apollo_filters["technologies"] = input_data.technology_focus.platforms

    # Build tech detection patterns from technology focus
    tech_detection_patterns = []
    for platform in input_data.technology_focus.platforms:
        pattern = {
            "platform": platform,
            "url_patterns": [
                p for p in input_data.technology_focus.detection_patterns
                if platform.lower().replace(" ", "") in p.lower().replace(" ", "")
            ],
            "html_signatures": [],
            "weight": 1.0,
        }
        tech_detection_patterns.append(pattern)

    # Build review pain categories from pain points
    review_pain_categories = [
        _pain_to_review_category(pain) for pain in input_data.pain_points
    ]

    # CSV column mappings (standard defaults)
    csv_column_mappings = {
        "company_name": "Company",
        "website": "Website",
        "industry": "Industry",
        "employee_count": "Employees",
        "technology": "Technology",
    }

    # Qualification weights based on ICP criteria count
    qualification_weights = {}
    for i, criterion in enumerate(input_data.icp.criteria):
        key = f"criterion_{i + 1}"
        qualification_weights[key] = {
            "description": criterion,
            "weight": round(100 / len(input_data.icp.criteria)),
        }

    return ICPConfig(
        apollo_filters=apollo_filters,
        tech_detection_patterns=tech_detection_patterns,
        review_pain_categories=review_pain_categories,
        csv_column_mappings=csv_column_mappings,
        min_qualification_score=60,
        qualification_weights=qualification_weights,
    )


def build_discovery_config(input_data: StrategySprintInput) -> DiscoveryConfig:
    """Build Discovery configuration from Strategy Sprint input.

    Generates technology fingerprints, URL scan patterns,
    search queries, and geographic filters.

    Args:
        input_data: Validated Strategy Sprint input.

    Returns:
        Configured DiscoveryConfig instance.
    """
    # Build technology fingerprints
    tech_fingerprints = []
    for platform in input_data.technology_focus.platforms:
        fingerprint = {
            "name": platform,
            "url_patterns": [
                p for p in input_data.technology_focus.detection_patterns
                if platform.lower().replace(" ", "") in p.lower().replace(" ", "")
            ],
            "html_signatures": [
                f'<meta name="generator" content="{platform}"',
                f"powered by {platform}",
            ],
            "weight": 1.0,
        }
        tech_fingerprints.append(fingerprint)

    # Build URL scan patterns
    url_scan_patterns = [
        {"pattern": pattern, "platform": _detect_platform_from_pattern(
            pattern, input_data.technology_focus.platforms
        )}
        for pattern in input_data.technology_focus.detection_patterns
    ]

    # Build search queries from ICP and target market
    search_queries = []
    for industry in input_data.target_market.industries:
        for geo in input_data.target_market.geographies:
            search_queries.append(f"{industry} companies {geo}")
    # Add pain-point-driven queries
    for pain in input_data.pain_points[:3]:  # Top 3 pain points
        search_queries.append(
            f"{input_data.target_market.industries[0]} {_pain_to_search_query(pain)}"
        )

    # Geographic filters
    geographic_filters = list(input_data.target_market.geographies)

    return DiscoveryConfig(
        tech_fingerprints=tech_fingerprints,
        url_scan_patterns=url_scan_patterns,
        search_queries=search_queries,
        geographic_filters=geographic_filters,
    )


# ============================================================================
# Helper functions
# ============================================================================


def _pain_to_review_category(pain_point: str) -> str:
    """Convert a pain point description to a review scraper category.

    Extracts the core topic from a pain point for use as a review
    search/filter category.

    Args:
        pain_point: A pain point description string.

    Returns:
        A short category string suitable for review scraping.
    """
    # Extract key noun phrases — simplified approach
    keywords = {
        "maintenance": "maintenance issues",
        "response time": "slow response",
        "communication": "communication problems",
        "turnover": "tenant turnover",
        "cost": "cost complaints",
        "emergency": "emergency repairs",
        "vendor": "vendor coordination",
        "billing": "billing issues",
        "visibility": "lack of visibility",
        "manual": "manual processes",
    }
    pain_lower = pain_point.lower()
    for keyword, category in keywords.items():
        if keyword in pain_lower:
            return category
    # Fallback: use the first 5 words
    words = pain_point.split()[:5]
    return " ".join(words).rstrip(".,;:")


def _detect_platform_from_pattern(
    pattern: str, platforms: list[str]
) -> str:
    """Detect which platform a URL pattern belongs to.

    Args:
        pattern: URL pattern string.
        platforms: List of known platform names.

    Returns:
        Matched platform name, or "unknown".
    """
    pattern_lower = pattern.lower().replace(" ", "")
    for platform in platforms:
        if platform.lower().replace(" ", "") in pattern_lower:
            return platform
    return "unknown"


def _pain_to_search_query(pain_point: str) -> str:
    """Convert a pain point to a search query fragment.

    Args:
        pain_point: A pain point description.

    Returns:
        A search query fragment.
    """
    # Take the core of the pain point, removing common filler
    words = pain_point.lower().split()
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "to", "for", "of", "in", "on", "at"}
    filtered = [w for w in words if w not in stop_words]
    return " ".join(filtered[:6])