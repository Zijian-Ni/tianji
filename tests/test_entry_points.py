"""Exercise documented entry points that the engine unit tests cannot reach."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from tianji import __version__
from tianji.api.app import app
from tianji.bazi import BaZiChart
from tianji.liuyao import LiuYaoAnalysis, cast_hexagram
from tianji.llm import interpreter


client = TestClient(app)


def test_bazi_api():
    assert client.get("/health").json()["version"] == __version__
    birth = dict(year=2025, month=2, day=3, hour=22, minute=10)
    data = client.post("/api/v1/bazi/chart", json=birth).json()
    assert data["pillars"] == {"year": "乙巳", "month": "戊寅", "day": "癸卯", "hour": "癸亥"}
    assert data["ten_gods"]["月干"]["ten_god"] == "正官"
    assert data["five_elements"]["weighted_scores"]["木"] > 0
    assert client.post("/api/v1/bazi/chart", json={**birth, "day": 30}).status_code == 400


@pytest.mark.parametrize("inputs", [[2, 3, 1], [9, 8, 7, 7, 7, 8]])
def test_liuyao_api(inputs):
    data = client.post("/api/v1/liuyao/cast", json={"numbers": inputs}).json()
    assert data["primary_hexagram"]["number"] == 49 and data["changed_hexagram"]["number"] == 31


def test_api_lunar_palace():
    data = client.post("/api/v1/ziwei/chart", json={"year": 1990, "lunar_month": 4, "lunar_day": 21, "hour": 14}).json()
    assert "紫微" in data["palaces"]["命宫"]["stars"]
    assert data["body_branch"] == "子" and data["wu_xing_ju"] == 5


def test_leap_month_input():
    birth = {"year": 2025, "lunar_month": 6, "lunar_day": 29, "hour": 14, "is_leap": True}
    assert client.post("/api/v1/ziwei/chart", json=birth).json()["birth"]["is_leap"]
    assert client.post("/api/v1/ziwei/chart", json={**birth, "lunar_day": 30}).status_code == 400


def test_interpretations_use_chart_data_without_a_provider(monkeypatch):
    monkeypatch.setattr(interpreter, "_call_llm", lambda system, user, config: user)
    text = interpreter.interpret_bazi(BaZiChart(datetime(2025, 2, 3, 22, 10)))
    assert "乙巳" in text and "戊寅" in text
    cast = cast_hexagram("number", num1=2, num2=3, num3=1)
    text = interpreter.interpret_liuyao(LiuYaoAnalysis(cast).to_dict())
    assert "革" in text and "咸" in text
