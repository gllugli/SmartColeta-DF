from __future__ import annotations

import os
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
APP_DIR = PACKAGE_DIR.parent
DELIVERY_DIR = APP_DIR.parent
PROJECT_ROOT = DELIVERY_DIR.parent.parent
STATIC_DIR = PROJECT_ROOT / "public" / "static"
DEFAULT_DATA_PATH = PROJECT_ROOT / "docs" / "Entrega_3" / "Base_dados_SMART_tratada.xlsx"
DATA_PATH = Path(os.environ.get("SMARTCOLETA_DATA_PATH", DEFAULT_DATA_PATH)).expanduser()

MONTHS = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

MONTHS_SHORT = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}

TYPE_TO_INDICATORS = {
    "Domiciliar": ["Coleta Domiciliar (t)"],
    "Seletiva": [
        "Coleta Seletiva - resíduo seletivo (t)",
        "Coleta Seletiva - Rejeitos IRR (t)",
    ],
    "RCC PEV": ["Coleta RCC PEV (t)"],
    "Podas PEV": ["Coleta Podas PEV (t)"],
    "Volumosos PEV": ["Coleta Volumosos PEV (t)"],
    "Entulho Manual": ["Entulho Manual (t)"],
    "Entulho Mecanizado": ["Entulho Mecanizado (t)"],
}

COST_LOT_BY_INDICATOR = {
    "LOTE I (R$)": "Lote I",
    "LOTE II (R$)": "Lote II",
    "LOTE III (R$)": "Lote III",
}

MONTHLY_COST_TYPE_BY_CATEGORY = {
    "Coleta Seletiva": "Seletiva",
    "Coleta convencional de RSU": "Domiciliar",
    "Coleta manual de entulhos": "Entulho Manual",
    "Coleta mecanizada de entulhos": "Entulho Mecanizado",
}

PEV_COST_TYPE_BY_CATEGORY = {
    "Coleta e transporte mecanizado de entulho": "RCC PEV",
    "Coleta e transporte manual de podas": "Podas PEV",
    "Coleta e Transporte manual de Resíduos Volumosos": "Volumosos PEV",
}

PEV_INDICATORS = {
    "Coleta RCC PEV (t)",
    "Coleta Podas PEV (t)",
    "Coleta Volumosos PEV (t)",
}

LOT_REGIONS = {
    "Lote I": [
        "Arapoanga",
        "Cruzeiro",
        "Fercal",
        "Itapoã",
        "Lago Norte",
        "Paranoá",
        "Planaltina",
        "Plano Piloto",
        "Sobradinho",
        "Sobradinho II",
        "Sudoeste/Octogonal",
        "São Sebastião",
        "Varjão",
    ],
    "Lote II": [
        "Taguatinga",
        "Brazlândia",
        "Ceilândia",
        "Pôr do Sol",
        "Sol Nascente",
        "Sol Nascente/Pôr do Sol",
        "Samambaia",
    ],
    "Lote III": [
        "Guará",
        "SCIA/Estrutural",
        "SIA",
        "Águas Claras",
        "Vicente Pires",
        "Água Quente",
        "Arniqueira",
        "Candangolândia",
        "Gama",
        "Jardim Botânico",
        "Lago Sul",
        "Núcleo Bandeirante",
        "Park Way",
        "Recanto das Emas",
        "Riacho Fundo",
        "Riacho Fundo II",
        "Santa Maria",
    ],
}

TOOLTIP_LOT_REGIONS = {
    "Lote I": [
        "Arapoanga",
        "Cruzeiro",
        "Fercal",
        "Itapoã",
        "Lago Norte",
        "Paranoá",
        "Planaltina",
        "Plano Piloto",
        "Sobradinho",
        "Sobradinho II",
        "Sudoeste/Octogonal",
        "São Sebastião",
        "Varjão",
    ],
    "Lote II": [
        "Taguatinga",
        "Brazlândia",
        "Ceilândia",
        "Pôr do Sol",
        "Sol Nascente",
        "Samambaia",
    ],
    "Lote III": [
        "Guará",
        "SCIA",
        "Estrutural",
        "SIA",
        "Águas Claras",
        "Vicente Pires",
        "Água Quente",
        "Arniqueira",
        "Candangolândia",
        "Gama",
        "Jardim Botânico",
        "Lago Sul",
        "Núcleo Bandeirante",
        "Park Way",
        "Recanto das Emas",
        "Riacho Fundo",
        "Riacho Fundo II",
        "Santa Maria",
    ],
}

REGION_TO_LOT = {
    region: lot
    for lot, regions in LOT_REGIONS.items()
    for region in regions
}

LOT_OPTIONS = ["Todos", "Lote I", "Lote II", "Lote III"]
