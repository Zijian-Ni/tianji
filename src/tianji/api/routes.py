"""API routes for Tianji."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from tianji.bazi.chart import create_chart
from tianji.bazi.five_elements import elements_from_chart
from tianji.bazi.ten_gods import ten_gods_from_chart
from tianji.liuyao.analysis import LiuYaoAnalysis
from tianji.liuyao.casting import cast_by_numbers, cast_by_time, cast_from_lines

router = APIRouter(prefix="/api/v1", tags=["tianji"])


# --- Request/Response Models ---

class BaZiRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="出生年份")
    month: int = Field(..., ge=1, le=12, description="出生月份")
    day: int = Field(..., ge=1, le=31, description="出生日期")
    hour: int = Field(..., ge=0, le=23, description="出生时辰 (24小时制)")
    minute: int = Field(0, ge=0, le=59)
    gender: str = Field("男", description="性别: 男/女")


class LiuYaoRequest(BaseModel):
    numbers: Optional[list[int]] = Field(None, description="2–3个报数，或6个从初爻至上爻的铜钱值（6–9）")
    dt: datetime | None = Field(None, description="时间起卦的北京时间")
    question: str = Field("综合运势", description="所问事项")


class ZiWeiRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    lunar_month: int = Field(..., ge=1, le=12, description="农历月份")
    lunar_day: int = Field(..., ge=1, le=30, description="农历日期")
    hour: int = Field(..., ge=0, le=23)
    gender: str = Field("男")
    is_leap: bool = False


# --- Routes ---

@router.post("/bazi/chart")
async def bazi_chart(req: BaZiRequest):
    """排八字命盘 — Calculate BaZi chart."""
    try:
        chart = create_chart(req.year, req.month, req.day, req.hour, req.gender, req.minute)
        gods = ten_gods_from_chart(chart)
        elements = elements_from_chart(chart)
        return {
            "status": "ok",
            "birth": {
                "year": req.year,
                "month": req.month,
                "day": req.day,
                "hour": req.hour,
                "gender": req.gender,
                "minute": req.minute,
            },
            "pillars": {
                "year": str(chart.year_pillar),
                "month": str(chart.month_pillar),
                "day": str(chart.day_pillar),
                "hour": str(chart.hour_pillar),
            },
            "day_master": chart.day_master.char,
            "ten_gods": gods,
            "five_elements": {
                "weighted_scores": dict(elements.weighted_scores),
                "stem_counts": dict(elements.stem_counts),
                "branch_counts": dict(elements.branch_counts),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/liuyao/cast")
async def liuyao_cast(req: LiuYaoRequest):
    """六爻起卦 — Cast Liu Yao hexagram."""
    try:
        if req.numbers is None:
            result = cast_by_time(req.dt)
        elif len(req.numbers) in (2, 3):
            result = cast_by_numbers(*req.numbers)
        elif len(req.numbers) == 6:
            result = cast_from_lines(req.numbers)
        else:
            raise ValueError("请输入两个或三个报数，或六个铜钱爻值")
        analysis_result = LiuYaoAnalysis(result).to_dict()
        return {
            "status": "ok",
            "question": req.question,
            **analysis_result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ziwei/chart")
async def ziwei_chart(req: ZiWeiRequest):
    """排紫微斗数命盘 — Calculate Zi Wei Dou Shu chart."""
    try:
        from tianji.ziwei.chart import create_ziwei_chart
        chart = create_ziwei_chart(
            req.year, req.lunar_month, req.lunar_day, req.hour, req.gender, is_leap=req.is_leap
        )
        palaces_data = {}
        for name, palace in chart.palaces.items():
            palaces_data[name] = {
                "branch": palace.branch,
                "stars": palace.stars,
            }
        return {
            "status": "ok",
            "birth": {
                "year": req.year,
                "lunar_month": req.lunar_month,
                "is_leap": req.is_leap,
                "lunar_day": req.lunar_day,
                "hour": req.hour,
                "gender": req.gender,
            },
            "body_branch": chart.body_branch,
            "wu_xing_ju": chart.wu_xing_ju,
            "palaces": palaces_data,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
