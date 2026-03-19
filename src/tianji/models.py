"""
Shared Pydantic models for tianji.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


class BirthInfo(BaseModel):
    """Birth information for chart calculation."""
    birth_datetime: datetime = Field(..., description="Birth datetime")
    gender: str = Field(default="male", description="Gender: 'male' or 'female'")
    name: Optional[str] = Field(default=None, description="Optional name")
    location: Optional[str] = Field(default=None, description="Optional birth location")


class PillarModel(BaseModel):
    """Represents a single pillar (stem + branch)."""
    stem: str = Field(..., description="Heavenly stem character")
    branch: str = Field(..., description="Earthly branch character")
    combined: str = Field(..., description="Combined stem-branch string")
    element: str = Field(..., description="Stem's element")
    polarity: str = Field(..., description="Stem's polarity (阴/阳)")


class BaZiChartModel(BaseModel):
    """Serialized BaZi chart."""
    birth_datetime: str
    gender: str
    year_pillar: PillarModel
    month_pillar: PillarModel
    day_pillar: PillarModel
    hour_pillar: PillarModel
    day_master: dict


class HexagramModel(BaseModel):
    """Serialized hexagram info."""
    number: int
    name: str
    symbol: Optional[str] = None


class LiuYaoResultModel(BaseModel):
    """Serialized Liu Yao analysis."""
    primary_hexagram: HexagramModel
    changed_hexagram: Optional[HexagramModel] = None
    world_line: int
    response_line: int
    moving_lines: list[int]
    lines: list[dict]


class ZiWeiChartModel(BaseModel):
    """Serialized Zi Wei chart."""
    birth_date: str
    birth_hour: int
    gender: str
    lunar_date: dict
    life_palace_branch: str
    wu_xing_ju: int
    palaces: list[dict]
    star_placements: dict[str, str]
