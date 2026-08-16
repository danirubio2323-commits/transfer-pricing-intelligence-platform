"""
Registro de fuentes de TPIP.

Registro CERRADO: el motor solo puede emitir fuentes definidas aquí, y la capa
de IA solo puede citar fuentes emitidas por el motor. Es lo que impide que una
explicación generada invente referencias a párrafos de las Directrices.

Cada entrada apunta a su ficha de investigación en `documentation/tax-research/`,
que a su vez remite a la fuente primaria. La cadena módulo -> ficha -> norma es
lo que hace defendible un informe.

Fase 1: cinco entradas. Crece con `tp_domain/rules/`, no antes.
"""

import datetime as dt
from typing import Dict, List

from tp_domain.models import LocatorType, Source, SourceKind, VerificationConfidence

RESEARCH_ROOT = "documentation/tax-research"

#: Fecha de la sesión de verificación de Fase 1 (estabilización del corpus).
#: Todas las entradas migradas en ese paso comparten esta fecha porque se
#: revisaron en la misma sesión, no porque el motor lo exija.
_PHASE1_VERIFICATION_DATE = dt.date(2026, 8, 10)


ES_LIS_ART18_4 = Source(
    id="es-lis-art18-4",
    kind=SourceKind.LEGISLATION,
    citation="Ley 27/2014, del Impuesto sobre Sociedades, Art. 18.4",
    pinpoint="Art. 18.4 — determinación del valor de mercado",
    official_ref="BOE-A-2014-12328",
    research_note=f"{RESEARCH_ROOT}/jurisdictions/spain/art18-lis-operaciones-vinculadas.md",
    disclaimer=(
        "El Art. 18.4 LIS no contiene regla estadística: no impone rango "
        "intercuartílico ni ajuste a la mediana. Exige aplicar el método más "
        "adecuado de entre los cinco de la OCDE."
    ),
    jurisdiction="ES",
    locator_type=LocatorType.BOE_ID,
    locator="BOE-A-2014-12328",
    verified_at=_PHASE1_VERIFICATION_DATE,
    verification_confidence=VerificationConfidence.PRIMARY_SOURCE_VERIFIED,
    # Verificado en vivo vía mcp-boe (get_consolidated_law): norma vigente,
    # consolidación actualizada. ELI: https://www.boe.es/eli/es/l/2014/11/27/27
)

DE_ASTG_1_3A = Source(
    id="de-astg-1-3a",
    kind=SourceKind.LEGISLATION,
    citation="Außensteuergesetz (AStG), §1.3a",
    pinpoint="§1.3a — estrechamiento del rango y ajuste a la mediana",
    official_ref="AStG §1 Abs. 3a",
    research_note=f"{RESEARCH_ROOT}/jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md",
    disclaimer=(
        "La ficha de investigación original marcaba la lectura del §1.3 como "
        "dirigida, no exhaustiva. En Fase 1 (2026-08-10) se verificó el texto "
        "vigente del §1 Abs. 3a contra el portal oficial "
        "gesetze-im-internet.de (Bundesministerium der Justiz), coincidente "
        "con la copia en `raw/Derecho_Comparado/Alemania/`. Queda pendiente "
        "de re-verificación periódica: no existe MCP de vigilancia normativa "
        "alemana equivalente a MCP-BOE."
    ),
    jurisdiction="DE",
    locator_type=LocatorType.URL,
    locator="https://www.gesetze-im-internet.de/astg/__1.html",
    verified_at=_PHASE1_VERIFICATION_DATE,
    verification_confidence=VerificationConfidence.PRIMARY_SOURCE_VERIFIED,
    quote=(
        "(3a) ... Liegt der vom Steuerpflichtigen für seine "
        "Einkünfteermittlung verwendete Wert außerhalb der Bandbreite gemäß "
        "Satz 1 oder der eingeengten Bandbreite, ist der Median maßgeblich, "
        "wenn der Steuerpflichtige nicht glaubhaft macht, dass ein anderer "
        "Wert innerhalb der Bandbreite dem Fremdvergleichsgrundsatz besser "
        "entspricht."
    ),
)

