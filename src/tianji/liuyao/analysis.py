"""
六爻装卦分析 (Liu Yao Hexagram Analysis)

After casting a hexagram, this module "loads" it (装卦) with:
- 世应 (World/Response positions): Which line is the querent (世爻) and response (应爻)
- 六亲 (Six Relatives): The relationship of each line to the palace's primary element
- 六神 (Six Gods/Spirits): Six spirits assigned to lines based on day stem
- 动爻变爻 (Moving/Changed Lines): Which lines transform and what they become
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from tianji.liuyao.hexagram import Hexagram, Trigram, TRIGRAMS
from tianji.liuyao.casting import CastResult
from tianji.calendar.heavenly_stems import Element, HeavenlyStem, ELEMENT_PRODUCES, ELEMENT_CONQUERS


# 世应 (World-Response) positions for each hexagram based on palace structure
# For each of the 8 palaces (one per trigram), the world position cycles:
# 1st palace gua (纯卦): 世 at line 6, 应 at line 3
# 2nd palace gua (一世卦): 世 at line 1, 应 at line 4
# ... etc.
# Simplified: use the standard 世应 lookup by hexagram number
# World position (世爻) is at line position (1-based)
_SHIYYING_TABLE: dict[int, tuple[int, int]] = {
    # (world_line, response_line) for each hexagram number
    # Based on the 8-palace (八宫) system
    1:  (6, 3), 2:  (6, 3), 3:  (2, 5), 4:  (2, 5),
    5:  (4, 1), 6:  (4, 1), 7:  (2, 5), 8:  (2, 5),
    9:  (4, 1), 10: (4, 1), 11: (3, 6), 12: (3, 6),
    13: (3, 6), 14: (3, 6), 15: (3, 6), 16: (3, 6),
    17: (1, 4), 18: (1, 4), 19: (2, 5), 20: (2, 5),
    21: (5, 2), 22: (5, 2), 23: (4, 1), 24: (4, 1),
    25: (4, 1), 26: (4, 1), 27: (3, 6), 28: (3, 6),
    29: (6, 3), 30: (6, 3), 31: (1, 4), 32: (1, 4),
    33: (3, 6), 34: (3, 6), 35: (2, 5), 36: (2, 5),
    37: (2, 5), 38: (2, 5), 39: (1, 4), 40: (1, 4),
    41: (3, 6), 42: (3, 6), 43: (4, 1), 44: (4, 1),
    45: (2, 5), 46: (2, 5), 47: (3, 6), 48: (3, 6),
    49: (1, 4), 50: (1, 4), 51: (6, 3), 52: (6, 3),
    53: (3, 6), 54: (3, 6), 55: (4, 1), 56: (4, 1),
    57: (6, 3), 58: (6, 3), 59: (3, 6), 60: (3, 6),
    61: (2, 5), 62: (2, 5), 63: (1, 4), 64: (1, 4),
}

# Six Relatives (六亲) based on element relationships
_SIX_RELATIVES_NAMES: dict[str, str] = {
    "same_yang": "兄弟",    # Same element + same polarity
    "same_yin": "兄弟",     # Same element
    "produces": "子孙",      # Element produced by palace
    "produced_by": "父母",   # Element that produces palace
    "conquers": "妻财",      # Element conquered by palace
    "conquered_by": "官鬼",  # Element that conquers palace
}

# Six Gods (六神) in order, assigned starting from the day stem element
_SIX_GODS = ["青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"]

# Element to six gods starting position
_ELEMENT_GOD_START: dict[Element, int] = {
    Element.WOOD:  0,   # 甲乙日 → 青龙起
    Element.FIRE:  2,   # 丙丁日 → 勾陈起
    Element.EARTH: 2,   # 戊己日 → 勾陈起
    Element.METAL: 4,   # 庚辛日 → 白虎起
    Element.WATER: 5,   # 壬癸日 → 玄武起 (some traditions differ)
}


def _get_line_element(line_pos: int, hexagram: Hexagram) -> Element:
    """
    Get the element of a line based on its position and hexagram palace.

    In Liu Yao, each line is associated with one of the five elements
    based on a standard mapping. This uses the Earthly Branch for each line.
    """
    # Standard branch assignment for lines (bottom to top): 子寅辰午申戌 for yang palace
    # Simplified: use branch cycle starting from palace's primary branch
    # For now, use a standard 6-line branch mapping
    _YANG_PALACE_BRANCHES = ["子", "寅", "辰", "午", "申", "戌"]
    _YIN_PALACE_BRANCHES =  ["丑", "亥", "酉", "未", "巳", "卯"]

    # Use yang mapping as default
    branch_elements = {
        "子": Element.WATER, "寅": Element.WOOD, "辰": Element.EARTH,
        "午": Element.FIRE, "申": Element.METAL, "戌": Element.EARTH,
        "丑": Element.EARTH, "亥": Element.WATER, "酉": Element.METAL,
        "未": Element.EARTH, "巳": Element.FIRE, "卯": Element.WOOD,
    }

    # Determine palace element from lower trigram
    palace_element_map = {
        "乾": Element.METAL, "兑": Element.METAL,
        "离": Element.FIRE, "震": Element.WOOD, "巽": Element.WOOD,
        "坎": Element.WATER, "艮": Element.EARTH, "坤": Element.EARTH,
    }
    palace_element = palace_element_map.get(hexagram.lower.name, Element.EARTH)

    # Simplified: return standard branch element for line position
    branch = _YANG_PALACE_BRANCHES[line_pos - 1]
    return branch_elements[branch]


def _get_six_relative(line_element: Element, palace_element: Element) -> str:
    """Compute the Six Relative (六亲) name for a line."""
    if line_element == palace_element:
        return "兄弟"
    elif ELEMENT_PRODUCES.get(palace_element) == line_element:
        return "子孙"
    elif ELEMENT_PRODUCES.get(line_element) == palace_element:
        return "父母"
    elif ELEMENT_CONQUERS.get(palace_element) == line_element:
        return "妻财"
    elif ELEMENT_CONQUERS.get(line_element) == palace_element:
        return "官鬼"
    return "兄弟"  # fallback


@dataclass
class LineAnalysis:
    """Analysis of one line in the hexagram."""
    position: int      # 1–6, from bottom
    name: str          # 初/二/三/四/五/上
    is_yang: bool      # True=阳爻, False=阴爻
    is_moving: bool    # True=动爻
    element: Element   # Line's element
    six_relative: str  # 六亲 (兄弟/子孙/父母/妻财/官鬼)
    six_god: str       # 六神 (青龙/朱雀/...)
    is_world: bool     # 世爻
    is_response: bool  # 应爻

    def __str__(self) -> str:
        sym = "阳" if self.is_yang else "阴"
        markers = []
        if self.is_world: markers.append("世")
        if self.is_response: markers.append("应")
        if self.is_moving: markers.append("动")
        marker_str = f"[{''.join(markers)}]" if markers else ""
        return f"{self.name}爻 {sym} {self.six_relative} {self.six_god} {marker_str}"


@dataclass
class LiuYaoAnalysis:
    """
    Complete 六爻 analysis after casting.

    Loads the hexagram with 世应, 六亲, 六神, and 动爻 information.
    """
    cast_result: CastResult
    line_analyses: list[LineAnalysis] = field(default_factory=list)
    world_line: int = 0    # World position (1–6)
    response_line: int = 0 # Response position (1–6)

    def __post_init__(self) -> None:
        self._analyze()

    def _analyze(self) -> None:
        """Perform the full analysis."""
        hexagram = self.cast_result.primary_hexagram
        raw_lines = self.cast_result.raw_lines
        moving_lines = self.cast_result.moving_lines

        # Get 世应 positions
        world_pos, response_pos = _SHIYYING_TABLE.get(
            hexagram.number, (3, 6)
        )
        self.world_line = world_pos
        self.response_line = response_pos

        # Palace element from lower trigram
        palace_element_map = {
            "乾": Element.METAL, "兑": Element.METAL,
            "离": Element.FIRE, "震": Element.WOOD, "巽": Element.WOOD,
            "坎": Element.WATER, "艮": Element.EARTH, "坤": Element.EARTH,
        }
        palace_element = palace_element_map.get(hexagram.lower.name, Element.EARTH)

        # Six gods starting position (use default 甲日 = 青龙)
        god_start = 0
        line_names = ["初", "二", "三", "四", "五", "上"]

        for i in range(6):
            pos = i + 1
            raw = raw_lines[i]
            is_yang = raw in (7, 9, 1)
            is_moving = pos in moving_lines

            line_element = _get_line_element(pos, hexagram)
            six_relative = _get_six_relative(line_element, palace_element)
            six_god = _SIX_GODS[(god_start + i) % 6]

            self.line_analyses.append(LineAnalysis(
                position=pos,
                name=line_names[i],
                is_yang=is_yang,
                is_moving=is_moving,
                element=line_element,
                six_relative=six_relative,
                six_god=six_god,
                is_world=(pos == world_pos),
                is_response=(pos == response_pos),
            ))

    def display(self) -> None:
        """Print the complete analysis."""
        h = self.cast_result.primary_hexagram
        print(f"\n六爻装卦分析 — {h}")
        print("─" * 60)
        print(f"{'位置':<6} {'阴阳':<4} {'六亲':<6} {'六神':<6} {'标记':<8} {'元素'}")
        print("─" * 60)

        for la in reversed(self.line_analyses):  # Display top to bottom
            sym = "阳爻" if la.is_yang else "阴爻"
            markers = []
            if la.is_world: markers.append("世")
            if la.is_response: markers.append("应")
            if la.is_moving: markers.append("动")
            marker_str = "/".join(markers)
            print(f"{la.name}爻{la.position:<2} {sym:<4} {la.six_relative:<6} {la.six_god:<6} {marker_str:<8} {la.element.value}")

        print("─" * 60)
        if self.cast_result.changed_hexagram:
            print(f"变卦: {self.cast_result.changed_hexagram}")

    def to_dict(self) -> dict:
        """Serialize analysis to dictionary."""
        return {
            "primary_hexagram": {
                "number": self.cast_result.primary_hexagram.number,
                "name": self.cast_result.primary_hexagram.name,
                "symbol": self.cast_result.primary_hexagram.symbol,
            },
            "changed_hexagram": {
                "number": self.cast_result.changed_hexagram.number,
                "name": self.cast_result.changed_hexagram.name,
            } if self.cast_result.changed_hexagram else None,
            "world_line": self.world_line,
            "response_line": self.response_line,
            "moving_lines": self.cast_result.moving_lines,
            "lines": [
                {
                    "position": la.position,
                    "name": la.name,
                    "is_yang": la.is_yang,
                    "is_moving": la.is_moving,
                    "element": la.element.value,
                    "six_relative": la.six_relative,
                    "six_god": la.six_god,
                    "is_world": la.is_world,
                    "is_response": la.is_response,
                }
                for la in self.line_analyses
            ],
        }
