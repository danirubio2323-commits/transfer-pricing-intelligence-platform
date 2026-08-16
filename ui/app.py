"""
Interfaz de TPIP.

Esta capa no calcula nada: construye una `Transaction`, llama al dominio y
presenta el `AnalysisResult`. Cualquier aritmética que aparezca aquí es un bug.

Jerarquía de lectura, en este orden y por este motivo:

    1. Veredicto en una frase — qué ha pasado
    2. Rango con el tipo situado — por qué, en dos segundos
    3. Comparación por jurisdicción — la asimetría, que es el argumento
    4. Riesgos, fuentes y anexos — el soporte
    5. Entregable — el informe

El índice de defensibilidad va deliberadamente subordinado a la posición
estadística: es una etiqueta derivada de dónde cae el tipo, no una puntuación
propia.
"""

import datetime as dt
from decimal import Decimal

import streamlit as st

from ai.claude_client import explain_analysis, resolve_api_key
from infrastructure.charts import benchmark_range_svg
from infrastructure.report.pdf_report import render_report_bytes
from infrastructure.theme import (
    COLORS,
    LEVEL_COLOR,
    LEVEL_LABEL,
    POSITION_LABEL,
    REJECTION_LABEL,
    ROLE_LABEL,
    RULE_LABEL_SHORT,
    SEVERITY_LABEL,
    VERIFICATION_CONFIDENCE_LABEL,
)
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import Industry, RangeRule, Severity, Transaction

st.set_page_config(
    page_title="TPIP · Análisis de plena competencia",
    layout="wide",
)

#: Caso de referencia. Alemania importa: el §1.3a AStG impone ajuste a la
#: mediana y España no tiene regla estadística, así que la misma operación
#: recibe dos tratamientos distintos.
DEMO_CASE = {
    "description": "Canon por licencia de tecnología de software",
    "payer_country": "ES",
    "recipient_country": "DE",
    "industry": Industry.SOFTWARE,
    "amount_eur": 1_000_000,
    "rate_percent": 12.0,
    "effective_date": dt.date(2026, 1, 1),
}