OECD_TPG_2022_CH3 = Source(
    id="oecd-tpg-2022-cap3",
    kind=SourceKind.GUIDELINES,
    citation="OECD Transfer Pricing Guidelines 2022, Cap. III",
    pinpoint="Análisis de comparabilidad y rango de plena competencia (párr. 3.55-3.59)",
    research_note=f"{RESEARCH_ROOT}/frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md",
    disclaimer=(
        "Las Directrices no imponen un método de cálculo de percentiles. La "
        "convención empleada se declara en el propio informe. Publicación "
        "OCDE de pago, sin identificador público equivalente a CELEX/ELI: "
        "localizador OFFLINE contra el PDF adquirido en el corpus local. El "
        "Capítulo III no estaba investigado en ninguna ficha de "
        "Cerebros_Fiscales antes de Fase 1 — la ficha derivada de TPIP solo "
        "cubría los Capítulos I, VI y VII."
    ),
    jurisdiction="OECD",
    locator_type=LocatorType.OFFLINE,
    locator=(
        "raw/Normativa_Internacional/OCDE_BEPS/OCDE, Transfer Pricing "
        "Guidelines (ene 2022) Directrices Precios de Transferencia.pdf — "
        "p. 165 impresa (índice PDF 166), párr. 3.55-3.59"
    ),
    verified_at=_PHASE1_VERIFICATION_DATE,
    verification_confidence=VerificationConfidence.PRIMARY_SOURCE_VERIFIED,
    quote=(
        "3.57. ... In such cases, if the range includes a sizeable number of "
        "observations, statistical tools that take account of central "
        "tendency to narrow the range (e.g. the interquartile range or other "
        "percentiles) might help to enhance the reliability of the analysis."
    ),
)

OECD_TPG_2022_CH6 = Source(
    id="oecd-tpg-2022-cap6",
    kind=SourceKind.GUIDELINES,
    citation="OECD Transfer Pricing Guidelines 2022, Cap. VI",
    pinpoint="Intangibles — marco DEMPE (párr. 6.34); propiedad legal no confiere el retorno (párr. 6.42)",
    research_note=f"{RESEARCH_ROOT}/frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md",
    disclaimer=(
        "Publicación OCDE de pago, sin identificador público equivalente a "
        "CELEX/ELI: localizador OFFLINE contra el PDF adquirido en el corpus "
        "local."
    ),
    jurisdiction="OECD",
    locator_type=LocatorType.OFFLINE,
    locator=(
        "raw/Normativa_Internacional/OCDE_BEPS/OCDE, Transfer Pricing "
        "Guidelines (ene 2022) Directrices Precios de Transferencia.pdf — "
        "p. 259 impresa (índice PDF 260), párr. 6.42"
    ),
    verified_at=_PHASE1_VERIFICATION_DATE,
    verification_confidence=VerificationConfidence.PRIMARY_SOURCE_VERIFIED,
    quote=(
        "6.42. ... For transfer pricing purposes, legal ownership of "
        "intangibles, by itself, does not confer any right ultimately to "
        "retain returns derived by the MNE group from exploiting the "
        "intangible ... The return ultimately retained by or attributed to "
        "the legal owner depends upon the functions it performs, the assets "
        "it uses, and the risks it assumes."
    ),
)

TPIP_DATASET_V1 = Source(
    id="tpip-dataset-v1",
    kind=SourceKind.DATASET,
    citation="TPIP — dataset de comparables sintético v1",
    research_note=f"{RESEARCH_ROOT}/frameworks/criterios-seleccion-comparables.md",
    disclaimer=(
        "DATOS SINTÉTICOS. Los comparables no proceden de compañías reales ni "
        "de bases comerciales (Orbis, Amadeus, Bloomberg). Son valores "
        "generados con rangos plausibles por sector para demostrar el "
        "funcionamiento del motor. Ningún resultado de esta herramienta "
        "constituye un estudio de benchmarking utilizable ante una "
        "administración tributaria."
    ),
    jurisdiction="GLOBAL",
    locator_type=LocatorType.INTERNAL,
    locator="tp_domain/comparables.json",
    verified_at=_PHASE1_VERIFICATION_DATE,
    # Sin verification_confidence: no es una fuente jurídica que verificar
    # contra un texto primario, es un dataset generado internamente. La
    # honestidad sobre su naturaleza la da el disclaimer, no este campo.
)


#: Registro cerrado. Toda fuente citable de Fase 1 está aquí.
SOURCE_REGISTRY: Dict[str, Source] = {
    s.id: s
    for s in (
        ES_LIS_ART18_4,
        DE_ASTG_1_3A,
        OECD_TPG_2022_CH3,
        OECD_TPG_2022_CH6,
        TPIP_DATASET_V1,
    )
}


def resolve(source_ids: List[str]) -> List[Source]:
    """
    Resuelve ids contra el registro, preservando el orden y sin duplicar.

    Lanza KeyError si un id no existe: un fallo ruidoso aquí es preferible a
    un informe que cita una fuente inexistente.
    """
    seen = set()
    resolved: List[Source] = []
    for sid in source_ids:
        if sid in seen:
            continue
        if sid not in SOURCE_REGISTRY:
            raise KeyError(
                f"Fuente desconocida: '{sid}'. El registro de Fase 1 contiene: "
                f"{sorted(SOURCE_REGISTRY)}"
            )
        seen.add(sid)
        resolved.append(SOURCE_REGISTRY[sid])
    return resolved
