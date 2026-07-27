---
name: icp-prioritization
description: "Strategy Sprint Exercise 2: ICP Prioritization. Maps the total addressable market and prioritizes ideal customer profiles by tier (Core/Scaling/Testing). Output is automatically saved to the /marketing-strategy skill."
metadata:
  version: 1.0.0
---

# ICP Prioritization Exercise

You are running the ICP Prioritization exercise — the foundation for all audience-targeted marketing work.

## Why This Exercise Matters

Most companies try to market to everyone and end up resonating with no one. This exercise forces prioritization: which audience segments get the most resources, which are we testing, and which do we explicitly deprioritize. Every campaign, content piece, and channel decision flows from this.

The MKT1 framework uses four priority tiers:
- **Core** — proven segments getting the most resources
- **Scaling** — promising segments we're actively growing
- **Testing** — hypotheses we're validating with small bets
- **Not a Priority** — segments we explicitly choose not to pursue right now

## Prerequisites

- Read `${ARTIFACT_DIR}/output/marketing-strategy.md` — the Company Overview should be completed first
- Read `${ARTIFACT_DIR}/output/icp.md` for any existing ICP data

## Step 1: Research

1. **Review existing context:**
   - Company Overview from marketing-strategy (who they sell to currently)
   - Any existing ICP documentation in `${ARTIFACT_DIR}/output/icp.md`
   - CRM data or customer lists if available

2. **Research the market:**
   - Who uses similar products? (check competitor customer pages, case studies)
   - What industries/roles appear in reviews on G2/Capterra?
   - What segments does the company's content/marketing currently speak to?

3. **Map the TAM (Total Addressable Market):**
   - Identify company-type segments (by industry, size, stage, geography)
   - Identify role-based segments (who within those companies buys/uses)

## Step 2: Conversational Discovery

### TAM Mapping
1. "Let's map your total addressable market. What types of companies could use your product?" (by industry, size, stage)
2. "Within those companies, which roles are the buyers vs. the users?"
3. "Are there geographic or regulatory constraints that limit your market?"

### Current Customer Analysis
4. "Who are your best customers today — the ones that get the most value and are easiest to serve?"
5. "What patterns do you see? Are they in specific industries, company sizes, or roles?"
6. "Which customers churn fastest or get the least value? What do they have in common?"

### Prioritization
7. "Of all these segments, which 1-2 are your bread and butter — the ones you'd double down on?"
8. "Which segments are you actively trying to grow into?"
9. "Are there any segments you're curious about but haven't proven yet?"
10. "Which segments should we explicitly NOT pursue right now, and why?"

### Segment Deep-Dive (for each Core/Scaling segment)
11. "For [segment]: what's their biggest pain point that you solve?"
12. "What triggers them to look for a solution like yours?"
13. "What does their buying process look like? Who's involved?"
14. "Where do they hang out — what communities, publications, events?"
15. "How much are they willing to pay? What's their budget cycle?"

### Resource Allocation
16. "If you had to allocate 100% of marketing effort across these segments, how would you split it?"

## Step 3: Document

Compile into this format:

```markdown
### TAM Overview
[2-3 sentences describing the total addressable market]

### ICP Priority Matrix

| Priority | Resource Allocation | ICP - Role | ICP - Company Type | Maturity Level | Notes |
|----------|-------------------|------------|-------------------|---------------|-------|
| Core | [X]% | [Role] | [Company type] | [Proven/Growing/New] | [Key notes] |
| Core | [X]% | [Role] | [Company type] | [Proven/Growing/New] | [Key notes] |
| Scaling | [X]% | [Role] | [Company type] | [Proven/Growing/New] | [Key notes] |
| Testing | [X]% | [Role] | [Company type] | [Proven/Growing/New] | [Key notes] |
| Not a Priority | — | [Role] | [Company type] | — | [Why deprioritized] |

### Segment Deep-Dives

#### [Core Segment 1: Name]
- **Pain points:** [Top 3]
- **Purchase triggers:** [What makes them look for a solution]
- **Buying process:** [Who's involved, typical timeline]
- **Where they hang out:** [Communities, publications, events]
- **Budget/willingness to pay:** [Range and cycle]
- **Why they choose us:** [Key decision factors]

#### [Core Segment 2: Name]
[Same structure]

#### [Scaling Segment: Name]
[Same structure]

### Anti-ICP (Who We Don't Target)
- [Segment]: [Why — e.g., high churn, low LTV, product gap]
- [Segment]: [Why]
```

## Step 4: Client Confirmation

Present the ICP matrix and segment deep-dives:
- "Does this priority ranking feel right? Would you shift any tiers?"
- "Are the resource allocation percentages realistic?"
- "Anything missing from the segment deep-dives?"

Make corrections based on feedback.

## Step 5: Save to Marketing Strategy

After client confirms, update `${ARTIFACT_DIR}/output/marketing-strategy.md`:
1. Find the `## ICP Prioritization` section
2. Replace everything from `*Not yet completed.*` through the `### What Goes Here` subsection with the confirmed output
3. Add `*Last updated: [today's date]*` at the top of the section

## Step 6: Enrich Context Files

Update these files:

1. **`${ARTIFACT_DIR}/output/icp.md`** — Update with priority tiers, maturity levels, time allocation per segment, deep-dive details

Only add/update information — never remove existing content.

## Related Exercises

- **Depends on:** `/company-overview` (need to know the company before prioritizing audiences)
- **Next:** `/marketing-advantages` — what strengths can we leverage for these audiences?
- **Feeds into:** `/perceptions`, `/positioning`, `/revenue-levers`, `/big-bets` — all reference ICP priorities
