from __future__ import annotations

import re

import pandas as pd

from .config import LOT_OPTIONS, PEV_INDICATORS, REGION_TO_LOT, TYPE_TO_INDICATORS


def normalize_region_name(value: object) -> str:
    if pd.isna(value):
        return ""

    region = str(value).replace("_x000D_", " ").replace("\n", " ")
    region = region.replace("–", "-").strip()
    region = re.sub(r"\s*-\s*[12]$", "", region)
    region = re.sub(r"\s+[12]$", "", region)
    region = re.sub(r"\s+", " ", region).strip()

    replacements = {
        "Asa sul": "Plano Piloto",
        "Asa Sul": "Plano Piloto",
        "Arniqueiras": "Arniqueira",
        "Ceilandia": "Ceilândia",
        "Papa Entulho": "",
        "Papa Lixo": "",
        "Papa Reciclavel": "",
        "Riacho Fundo II Riacho Fundo II": "Riacho Fundo II",
        "SCIA": "SCIA/Estrutural",
        "São Sebastiâo": "São Sebastião",
        "Sobradinho I": "Sobradinho",
    }
    return replacements.get(region, region)


def lot_from_region(region: object) -> str:
    normalized = normalize_region_name(region)
    return REGION_TO_LOT.get(normalized, "")


def lot_from_category(category: object) -> str:
    normalized = normalize_region_name(category)
    if normalized in REGION_TO_LOT:
        return REGION_TO_LOT[normalized]

    category_text = "" if pd.isna(category) else str(category).strip()
    for lot in LOT_OPTIONS[1:]:
        if category_text.lower() == lot.lower():
            return lot
    return ""


def indicator_group(indicator: str) -> str:
    for group, indicators in TYPE_TO_INDICATORS.items():
        if indicator in indicators:
            return group
    return indicator


def is_pev_type(collection_type: str) -> bool:
    if collection_type == "Todas":
        return True
    return any(indicator in PEV_INDICATORS for indicator in TYPE_TO_INDICATORS.get(collection_type, []))
