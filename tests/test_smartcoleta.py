from __future__ import annotations

import unittest
from urllib.parse import parse_qs

from smartcoleta.config import DATA_PATH, REGION_TO_LOT
from smartcoleta.data_loader import get_source_data
from smartcoleta.domain import indicator_group, lot_from_region, normalize_region_name
from smartcoleta.filters import parse_selection
from smartcoleta.templates import render_dashboard


class SmartColetaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = get_source_data()

    def test_data_file_exists_and_has_expected_contract(self) -> None:
        self.assertTrue(DATA_PATH.exists())
        self.assertGreater(len(self.source.monthly), 0)
        self.assertGreater(len(self.source.years), 0)
        self.assertIn("valor", self.source.monthly.columns)
        self.assertIn("regiao", self.source.regional_volume.columns)
        self.assertIn("tipo_equipamento", self.source.equipment.columns)

    def test_domain_normalization_and_indicator_groups(self) -> None:
        self.assertEqual(normalize_region_name("Ceilandia"), "Ceilândia")
        self.assertEqual(lot_from_region("Taguatinga"), "Lote II")
        self.assertEqual(indicator_group("Coleta RCC PEV (t)"), "RCC PEV")
        self.assertEqual(indicator_group("Indicador experimental"), "Indicador experimental")

    def test_parse_selection_accepts_region_when_it_matches_lot(self) -> None:
        region = "Taguatinga"
        lot = REGION_TO_LOT[region]
        selection = parse_selection({"lote": [lot], "regiao": [region], "tipo": ["Domiciliar"]}, self.source)

        self.assertEqual(selection.lot, lot)
        self.assertEqual(selection.region, region)
        self.assertEqual(selection.collection_type, "Domiciliar")

    def test_parse_selection_resets_region_when_it_conflicts_with_lot(self) -> None:
        selection = parse_selection({"lote": ["Lote I"], "regiao": ["Taguatinga"]}, self.source)

        self.assertEqual(selection.lot, "Lote I")
        self.assertEqual(selection.region, "Todas")

    def test_render_dashboard_with_region_filter(self) -> None:
        html = render_dashboard(parse_qs("lote=Lote%20II&regiao=Taguatinga&tipo=Domiciliar"))

        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn('name="regiao"', html)
        self.assertIn("Taguatinga", html)
        self.assertIn("SmartColeta - DF", html)


if __name__ == "__main__":
    unittest.main()
