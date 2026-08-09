# Transfer Pricing Intelligence Platform (TPIP)

![Tests](https://github.com/danirubio2323-commits/transfer-pricing-intelligence-platform/actions/workflows/tests.yml/badge.svg)

TP analysis platform for transfer pricing validation

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Run the app

```bash
streamlit run ui/app.py
```

The app opens in your browser at `http://localhost:8501`

### Important

- Always run `pip install -e .` first (makes `tp_domain` importable)
- The project requires Python 3.10+

## Report

Every analysis produces a professional PDF report — cover with dataset
disclosure, executive summary, benchmark chart, legal basis per jurisdiction,
and the full annex of accepted and rejected comparables.

```python
from infrastructure.report import build_report
build_report(result, "report.pdf")
```

The report is generated without any API call. The AI explanation is an
additive section: its absence does not degrade the document.

## AI layer (optional)

Claude writes a narrative explanation **of an already-calculated analysis**.
It never computes, decides, or introduces sources the engine did not emit.

```bash
cp .env.example .env    # then fill in ANTHROPIC_API_KEY
```

Key precedence: `st.secrets` > environment variable > `.env` > none.
With no key the app runs normally and the PDF is generated without the AI
section. The model id is read from `ANTHROPIC_MODEL`; if unset, the newest
available Sonnet is resolved at runtime and recorded in the report.

Every draft is validated before it reaches the report: cited source ids must
belong to the closed registry the engine emitted, and legal references found in
the prose are checked against it too. A rejected draft is retried once with the
rejection reasons only; if it fails again, the report ships without the section.