st.markdown(
    f"""
    <style>
      .tpip-eyebrow {{
        font-size: 0.72rem; letter-spacing: .13em; text-transform: uppercase;
        color: {COLORS["muted"]}; margin-bottom: .1rem;
      }}
      .tpip-title {{
        font-size: 1.85rem; font-weight: 700; color: {COLORS["ink"]};
        line-height: 1.15; margin: 0 0 .2rem 0;
      }}
      .tpip-verdict {{
        font-size: 1.28rem; line-height: 1.45; color: {COLORS["ink"]};
        margin: .1rem 0 .35rem 0;
      }}
      .tpip-notice {{
        border-left: 3px solid {COLORS["risk"]};
        background: {COLORS["surface"]};
        padding: .7rem .95rem; margin: .4rem 0 1.1rem 0;
        font-size: .82rem; color: {COLORS["ink"]};
      }}
      .tpip-card {{
        border: 1px solid {COLORS["rule"]}; border-top: 4px solid var(--accent);
        background: #FFFFFF; padding: 1rem 1.15rem 1.15rem 1.15rem;
        height: 100%;
      }}
      .tpip-card h3 {{
        font-size: 1.35rem; margin: 0; color: {COLORS["ink"]}; font-weight: 700;
      }}
      .tpip-card .role {{
        font-size: .72rem; text-transform: uppercase; letter-spacing: .1em;
        color: {COLORS["muted"]};
      }}
      .tpip-rule {{
        font-size: .85rem; font-weight: 600; color: var(--accent);
        margin: .55rem 0 .1rem 0;
      }}
      .tpip-outcome {{
        font-size: 1.5rem; font-weight: 700; color: {COLORS["ink"]};
        margin: .45rem 0 .05rem 0;
      }}
      .tpip-outcome small {{
        display: block; font-size: .74rem; font-weight: 400;
        color: {COLORS["muted"]}; letter-spacing: .04em; text-transform: uppercase;
      }}
      .tpip-consequence {{
        font-size: .84rem; line-height: 1.5; color: {COLORS["ink"]};
        margin-top: .7rem;
      }}
      .tpip-index {{
        font-size: .74rem; color: {COLORS["muted"]}; margin-top: .8rem;
        border-top: 1px solid {COLORS["rule"]}; padding-top: .5rem;
      }}
      .tpip-meta {{
        font-size: .72rem; color: {COLORS["muted"]}; margin-top: 1.6rem;
        border-top: 1px solid {COLORS["rule"]}; padding-top: .6rem;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="tpip-eyebrow">Transfer Pricing Intelligence Platform</div>'
    '<div class="tpip-title">Análisis de plena competencia</div>',
    unsafe_allow_html=True,
)

if "case" not in st.session_state:
    st.session_state.case = dict(DEMO_CASE)
if "run" not in st.session_state:
    st.session_state.run = False


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("**Operación vinculada**")

    if st.button("Cargar caso de referencia (ES → DE, canon 12%)",
                 use_container_width=True):
        st.session_state.case = dict(DEMO_CASE)
        st.session_state.run = True

    case = st.session_state.case

    with st.form("transaction_form"):
        description = st.text_input("Descripción", value=case["description"])

        col1, col2 = st.columns(2)
        with col1:
            payer_country = st.text_input(
                "Jurisdicción pagadora", value=case["payer_country"], max_chars=2,
                help="Satisface el canon y deduce el gasto",
            )
        with col2:
            recipient_country = st.text_input(
                "Jurisdicción perceptora", value=case["recipient_country"],
                max_chars=2,
            )

        # Un desplegable con una sola opción es un control muerto: informa mejor
        # como texto, y deja claro el alcance de esta versión.
        st.text_input(
            "Tipo de operación", value="Canon sobre intangibles",
            disabled=True,
            help="Esta versión cubre exclusivamente cánones. Los servicios "
                 "intragrupo requieren su propia rama de cálculo.",
        )

        industry = st.selectbox(
            "Sector", [i.value for i in Industry],
            index=[i.value for i in Industry].index(case["industry"].value),
        )

        col1, col2 = st.columns(2)
        with col1:
            amount_eur = st.number_input(
                "Importe (EUR)", value=case["amount_eur"], min_value=1,
                step=100_000,
            )
        with col2:
            rate_percent = st.number_input(
                "Tipo propuesto (%)", value=case["rate_percent"],
                min_value=0.0, max_value=100.0, step=0.5,
            )

        effective_date = st.date_input(
            "Fecha de efecto", value=case["effective_date"]
        )
        if st.form_submit_button("Analizar", use_container_width=True):
            st.session_state.run = True

if not st.session_state.run:
    st.markdown(
        '<div class="tpip-verdict">Introduzca una operación vinculada o cargue '
        "el caso de referencia para iniciar el análisis.</div>",
        unsafe_allow_html=True,
    )
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
    st.error(f"La operación no supera la validación del dominio: {exc}")
    st.stop()

result = calculate_arm_length_range(transaction)
benchmark = result.benchmark

if benchmark.count_accepted == 0:
    st.error(result.conclusion)
    st.stop()

position = result.assessments[0].position
rate = float(transaction.rate_percent)


# ---------------------------------------------------------------------------
# 1. Veredicto
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="tpip-verdict">El canon propuesto del <strong>{rate}%</strong> '
    f"({transaction.industry.value}, {transaction.payer_country} → "
    f"{transaction.recipient_country}) se sitúa "
    f"<strong>{POSITION_LABEL[position].lower()}</strong> del rango de "
    f"comparables.</div>",
    unsafe_allow_html=True,
)

dataset_source = next((s for s in result.sources if s.id == "tpip-dataset-v1"), None)
if dataset_source and dataset_source.disclaimer:
    st.markdown(
        f'<div class="tpip-notice">{dataset_source.disclaimer}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 2. Rango
# ---------------------------------------------------------------------------

chart = benchmark_range_svg(result)
if chart:
    st.markdown(chart, unsafe_allow_html=True)

st.caption(
    f"Método {result.method_applied.value.upper()} · "
    f"{benchmark.count_accepted} comparables aceptados y "
    f"{len(result.comparables_rejected)} rechazados · "
    f"percentiles por {benchmark.percentile_method}"
)

st.divider()


# ---------------------------------------------------------------------------
# 3. Comparación por jurisdicción — el argumento de la herramienta
# ---------------------------------------------------------------------------

st.markdown("#### Tratamiento por jurisdicción")
st.caption(
    "Mismo tipo, mismos comparables, mismo rango. La consecuencia la fija "
    "cada ordenamiento."
)

for column, assessment in zip(st.columns(len(result.assessments)), result.assessments):
    accent = LEVEL_COLOR[assessment.defensibility_level]

    if assessment.adjusted_rate is not None:
        outcome = f"{assessment.adjusted_rate}%"
        outcome_label = "Ajuste de oficio a la mediana"
    elif assessment.range_rule is RangeRule.NO_STATUTORY_RULE:
        outcome = "No automático"
        outcome_label = "Ajuste · valoración caso por caso"
    else:
        outcome = "No evaluado"
        outcome_label = "Regla no modelada en esta versión"

    with column:
        st.markdown(
            f'<div class="tpip-card" style="--accent:{accent}">'
            f'<h3>{assessment.country}</h3>'
            f'<div class="role">{ROLE_LABEL[assessment.role]}</div>'
            f'<div class="tpip-rule">{RULE_LABEL_SHORT[assessment.range_rule]}</div>'
            f'<div class="tpip-outcome">{outcome}'
            f"<small>{outcome_label}</small></div>"
            f'<div class="tpip-consequence">{assessment.consequence}</div>'
            f'<div class="tpip-index">Posición: {POSITION_LABEL[assessment.position]}'
            f" · índice de defensibilidad "
            f"{assessment.defensibility_score}/10 "
            f"({LEVEL_LABEL[assessment.defensibility_level].lower()})</div>"
            "</div>",
            unsafe_allow_html=True,
        )

st.divider()


# ---------------------------------------------------------------------------
# 4. Soporte
# ---------------------------------------------------------------------------

st.markdown("#### Factores de riesgo")
for factor in result.risk_factors:
    label = SEVERITY_LABEL[factor.severity]
    if factor.severity is Severity.CRITICAL:
        st.error(f"**{label}** · {factor.message}")
    elif factor.severity is Severity.WARNING:
        st.warning(f"**{label}** · {factor.message}")
    else:
        st.info(f"**{label}** · {factor.message}")

with st.expander(f"Fuentes citadas ({len(result.sources)})"):
    for source in result.sources:
        pinpoint = f" — {source.pinpoint}" if source.pinpoint else ""
        st.markdown(f"**{source.citation}**{pinpoint}")

        verification = f"{source.jurisdiction} · {source.verified_at:%d/%m/%Y}"
        if source.verification_confidence is not None:
            verification += f" · {VERIFICATION_CONFIDENCE_LABEL[source.verification_confidence]}"
        verification += f" · {source.locator_type.value}: {source.locator}"
        st.caption(verification)

        if source.disclaimer:
            st.caption(source.disclaimer)

with st.expander(f"Comparables aceptados ({len(result.comparables_accepted)})"):
    st.dataframe(
        [
            {
                "Referencia": c.id, "Compañía": c.company_name, "País": c.country,
                "Sector": c.industry.value, "Canon": f"{c.royalty_rate}%",
                "Ejercicio": c.data_year,
            }
            for c in result.comparables_accepted
        ],
        use_container_width=True, hide_index=True,
    )

with st.expander(f"Comparables rechazados ({len(result.comparables_rejected)})"):
    st.dataframe(
        [
            {
                "Referencia": r.comparable_id, "Compañía": r.company_name,
                "Motivo": REJECTION_LABEL[r.reason], "Detalle": r.detail,
            }
            for r in result.comparables_rejected
        ],
        use_container_width=True, hide_index=True,
    )

st.divider()


# ---------------------------------------------------------------------------
# 5. Entregable
# ---------------------------------------------------------------------------

st.markdown("#### Informe")

if resolve_api_key():
    if st.checkbox(
        "Incorporar explicación redactada con asistencia de IA",
        help="La explicación se redacta sobre el análisis ya calculado y se "
             "valida contra las fuentes emitidas por el motor antes de "
             "incorporarse al informe.",
    ):
        with st.spinner("Redactando explicación sobre el análisis calculado"):
            explanation = explain_analysis(result)
        if explanation is None:
            st.warning(
                "La explicación no ha superado la validación automática y se ha "
                "descartado. El informe se emite sin esa sección."
            )
        else:
            result = result.model_copy(update={"ai_explanation": explanation})
            st.caption(f"Explicación validada · modelo {explanation.model}")
else:
    st.caption(
        "Sin ANTHROPIC_API_KEY configurada. El informe se emite sin sección de "
        "IA; su ausencia no afecta al análisis."
    )

st.download_button(
    "Descargar informe (PDF)",
    data=render_report_bytes(result),
    file_name=f"{result.analysis_id}.pdf",
    mime="application/pdf",
    type="primary",
)

st.markdown(
    f'<div class="tpip-meta">Análisis {result.analysis_id} · motor '
    f"{result.engine_version} · dataset {result.dataset_version} · "
    f"{result.created_at:%d/%m/%Y %H:%M}</div>",
    unsafe_allow_html=True,
)
