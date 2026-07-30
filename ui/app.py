"""
Streamlit UI for TPIP (Transfer Pricing Intelligence Platform)

Simple web interface to analyze transfer pricing transactions.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tp_domain.models import (
    Transaction, TransactionType, TPMethod,
    BenchmarkRange, AnalysisResult, DefensibilityLevel, Comparable
)

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="TPIP - Transfer Pricing Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("🔍 Transfer Pricing Intelligence Platform")
st.markdown("**Validate if your transfer prices are arm's length defensible**")

# ============================================================================
# SIDEBAR: Input form
# ============================================================================

st.sidebar.header("Transaction Details")

with st.sidebar.form("transaction_form"):
    st.write("### Enter Transaction")

    # Identificación
    description = st.text_input(
        "Transaction Description",
        value="Royalty payment for patent license",
        help="Brief description of what this transaction is"
    )

    # Países
    col1, col2 = st.columns(2)
    with col1:
        from_country = st.text_input("From Country", value="ES", max_chars=2)
    with col2:
        to_country = st.text_input("To Country", value="LU", max_chars=2)

    # Tipo de transacción
    transaction_type = st.selectbox(
        "Transaction Type",
        [t.value for t in TransactionType]
    )

    # Datos económicos
    col1, col2 = st.columns(2)
    with col1:
        amount_eur = st.number_input("Amount (EUR)", value=1000000, min_value=1, step=100000)
    with col2:
        rate_percent = st.number_input("Proposed Rate (%)", value=12.0, min_value=0.0, max_value=100.0, step=0.5)

    # Fecha
    effective_date = st.date_input("Effective Date", value=datetime.now())

    # TP Method hint
    method_hint = st.selectbox(
        "Suggested TP Method (optional)",
        ["Auto-detect"] + [m.value for m in TPMethod]
    )

    # Submit button
    submitted = st.form_submit_button("📊 Analyze Transaction")

# ============================================================================
# MAIN CONTENT: Results
# ============================================================================

if submitted:
    st.divider()
    st.header("📈 Analysis Results")

    # Create transaction object
    try:
        transaction = Transaction(
            description=description,
            from_country=from_country.upper(),
            to_country=to_country.upper(),
            transaction_type=transaction_type,
            amount_eur=amount_eur,
            rate_percent=rate_percent,
            effective_date=effective_date,
            method_hint=None if method_hint == "Auto-detect" else method_hint
        )

        # MOCK RESULT (for now, hardcoded)
        # Later this will call real analysis logic

        comparable_1 = Comparable(
            id="comp_001",
            company_name="Pharma Corp AG",
            country="CH",
            industry="pharmaceutical",
            royalty_rate=5.2,
            data_year=2024,
            source="OECD TP Database"
        )

        comparable_2 = Comparable(
            id="comp_002",
            company_name="BioTech Ltd",
            country="DE",
            industry="pharmaceutical",
            royalty_rate=6.8,
            data_year=2024,
            source="OECD TP Database"
        )

        result = AnalysisResult(
            transaction_id="tx_001",
            method_recommended=TPMethod.CUP,
            benchmark_range=BenchmarkRange(
                percentile_25=4.5,
                percentile_50=6.1,
                percentile_75=8.2,
                count_comparables=23
            ),
            proposed_rate=rate_percent,
            defensibility_score=4,
            defensibility_level=DefensibilityLevel.WEAK,
            comparables_used=[comparable_1, comparable_2],
            risk_factors=[
                f"Rate {rate_percent}% exceeds 90th percentile (8.2%)",
                "Only 2 recent comparables found for this industry"
            ],
            conclusion="This transfer price is RISKY. High probability of audit challenge. Consider adjusting rate to 6-8% range."
        )

        # Display results in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Defensibility Score",
                f"{result.defensibility_score}/10",
                delta=None
            )

        with col2:
            st.metric(
                "Your Rate",
                f"{result.proposed_rate}%",
                delta=None
            )

        with col3:
            st.metric(
                "Median Rate",
                f"{result.benchmark_range.percentile_50}%",
                delta=None
            )

        with col4:
            st.metric(
                "Comparables",
                f"{result.benchmark_range.count_comparables}",
                delta=None
            )

        st.divider()

        # Benchmark range visualization
        st.subheader("Benchmark Range (Arm's Length)")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Create a simple bar representation
            benchmark = result.benchmark_range
            your_rate = result.proposed_rate

            st.write(f"""
            **Percentile 25:** {benchmark.percentile_25}%
            **Percentile 50 (Median):** {benchmark.percentile_50}%
            **Percentile 75:** {benchmark.percentile_75}%

            **Your Proposed Rate:** {your_rate}%
            """)

        with col2:
            if result.defensibility_level == DefensibilityLevel.STRONG:
                st.success("✅ STRONG", icon="✅")
            elif result.defensibility_level == DefensibilityLevel.MODERATE:
                st.warning("⚠️ MODERATE", icon="⚠️")
            else:
                st.error("❌ WEAK", icon="❌")

        st.divider()

        # Risk factors
        st.subheader("⚠️ Risk Factors")
        for risk in result.risk_factors:
            st.warning(risk)

        st.divider()

        # Conclusion
        st.subheader("📋 Conclusion")
        st.info(result.conclusion)

        # Comparables used
        st.subheader("📊 Comparables Used")
        for comp in result.comparables_used:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{comp.company_name}**")
            with col2:
                st.write(f"{comp.country} | {comp.industry}")
            with col3:
                st.write(f"Rate: {comp.royalty_rate}%")

    except ValueError as e:
        st.error(f"Error: {e}")

# ============================================================================
# SIDEBAR: Instructions
# ============================================================================

st.sidebar.divider()
st.sidebar.markdown("""
### 📚 How It Works

1. **Fill in transaction details** on the left
2. **Click "Analyze"** to validate
3. **See benchmark comparison** and risk score
4. **Export report** when ready

### About Defensibility Score
- **8-10: STRONG** — Defensible in audit
- **5-7: MODERATE** — Requires documentation
- **1-4: WEAK** — High audit risk
""")
