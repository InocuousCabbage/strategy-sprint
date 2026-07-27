---
name: positioning
description: "Strategy Sprint Exercise 5: Positioning. Defines the company's positioning statement and competitive positioning map — who we're for, what we are, why they should care, and why they should believe us. Output is automatically saved to the /marketing-strategy skill."
metadata:
  version: 1.0.0
---

# Positioning Exercise

You are running the Positioning exercise — crystallizing how the company positions itself in the market.

## Why This Exercise Matters

Positioning is the strategic foundation of all marketing communication. It answers four deceptively simple questions that most companies struggle with:

1. **Who is it for?** (target audience)
2. **What is it?** (category/frame of reference)
3. **Why should they care?** (key benefit)
4. **Why should they believe us?** (proof/credibility)

Good positioning makes everything downstream easier — messaging, content, campaigns, sales conversations. Poor positioning leads to "we do everything for everyone" messaging that resonates with no one.

This exercise also maps positioning evolution: where you are today vs. where you want to be in 12 months.

## Prerequisites

- Read `${ARTIFACT_DIR}/output/marketing-strategy.md` — Company Overview, ICP Prioritization, Marketing Advantages, and Perceptions should ideally be completed
- Read `${ARTIFACT_DIR}/output/competitors.md` for competitive landscape

## Step 1: Research

1. **Review prior exercises:**
   - Company Overview: product, differentiators, metrics
   - ICP Prioritization: who are our priority audiences
   - Marketing Advantages: what can we credibly leverage
   - Perceptions: what storylines are we driving

2. **Competitive positioning analysis:**
   - How do top 3-5 competitors position themselves?
   - What categories do they claim?
   - Where are the positioning gaps?

3. **Current positioning audit:**
   - What does the homepage currently say?
   - How do sales describe the product?
   - How do customers describe it to others?

## Step 2: Conversational Discovery

### The Four Questions
1. "Who is your primary audience — if you could only talk to one type of buyer?" (maps to Q1)
2. "What category does your product fit in? Or are you creating a new one?" (maps to Q2)
3. "What's the single biggest benefit — the thing that makes someone say 'I need this'?" (maps to Q3)
4. "What proof do you have? Case studies, metrics, logos, awards?" (maps to Q4)

### Category Strategy
5. "Do you compete in an existing category, a subcategory, or are you creating something new?"
6. "If existing category: who's the leader and how do you differentiate?"
7. "If new category: what's the 'old way' you're replacing? What do you call the 'new way'?"

### Competitive Positioning
8. "On what spectrum do you differ most from competitors?" (e.g., simple vs. powerful, SMB vs. enterprise, horizontal vs. vertical)
9. "What do you do that competitors literally cannot do?"
10. "Where do you lose deals, and to whom? Why?"

### Positioning Evolution
11. "How would you describe your positioning today vs. where you want to be in 12 months?"
12. "Is there a positioning shift you're trying to make?" (e.g., moving upmarket, new category, new audience)

## Step 3: Document

Compile into this format:

```markdown
### Positioning Statement

**For** [target audience — specific role and company type]
**who** [key pain point or need],
**[Product Name] is a** [category]
**that** [key benefit/what it does].
**Unlike** [primary alternative],
**we** [key differentiator].

### The Four Questions Answered

| Question | Today | In 12 Months |
|----------|-------|-------------|
| **Who is it for?** | [Current primary audience] | [Aspirational audience, if different] |
| **What is it?** | [Current category/framing] | [Target category/framing] |
| **Why should they care?** | [Current key benefit] | [Evolved benefit as product matures] |
| **Why should they believe us?** | [Current proof points] | [Proof points we're building toward] |

### Category Strategy
- **Approach:** [Existing category / Subcategory / New category]
- **Category label:** [What we call ourselves]
- **The old way:** [What we replace / the status quo]
- **The new way:** [What we represent]

### Competitive Positioning Map

| Attribute Spectrum | Us | [Competitor 1] | [Competitor 2] | [Competitor 3] |
|-------------------|----|----|----|----|
| [e.g., Simple ↔ Powerful] | [position] | [position] | [position] | [position] |
| [e.g., SMB ↔ Enterprise] | [position] | [position] | [position] | [position] |
| [e.g., Point solution ↔ Platform] | [position] | [position] | [position] | [position] |

### Win/Loss Patterns
- **We win when:** [Conditions, audience types, use cases]
- **We lose when:** [Conditions, competitor strengths, gaps]
- **We lose to [Competitor]:** [Why and how to address]
```

## Step 4: Client Confirmation

Present the positioning work:
- "Does this positioning statement feel right? Would you change any element?"
- "Is the category strategy accurate — is that how you want to be framed?"
- "Do the competitive positioning spectrums capture the real differences?"
- "Are the win/loss patterns accurate?"

Make corrections based on feedback.

## Step 5: Save to Marketing Strategy

After client confirms, update `${ARTIFACT_DIR}/output/marketing-strategy.md`:
1. Find the `## Positioning` section
2. Replace everything from `*Not yet completed.*` through the `### What Goes Here` subsection with the confirmed output
3. Add `*Last updated: [today's date]*` at the top of the section

## Step 6: Enrich Context Files

Update these files:

1. **`${ARTIFACT_DIR}/output/competitors.md`** — Add competitive positioning map, win/loss patterns, category strategy

Only add/update information — never remove existing content.

## Related Exercises

- **Depends on:** `/company-overview`, `/icp-prioritization`, `/marketing-advantages`, `/perceptions`
- **Next:** `/revenue-levers` — given our position, where should we invest to grow?
- **Feeds into:** `/big-bets` — campaigns must reinforce our positioning
