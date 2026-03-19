"""
tianji.bazi — 八字 (BaZi / Four Pillars of Destiny)

BaZi (八字, Eight Characters) is a Chinese astrological system that uses four pillars
(year, month, day, hour) each consisting of one Heavenly Stem and one Earthly Branch.
"""

from tianji.bazi.chart import BaZiChart, compute_year_pillar, compute_month_pillar, compute_day_pillar, compute_hour_pillar
from tianji.bazi.ten_gods import TenGodResult, compute_ten_god, compute_all_ten_gods, ten_gods_from_chart, display_ten_gods
from tianji.bazi.five_elements import FiveElementsAnalysis, analyze_five_elements, elements_from_chart
from tianji.bazi.day_master import DayMasterStrength, StrengthLevel, analyze_day_master_strength
from tianji.bazi.luck_pillars import LuckPillar, LuckPillarsResult, compute_luck_pillars
from tianji.bazi.relationships import BranchRelationship, RelationshipsAnalysis, analyze_relationships, relationships_from_chart

__all__ = [
    "BaZiChart",
    "compute_year_pillar", "compute_month_pillar", "compute_day_pillar", "compute_hour_pillar",
    "TenGodResult", "compute_ten_god", "compute_all_ten_gods", "ten_gods_from_chart", "display_ten_gods",
    "FiveElementsAnalysis", "analyze_five_elements", "elements_from_chart",
    "DayMasterStrength", "StrengthLevel", "analyze_day_master_strength",
    "LuckPillar", "LuckPillarsResult", "compute_luck_pillars",
    "BranchRelationship", "RelationshipsAnalysis", "analyze_relationships", "relationships_from_chart",
]
