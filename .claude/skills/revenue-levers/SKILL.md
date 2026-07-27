---
name: revenue-levers
description: "Strategy Sprint Exercise 6: Revenue Levers. Stack-ranks the four revenue levers (expand top-of-funnel core, expand top-of-funnel new, improve efficiency, increase customer value) to focus marketing investment. Output is automatically saved to the /marketing-strategy skill."
metadata:
  version: 1.0.0
---

# Revenue Levers Exercise

You are running the Revenue Levers exercise — determining where marketing investment will have the highest impact on revenue.

## Why This Exercise Matters

There are only four ways marketing can impact revenue:

1. **Increase top of funnel — core segments/market** (get more of the people we already know how to reach)
2. **Increase top of funnel — new segments/market** (expand into new audiences)
3. **Improve efficiency — increase conversion or reduce CAC** (get more from existing traffic/pipeline)
4. **Increase value of each customer — expand revenue, reduce churn** (grow what we have)

Most companies spread effort across all four and make marginal progress on everything. This exercise forces a stack rank: what's #1, what's #2, and what gets deprioritized.

The answer depends on company stage, current metrics, competitive position, and strategic goals — which is why this exercise comes after the foundational work.

## Prerequisites

- Read `${ARTIFACT_DIR}/output/marketing-strategy.md` — all prior exercises provide context for this decision
- Key inputs: company metrics (CAC, LTV, churn, conversion rates), ICP priorities, competitive position

## Step 1: Research

1. **Review prior exercises:**
   - Company Overview: current metrics, stage, growth rate
   - ICP Prioritization: which segments are proven vs. testing
   - Marketing Advantages: what channels/tactics have the most leverage
   - Positioning: competitive dynamics and market position

2. **Analyze current funnel:**
   - Where are the biggest drop-offs?
   - What's the current conversion rate at each stage?
   - Where is there the most room for improvement?

3. **Benchmark assessment:**
   - Is CAC reasonable for the business model?
   - Is churn/retention healthy?
   - Is top-of-funnel sufficient or constrained?

## Step 2: Conversational Discovery

### Current State
1. "Where does most of your revenue come from today — new customer acquisition or existing customer expansion?"
2. "What does your funnel look like? Roughly: visitors → leads → MQLs → SQLs → customers?"
3. "Where do you feel the biggest bottleneck is?"

### Lever-by-Lever Assessment
4. "If we doubled your top-of-funnel traffic from existing segments, do you have the sales capacity and product to handle it?"
5. "Are there new segments or markets you believe could be big but haven't invested in yet?"
6. "How healthy is your conversion rate? Do you feel you're leaving money on the table in the funnel?"
7. "What about existing customers — is there expansion/upsell opportunity? How's churn?"

### Prioritization
8. "Given everything we've discussed, which lever do you think would have the biggest revenue impact in the next 6 months?"
9. "And after that — what's #2?"
10. "What's something you're currently investing in that might be lower priority than we think?"

### Lever-by-ICP
11. "Do different ICPs have different lever priorities? For example, is the core segment about efficiency while the scaling segment needs top-of-funnel?"

## Step 3: Document

Compile into this format:

```markdown
### Revenue Levers — Stack Ranked

| Rank | Lever | Rationale | Time Allocation |
|------|-------|-----------|----------------|
| #1 | [Lever name] | [Why this is #1 for this company right now] | [X]% |
| #2 | [Lever name] | [Why this is #2] | [X]% |
| #3 | [Lever name] | [Why this is #3] | [X]% |
| #4 | [Lever name] | [Why this is deprioritized] | [X]% |

### Lever Details

#### #1: [Lever Name]
- **Current state:** [Where things stand — metrics if available]
- **Opportunity:** [Why there's room to improve]
- **Key strategies:**
  - [Strategy 1]
  - [Strategy 2]
  - [Strategy 3]
- **Expected impact:** [What success looks like]

#### #2: [Lever Name]
[Same structure]

#### #3: [Lever Name]
[Same structure]

#### #4: [Lever Name]
- **Why deprioritized:** [Specific reason — not that it doesn't matter, but other levers have higher ROI right now]
- **Revisit when:** [Conditions that would change the priority]

### Revenue Levers by ICP

| ICP Segment | Primary Lever | Secondary Lever | Notes |
|-------------|--------------|-----------------|-------|
| [Core segment 1] | [Lever] | [Lever] | [Why] |
| [Core segment 2] | [Lever] | [Lever] | [Why] |
| [Scaling segment] | [Lever] | [Lever] | [Why] |
```

## Step 4: Client Confirmation

Present the lever ranking:
- "Does this ranking feel right? Would you reorder anything?"
- "Are the time allocation percentages realistic?"
- "Do the lever-by-ICP priorities make sense?"
- "Any strategies listed that feel off or missing?"

Make corrections based on feedback.

## Step 5: Save to Marketing Strategy

After client confirms, update `${ARTIFACT_DIR}/output/marketing-strategy.md`:
1. Find the `## Revenue Levers` section
2. Replace everything from `*Not yet completed.*` through the `### What Goes Here` subsection with the confirmed output
3. Add `*Last updated: [today's date]*` at the top of the section

## Step 6: Enrich Context Files

Update these files:

1. **`${ARTIFACT_DIR}/input/client-brief.md`** — Enrich the goals section with revenue lever priorities and time allocation guidance

Only add/update information — never remove existing content.

## Related Exercises

- **Depends on:** All prior exercises (company overview, ICP, advantages, perceptions, positioning)
- **Next:** `/big-bets` — which campaigns will we run to activate our top levers?
- **Key input for:** All campaign planning, budget allocation, and resource decisions
