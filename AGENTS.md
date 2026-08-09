## Imported Claude Cowork project instructions

# TRANSFER PRICING INTELLIGENCE PLATFORM (TPIP)
## Project Instructions v1.0
## Professional Portfolio Product Architecture

---

# 1. PROJECT VISION

## What is TPIP?

TPIP (Transfer Pricing Intelligence Platform) is a professional-grade software tool designed to demonstrate how international tax expertise can be transformed into an AI-assisted professional application.

The objective is to build a platform that helps transfer pricing professionals:

- Analyze whether a transfer price is defensible under the arm's length principle
- Compare transactions against benchmark data
- Estimate tax impact across jurisdictions
- Generate professional analysis reports
- Improve research and decision-making processes

The project combines:

- International taxation knowledge
- Transfer pricing methodology
- Software engineering
- Artificial intelligence
- Product thinking

---

# 2. PORTFOLIO OBJECTIVE

This project is not only a software application.

It is designed to demonstrate:

1. Deep understanding of international tax and transfer pricing
2. Ability to transform professional problems into software solutions
3. Ability to build AI-assisted professional tools
4. Understanding of how tax technology products are designed
5. Long-term product vision beyond academic projects

The priority is:

1. Build something functional
2. Make it impressive in a professional demonstration
3. Ensure technical quality
4. Expand progressively

Do not optimize for enterprise complexity before creating a working MVP.

---

# 3. CORE PRINCIPLES

## 3.1 Tax logic is the source of truth

TPIP is NOT a chatbot.

It is a reasoning and calculation engine.

The architecture must separate:

- Tax/business logic
- API layer
- User interface
- AI assistance

The system must always follow:

Tax logic → Result → AI explanation

Never:

AI → Tax conclusion

---

## 3.2 AI GOVERNANCE

AI assists but never replaces professional tax judgement.

AI can:

✓ Explain calculated results
✓ Generate plain-language summaries
✓ Format reports
✓ Help users understand concepts
✓ Summarize documents

AI cannot:

✗ Create transfer prices
✗ Decide whether a transaction is arm's length
✗ Select comparables autonomously
✗ Interpret new tax regulations as legal advice
✗ Replace professional review

Every AI-generated explanation must be based on existing system outputs.

---

# 4. DEVELOPMENT PHILOSOPHY

## Demo First Principle

Every development phase must create something demonstrable.

A completed feature must:

- Work correctly
- Be understandable in a 5-minute demo
- Produce professional-looking output
- Have documentation

The project should always move toward a better demonstration.

---

## Before implementing features

Always explain:

1. What problem this solves
2. Why it belongs in the current phase
3. Architectural impact
4. Demo/interview value
5. Future scalability implications

Then implement.

---

# 5. PROJECT ROADMAP

## Phase 1 — MVP (Month 1)

Goal:

Create a working Transfer Pricing Analyzer.

Scope:

Input:

Example:

Spain → Luxembourg

Transaction:

Royalty payment

Amount:

€1,000,000

Rate:

12%

Industry:

Technology

Output:

- Benchmark range
- Arm's length assessment
- Risk classification
- Explanation
- Professional PDF report


The MVP must prove:

"A transfer pricing analyst can use this tool to quickly evaluate a transaction."

---

## Phase 2 — Tax Impact Modeler

Add:

- Multi-country tax calculations
- Withholding taxes
- Effective tax rate analysis
- Scenario comparison

Example:

"What happens if the royalty changes from 12% to 8%?"

---

## Phase 3 — Research Companion

Add:

- Document ingestion
- Semantic search
- OECD guideline search
- Research assistant capabilities

The research assistant supports the analyst but does not replace professional judgement.

---

# 6. ARCHITECTURE PRINCIPLES

Use modular architecture.

Recommended structure:


tpip/

├── tp_domain/
│ ├── models/
│ ├── calculations/
│ ├── validators/
│ └── comparables/

├── api/
│ ├── routes/
│ └── schemas/

├── frontend/
│ ├── components/
│ └── pages/

├── ai/
│ ├── prompts/
│ ├── synthesis/
│ └── validation/

├── database/

├── tests/

└── documentation/


---

# 7. DOMAIN LAYER RULES

All transfer pricing logic belongs in:


tp_domain/


Examples:

Correct:


tp_domain/calculations/
calculate_arm_length_range()

calculate_defensibility_score()

calculate_tax_impact()

Incorrect:

React component calculating tax.

API endpoint calculating transfer price.

AI deciding risk score.

---

# 8. INITIAL DATA STRATEGY

For MVP:

Realistic synthetic data is acceptable.

Requirements:

- Numbers must reflect realistic transfer pricing ranges
- Assumptions must be documented
- Data structure must allow replacement with real datasets later

Initial database:

Approximately:

- 50-100 comparable examples
- Several industries:
    - Software
    - Pharma
    - Manufacturing
    - Services

---

# 9. BENCHMARKING LOGIC

The system should:

1. Identify transaction type
2. Identify appropriate TP method
3. Find comparable transactions
4. Calculate statistical range:

- Percentile 25
- Median
- Percentile 75

5. Compare proposed rate
6. Generate risk classification


Example:

Royalty proposed:

12%

Benchmark:

5%-8%

Result:

"Outside typical range. Additional documentation recommended."

---

# 10. AI IMPLEMENTATION RULES

AI prompts must be:

- Stored separately
- Version controlled
- Documented

Example:


ai/prompts/

explain_analysis_v1.md

generate_report_v1.md


AI receives:

- Calculated result
- Benchmark information
- Sources

AI does not create calculations.

---

# 11. TESTING PRINCIPLES

Every important calculation requires tests.

Priority:

1. Domain logic tests
2. Integration tests
3. End-to-end demo tests


Examples:

Test:

Given:

Comparable rates:

5%, 6%, 8%, 10%

Expected:

Median:

7%

---

# 12. TECHNOLOGY STACK

Initial recommendation:

Backend:

- Python
- FastAPI

Frontend:

- React
- TypeScript
- Tailwind

Database:

- SQLite initially

AI:

- Claude API

Reports:

- PDF generation

Deployment:

- Simple cloud deployment

Avoid unnecessary complexity during MVP.

---

# 13. LONG TERM VISION

After MVP:

Possible evolution:

- More TP methods
- More jurisdictions
- Automated documentation
- Regulatory monitoring
- Knowledge graph
- SaaS capabilities
- Integration with professional workflows


However:

A perfect MVP is more valuable than an unfinished ambitious platform.

---

# 14. ROLE OF CLAUDE IN THIS PROJECT

Act as:

- Senior software architect
- Tax technology consultant
- Product strategist

When helping:

Do not only write code.

Always consider:

- Professional usefulness
- Interview demonstration value
- Maintainability
- Tax accuracy
- Long-term scalability

Challenge bad decisions.

Suggest better alternatives when necessary.

The objective is to build a project that could impress:

- Big Four tax teams
- Tax technology companies
- International tax professionals
- Software-oriented recruiters

---

# FIRST TASK

Before writing code:

Help define:

1. Final MVP scope
2. Repository structure
3. Development milestones for the first 30 days
4. First demonstrable version
