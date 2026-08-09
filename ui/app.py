"""
Interfaz Streamlit de TPIP.

Esta capa no calcula nada: construye una `Transaction`, llama al dominio y
presenta el `AnalysisResult`. Cualquier cálculo que aparezca aquí es un bug.

El acabado visual (jerarquía, gráfico de rango, tipografía) se aborda en el
pase de presentación al cierre de la Fase 1.
"""

import datetime as dt
from decimal import Decimal

import streamlit as st

from infrastructure.report.pdf_report import render_report_bytes
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import (
    SUPPORTED_TRANSACTION_TYPES,
    DefensibilityLevel,
    Industry,
    RangeRule,
    Severity,
    Transaction,
)

st.set_page_config(
    page_title="TPIP — Transfer Pricing Analyzer",
    layout="wide",
)

# Caso de referencia de la demo: canon de software España -> Alemania.
# Alemania importa porque el §1.3a AStG impone ajuste a la mediana y España no
# tiene regla estadística: la misma operación, dos consecuencias.
DEMO_CASE = {
    "description": "Canon por licencia de tecnología",
    "payer_country": "ES",
    "recipient_country": "DE",
    "industry": Industry.SOFTWARE,
    "amount_eur": 1_000_000,
    "rate_percent": 12.0,
}

st.title("Transfer Pricing Intelligence Platform")
st.caption(
    "Evalúa si un canon intragrupo resiste el principio de plena competencia, "
    "y qué consecuencia tiene en cada jurisdicción implicada."
)

if "case" not in st.session_state:
    st.session_state.case = dict(DEMO_CASE)

with st.sidebar:
    st.header("Operación")
    if st.button("Cargar caso de ejemplo", use_container_width=True):
        st.session_state.case = dict(DEMO_CASE)

    case = st.session_state.case

    with st.form("transaction_form"):
        description = st.text_input("Descripción", value=case["description"])

        col1, col2 = st.columns(2)
        with col1:
            payer_country = st.text_input(
                "País pagador", value=case["payer_country"], max_chars=2,
                help="Quién paga el canon y deduce el gasto",
            )
        with col2:
            recipient_country = st.text_input(
                "País perceptor", value=case["recipient_country"], max_chars=2,
            )

        st.selectbox(
            "Tipo de operación",
            [t.value for t in sorted(SUPPORTED_TRANSACTION_TYPES, key=lambda t: t.value)],
            help="Fase 1 cubre únicamente cánones sobre intangibles",
        )

        industry = st.selectbox(
            "Industria",
            [i.value for i in Industry],
            index=[i.value for i in Industry].index(case["industry"].value),
        )

        col1, col2 = st.columns(2)
        with col1:
            amount_eur = st.number_input(
                "Importe (EUR)", value=case["amount_eur"], min_value=1, step=100_000
            )
        with col2:
            rate_percent = st.number_input(
                "Tipo propuesto (%)", value=case["rate_percent"],
                min_value=0.0, max_value=100.0, step=0.5,
            )

        effective_date = st.date_input("Fecha de efecto", value=dt.date(2026, 1, 1))
        submitted = st.form_submit_button("Analizar", use_container_width=True)

    st.divider()
    st.caption(
        "Los comparables son sintéticos. La herramienta demuestra el motor de "
        "análisis; no produce estudios oponibles ante una administración."
    )

if not submitted:
    st.info("Introduce una operación o carga el caso de ejemplo para empezar.")
    st.stop()

try:
    transaction = Transaction(
        description=description,
        payer_country=payer_country,
        recipient_country=recipient_country,
        transaction_type="royalty",
        industry=industry,
        amount_eur=Decimal(str(amount_eur)),
        rate_percent=Decimal(str(rate_percent)),
        effective_date=effective_date,
    )
except ValueError as exc:
    st.error(f"Operación no válida: {exc}")
    st.stop()

