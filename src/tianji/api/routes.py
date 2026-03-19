"""API routes for Tianji."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from tianji.bazi.chart import create_chart
from tianji.bazi.ten_gods import compute_ten_gods
from tianji.bazi.five_elements import analyze_five_elements
from tianji.liuyao.casting import cast_by_time, cast_by_numbers
from tianji.liuyao.analysis import full_analysis

router = APIRouter(prefix="/api/v1", tags=["tianji"])


# --- Request/Response Models ---

class BaZiRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="出生年份")
    month: int = Field(..., ge=1, le=12, description="出生月份")
    day: int = Field(..., ge=1, le=31, description="出生日期")
    hour: int = Field(..., ge=0, le=23, description="出生时辰 (24小时制)")
    gender: str = Field("男", description="性别: 男/女")


class LiuYaoRequest(BaseModel):
    numbers: Optional[list[int]] = Field(None, description="6个数字起卦 (可选)")
    question: str = Field("综合运势", description="所问事项")


class ZiWeiRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    lunar_month: int = Field(..., ge=1, le=12, description="农历月份")
    lunar_day: int = Field(..., ge=1, le=30, description="农历日期")
    hour: int = Field(..., ge=0, le=23)
    gender: str = Field("男")


# --- Routes ---

@router.post("/bazi/chart")
async def bazi_chart(req: BaZiRequest):
    """排八字命盘 — Calculate BaZi chart."""
    try:
        chart = create_chart(req.year, req.month, req.day, req.hour, req.gender)
        gods = compute_ten_gods(chart)
        elements = analyze_five_elements(chart)
        return {
            "status": "ok",
            "birth": {
                "year": req.year,
                "month": req.month,
                "day": req.day,
                "hour": req.hour,
                "gender": req.gender,
            },
            "pillars": {
                "year": str(chart.year_pillar),
                "month": str(chart.month_pillar),
                "day": str(chart.day_pillar),
                "hour": str(chart.hour_pillar),
            },
            "day_master": str(chart.day_pillar.stem),
            "ten_gods": gods,
            "five_elements": elements,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/liuyao/cast")
async def liuyao_cast(req: LiuYaoRequest):
    """六爻起卦 — Cast Liu Yao hexagram."""
    try:
        if req.numbers:
            if len(req.numbers) != 6:
                raise ValueError("需要恰好6个数字")
            result = cast_by_numbers(req.numbers)
        else:
            result = cast_by_time(datetime.now())

        analysis_result = full_analysis(result)
        return {
            "status": "ok",
            "question": req.question,
            **analysis_result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ziwei/chart")
async def ziwei_chart(req: ZiWeiRequest):
    """排紫微斗数命盘 — Calculate Zi Wei Dou Shu chart."""
    try:
        from tianji.ziwei.chart import create_ziwei_chart
        chart = create_ziwei_chart(
            req.year, req.lunar_month, req.lunar_day, req.hour, req.gender
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
                "lunar_day": req.lunar_day,
                "hour": req.hour,
                "gender": req.gender,
            },
            "palaces": palaces_data,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
