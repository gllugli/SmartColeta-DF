from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SourceData:
    monthly: pd.DataFrame
    regional_volume: pd.DataFrame
    costs: pd.DataFrame
    equipment: pd.DataFrame
    population: pd.DataFrame
    years: list[int]
    regions: list[str]


@dataclass(frozen=True)
class Selection:
    year: int | None
    month: int | None
    lot: str
    region: str
    collection_type: str


MetricDetailRow = tuple[str, int | None, int]
MetricDetails = tuple[str, list[MetricDetailRow], str]
Metric = tuple[str, str, str, str, MetricDetails | None]
ChartTooltip = tuple[str, list[str]]


@dataclass(frozen=True)
class DashboardModel:
    source: SourceData
    selection: Selection
    metrics: list[Metric]
    volume_chart_title: str
    volume_chart_data: list[tuple[str, float]]
    volume_chart_tooltips: dict[str, ChartTooltip]
    monthly_chart_title: str
    monthly_volume: list[tuple[str, float]]
    cost_chart_title: str
    cost_chart_data: list[tuple[str, float]]
    collection_breakdown: list[tuple[str, float]]
    ranking_title: str
    ranking_context: str
    ranking: list[tuple[str, float]]
    summary: list[tuple[str, str]]
    period_label: str
