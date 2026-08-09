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

from typing import Dict, List

from tp_domain.models import Source, SourceKind

RESEARCH_ROOT = "documentation/tax-research"


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
)

DE_ASTG_1_3A = Source(
    id="de-astg-1-3a",
    kind=SourceKind.LEGISLATION,
    citation="Außensteuergesetz (AStG), §1.3a",
    pinpoint="§1.3a — estrechamiento del rango y ajuste a la mediana",
    official_ref="AStG §1 Abs. 3a",
    research_note=f"{RESEARCH_ROOT}/jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md",
    disclaimer=(
        "La ficha de investigación marca la lectura del §1.3 como dirigida, no "
        "exhaustiva. Verificar el texto vigente antes de usar como asesoramiento."
    ),
)

OECD_TPG_2022_CH3 = Source(
    id="oecd-tpg-2022-cap3",
    kind=SourceKind.GUIDELINES,
    citation="OECD Transfer Pricing Guidelines 2022, Cap. III",
    pinpoint="Análisis de comparabilidad y rango de plena competencia",
    research_note=f"{RESEARCH_ROOT}/frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md",
    disclaimer=(
        "Las Directrices no imponen un método de cálculo de percentiles. La "
        "convención empleada se declara en el propio informe."
    ),
)

OECD_TPG_2022_CH6 = Source(
    id="oecd-tpg-2022-cap6",
    kind=SourceKind.GUIDELINES,
    citation="OECD Transfer Pricing Guidelines 2022, Cap. VI",
    pinpoint="Intangibles — marco DEMPE (párr. 6.34)",
    research_note=f"{RESEARCH_ROOT}/frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md",
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
