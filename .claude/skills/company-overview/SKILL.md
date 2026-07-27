---
name: company-overview
description: "Strategy Sprint Exercise 1: Company Overview. Gathers comprehensive company context — product, business model, metrics, differentiators. Output is automatically saved to the /marketing-strategy skill."
metadata:
  version: 1.0.0
---

# Company Overview Exercise

You are running the Company Overview exercise — the first step of the Strategy Sprint. This builds the foundational context that every other exercise depends on.

## Why This Exercise Matters

Every marketing decision depends on deeply understanding the company — not just what it does, but how it makes money, who it serves, what stage it's at, and what makes it different. Without this foundation, positioning is guesswork and campaigns miss the mark.

## Prerequisites

- Read `${ARTIFACT_DIR}/output/marketing-strategy.md` for any existing context from prior exercises
- This is typically the first exercise — no prior exercises required

## Step 1: Research

Before asking questions, gather what you can:

1. **Check existing context files:**
   - Read `${ARTIFACT_DIR}/input/client-brief.md` for any client info already captured
   - Read `${ARTIFACT_DIR}/output/product.md` for product details
   - Read `.agents/product-marketing-context.md` if it exists

2. **Research the company online:**
   - Visit the company website (homepage, about, pricing, product pages)
   - Check for recent press, blog posts, or announcements
   - Look at G2/Capterra/TrustRadius for positioning signals
   - Check LinkedIn company page for team size and growth signals

3. **Synthesize what you found** — present it to the client and note gaps

## Step 2: Conversational Discovery

Ask these questions in order. Skip any already answered by research:

### Company Basics
1. "What's the one-line description of what your company does?"
2. "When was the company founded? What stage are you at?" (pre-seed, seed, Series A/B/C, bootstrapped, profitable)
3. "How many people on the team? Key departments?"

### Product & Business Model
4. "Walk me through what the product/service actually does — the core use case"
5. "What's the business model?" (SaaS, marketplace, services, hybrid)
6. "What's the pricing structure?" (free tier, trial, pricing tiers, enterprise)
7. "What's the primary value metric?" (per seat, per usage, flat rate)

### Metrics & Traction
8. "Can you share current metrics?" (ARR/MRR, customer count, growth rate, NRR)
9. "What's the current CAC and LTV if you know them?"
10. "What's your current MQL/SQL/opportunity pipeline look like?"

### Differentiation & Momentum
11. "What do customers say is the #1 reason they chose you over alternatives?"
12. "What's happened in the last 6 months that you're most proud of?" (launches, wins, milestones)
13. "What's the biggest challenge or constraint right now?"

### Market Context
14. "How would you describe the market you're in? Growing, mature, emerging?"
15. "Who are the 3-5 companies prospects most often compare you to?"

## Step 3: Document

Compile everything into this format:

```markdown
### Company Snapshot
| Field | Details |
|-------|---------|
| Company | [Name] |
| URL | [website] |
| Founded | [year] |
| Stage | [funding stage] |
| Team Size | [number] |
| Business Model | [type] |
| Pricing | [structure summary] |

### Product Overview
[2-3 paragraph description of what the product does, core use cases, and how it works]

### Key Metrics
| Metric | Value |
|--------|-------|
| ARR/MRR | [value] |
| Customers | [count] |
| Growth Rate | [%] |
| NRR | [%] |
| CAC | [value] |
| LTV | [value] |

### Key Differentiators
1. [Differentiator 1 — with evidence]
2. [Differentiator 2 — with evidence]
3. [Differentiator 3 — with evidence]

### Recent Momentum
- [Milestone 1]
- [Milestone 2]
- [Milestone 3]

### Current Challenges
- [Challenge 1]
- [Challenge 2]

### Competitive Landscape (High-Level)
| Competitor | How They Differ |
|-----------|----------------|
| [Name] | [Key difference] |
| [Name] | [Key difference] |
| [Name] | [Key difference] |
```

## Step 4: Client Confirmation

Present the compiled overview and ask:
- "Does this accurately capture your company? Anything I got wrong?"
- "Anything important I missed?"
- "Any metrics you'd like to add or correct?"

Make corrections based on feedback.

## Step 5: Save to Marketing Strategy

After client confirms, update `${ARTIFACT_DIR}/output/marketing-strategy.md`:
1. Find the `## Company Overview` section
2. Replace everything from `*Not yet completed.*` through the `### What Goes Here` subsection with the confirmed output
3. Add `*Last updated: [today's date]*` at the top of the section

## Step 6: Enrich Context Files

Update these files with relevant information from the exercise:

1. **`${ARTIFACT_DIR}/output/product.md`** — Update with deeper product details, metrics, and business model info
2. **`${ARTIFACT_DIR}/input/client-brief.md`** — Enrich the business context section with research findings and metrics

Only add/update information — never remove existing content from these files.

## Related Exercises

- **Next:** `/icp-prioritization` — now that we know the company, who should we target?
- **Feeds into:** All subsequent exercises use company overview as context
