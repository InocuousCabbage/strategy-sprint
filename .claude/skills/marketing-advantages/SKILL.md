---
name: marketing-advantages
description: "Strategy Sprint Exercise 3: Marketing Advantages. Identifies and prioritizes the company's unfair marketing advantages across product-led growth, brand, content, sales, and market position categories. Output is automatically saved to the /marketing-strategy skill."
metadata:
  version: 1.0.0
---

# Marketing Advantages Exercise

You are running the Marketing Advantages exercise — identifying where the company has unfair advantages that marketing can accelerate.

## Why This Exercise Matters

Companies grow faster when they play to their strengths rather than copying competitors' playbooks. A company with strong network effects should invest differently than one with a powerful founder brand. This exercise identifies which advantages exist (or could be developed) and creates a plan to accelerate each through marketing.

The MKT1 framework identifies advantages across these categories:
- **Product-led growth:** Network effects, virality, free tools, self-serve
- **Brand & community:** Founder brand, community, word of mouth, thought leadership
- **Content & SEO:** Expertise content, SEO moat, proprietary data/research
- **Sales & partnerships:** Channel partners, integrations, ecosystem
- **Market position:** First mover, category creation, platform status

## Prerequisites

- Read `${ARTIFACT_DIR}/output/marketing-strategy.md` — Company Overview and ICP Prioritization should be completed
- These prior exercises provide the context needed to assess advantages accurately

## Step 1: Research

1. **Review prior exercises:**
   - Company Overview: what differentiators were identified?
   - ICP Prioritization: what do customers value most?

2. **Analyze current marketing:**
   - What channels/tactics are currently working best?
   - Where does organic growth come from?
   - What content performs best?

3. **Check for advantage signals:**
   - Product virality (do users invite others? share outputs?)
   - Community presence (active Slack/Discord? user-generated content?)
   - SEO position (ranking for key terms?)
   - Founder/team visibility (speaking, writing, social following?)
   - Integration ecosystem (marketplace, API, partner network?)

## Step 2: Conversational Discovery

Walk through each advantage category:

### Product-Led Growth
1. "Does your product naturally get shared or seen by others? How?" (virality, network effects)
2. "Do you have a free tier, free tool, or self-serve motion that drives awareness?"
3. "What percentage of new customers come from product-led sources vs. sales-led?"

### Brand & Community
4. "Does anyone on your team have a personal brand or following? Who, and where?"
5. "Do you have an active community? (Slack, Discord, forum, user group)"
6. "How much word-of-mouth or referral business do you get?"

### Content & SEO
7. "Do you have expertise or proprietary data that competitors don't?"
8. "What's your current SEO situation? Any strong rankings?"
9. "What content has resonated most with your audience?"

### Sales & Partnerships
10. "Do you have channel partners, integrations, or an ecosystem play?"
11. "What's your relationship like with adjacent tools in your customer's stack?"

### Market Position
12. "Are you a first mover, category creator, or fast follower in your space?"
13. "Do you have any structural advantage — regulation, data, patents, switching costs?"

### Strength Assessment
14. "Of everything we discussed, which 3-5 advantages feel strongest to you right now?"
15. "Which advantages are emerging — not strong yet, but you could develop them?"
16. "Which advantages do your competitors have that you don't?"

## Step 3: Document

Compile into this format:

```markdown
### Marketing Advantages Assessment

| Advantage | Category | Strength | Competitive Differentiation | Marketing Strategy to Accelerate | Priority |
|-----------|----------|----------|---------------------------|--------------------------------|----------|
| [e.g., Founder brand on LinkedIn] | Brand & Community | Strong | Unique | Double down on LinkedIn content, speaking, podcast appearances | High |
| [e.g., Free tool drives signups] | Product-Led Growth | Moderate | Shared | Optimize free tool SEO, add viral sharing features | High |
| [e.g., Integration ecosystem] | Sales & Partnerships | Emerging | Unique | Build integration marketplace, co-marketing with partners | Medium |

**Strength ratings:** Strong / Moderate / Emerging / Weak
**Competitive differentiation:** Unique (only us) / Shared (us + few others) / Table Stakes (everyone has it)

### Top 3 Advantages to Accelerate

1. **[Advantage 1]:** [Why it's #1, specific marketing actions to take]
2. **[Advantage 2]:** [Why it's #2, specific marketing actions to take]
3. **[Advantage 3]:** [Why it's #3, specific marketing actions to take]

### Advantages to Develop (6-12 Month Horizon)
- [Advantage]: [What needs to happen to strengthen it]

### Competitive Advantage Gaps
- [Competitor advantage we lack]: [Whether to address or accept]
```

## Step 4: Client Confirmation

Present the advantages assessment:
- "Does this capture your real advantages? Anything over- or under-rated?"
- "Do the top 3 priorities feel right?"
- "Any advantages I missed that you think could be significant?"

Make corrections based on feedback.

## Step 5: Save to Marketing Strategy

After client confirms, update `${ARTIFACT_DIR}/output/marketing-strategy.md`:
1. Find the `## Marketing Advantages` section
2. Replace everything from `*Not yet completed.*` through the `### What Goes Here` subsection with the confirmed output
3. Add `*Last updated: [today's date]*` at the top of the section

## Step 6: Enrich Context Files

No specific context files to enrich for this exercise. The output lives in marketing-strategy.

## Related Exercises

- **Depends on:** `/company-overview`, `/icp-prioritization`
- **Next:** `/perceptions` — what stories should we tell, given our advantages?
- **Feeds into:** `/big-bets` — campaigns should leverage our strongest advantages