result = calculate_arm_length_range(transaction)
benchmark = result.benchmark

if benchmark.count_accepted == 0:
    st.error(result.conclusion)
    st.stop()

# --- Entregable -------------------------------------------------------------
st.download_button(
    "Descargar informe (PDF)",
    data=render_report_bytes(result),
    file_name=f"{result.analysis_id}.pdf",
    mime="application/pdf",
    help="Informe completo: benchmark, fundamento por jurisdicción y anexo de comparables",
)

# --- Rango de mercado -------------------------------------------------------
st.subheader("Rango de plena competencia")
st.caption(
    f"Método: {result.method_applied.value.upper()} · "
    f"{benchmark.count_accepted} comparables aceptados · "
    f"percentiles por {benchmark.percentile_method}"
)

cols = st.columns(5)
for col, label, value in zip(
    cols,
    ["P10", "P25", "Mediana", "P75", "P90"],
    [benchmark.percentile_10, benchmark.percentile_25, benchmark.percentile_50,
     benchmark.percentile_75, benchmark.percentile_90],
):
    col.metric(label, f"{value}%")

st.metric("Tipo propuesto", f"{float(transaction.rate_percent)}%")

st.divider()

# --- Veredicto por jurisdicción ---------------------------------------------
st.subheader("Tratamiento por jurisdicción")

for col, assessment in zip(st.columns(len(result.assessments)), result.assessments):
    with col:
        st.markdown(f"### {assessment.country}")
        st.caption(assessment.role.value)

        if assessment.defensibility_level is DefensibilityLevel.STRONG:
            st.success(f"Defendible — {assessment.defensibility_score}/10")
        elif assessment.defensibility_level is DefensibilityLevel.MODERATE:
            st.warning(f"Moderado — {assessment.defensibility_score}/10")
        else:
            st.error(f"Riesgo alto — {assessment.defensibility_score}/10")

        if assessment.adjusted_rate is not None:
            st.metric("Ajuste de oficio", f"{assessment.adjusted_rate}%")
        elif assessment.range_rule is RangeRule.NO_STATUTORY_RULE:
            st.metric("Ajuste de oficio", "No automático")

        st.write(assessment.consequence)

st.divider()

# --- Riesgos ----------------------------------------------------------------
st.subheader("Factores de riesgo")
for factor in result.risk_factors:
    if factor.severity is Severity.CRITICAL:
        st.error(factor.message)
    elif factor.severity is Severity.WARNING:
        st.warning(factor.message)
    else:
        st.info(factor.message)

st.subheader("Conclusión")
st.write(result.conclusion)

# --- Anexos -----------------------------------------------------------------
with st.expander(f"Comparables aceptados ({len(result.comparables_accepted)})"):
    st.dataframe(
        [
            {
                "ID": c.id, "Compañía": c.company_name, "País": c.country,
                "Industria": c.industry.value, "Canon %": c.royalty_rate,
                "Ejercicio": c.data_year,
            }
            for c in result.comparables_accepted
        ],
        use_container_width=True, hide_index=True,
    )

with st.expander(f"Comparables rechazados ({len(result.comparables_rejected)})"):
    st.dataframe(
        [
            {"ID": r.comparable_id, "Compañía": r.company_name,
             "Motivo": r.reason.value, "Detalle": r.detail}
            for r in result.comparables_rejected
        ],
        use_container_width=True, hide_index=True,
    )

with st.expander(f"Fuentes citadas ({len(result.sources)})"):
    for src in result.sources:
        st.markdown(f"**{src.citation}**" + (f" — {src.pinpoint}" if src.pinpoint else ""))
        if src.official_ref:
            st.caption(src.official_ref)
        if src.disclaimer:
            st.caption(src.disclaimer)

st.caption(
    f"Análisis {result.analysis_id} · motor {result.engine_version} · "
    f"dataset {result.dataset_version} · {result.created_at:%Y-%m-%d %H:%M}"
)
