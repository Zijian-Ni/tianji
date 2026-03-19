"""
六十四卦 (64 Hexagrams) definitions.

The 64 hexagrams of the I Ching (易经) are composed of pairs of trigrams (八卦).
Each hexagram has a name, Unicode symbol, and trigram composition.

Trigram encoding (lines from bottom to top, 1=yang/solid, 0=yin/broken):
☰ 乾 (Heaven):  111 = 7
☱ 兑 (Lake):    110 = 6
☲ 离 (Fire):    101 = 5
☳ 震 (Thunder): 100 = 4
☴ 巽 (Wind):    011 = 3
☵ 坎 (Water):   010 = 2
☶ 艮 (Mountain):001 = 1
☷ 坤 (Earth):   000 = 0
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Trigram:
    """八卦 (Trigram) — composed of 3 lines."""
    name: str        # Chinese name (e.g. 乾)
    symbol: str      # Unicode symbol (e.g. ☰)
    lines: int       # 3-bit integer: bit 2=top, bit 1=mid, bit 0=bottom (1=yang)
    element: str     # Associated element/attribute
    nature: str      # Nature/image

    @property
    def line_list(self) -> list[int]:
        """Return lines as list [bottom, middle, top], 1=yang, 0=yin."""
        return [(self.lines >> i) & 1 for i in range(3)]

    def __str__(self) -> str:
        return f"{self.symbol}{self.name}"


# Eight Trigrams (八卦) — ordered by binary value
TRIGRAMS: dict[int, Trigram] = {
    7: Trigram("乾", "☰", 7, "金", "天"),
    6: Trigram("兑", "☱", 6, "金", "泽"),
    5: Trigram("离", "☲", 5, "火", "火"),
    4: Trigram("震", "☳", 4, "木", "雷"),
    3: Trigram("巽", "☴", 3, "木", "风"),
    2: Trigram("坎", "☵", 2, "水", "水"),
    1: Trigram("艮", "☶", 1, "土", "山"),
    0: Trigram("坤", "☷", 0, "土", "地"),
}

# Lookup by name
TRIGRAM_BY_NAME: dict[str, Trigram] = {t.name: t for t in TRIGRAMS.values()}
TRIGRAM_BY_SYMBOL: dict[str, Trigram] = {t.symbol: t for t in TRIGRAMS.values()}


@dataclass(frozen=True)
class Hexagram:
    """
    一个卦象 (Hexagram) — composed of upper and lower trigrams.

    The hexagram number follows the King Wen (文王) sequence.
    Lines are numbered 1 (bottom/初) to 6 (top/上).
    """
    number: int        # King Wen sequence number (1–64)
    name: str          # Chinese name
    symbol: str        # Unicode hexagram symbol (U+4DC0–U+4DFF)
    upper: Trigram     # 上卦 (outer trigram)
    lower: Trigram     # 下卦 (inner trigram)
    description: str   # Brief meaning

    @property
    def lines(self) -> list[int]:
        """
        Return all 6 lines from bottom to top.
        1 = Yang (solid —), 0 = Yin (broken - -)
        """
        lower_lines = self.lower.line_list   # bottom 3
        upper_lines = self.upper.line_list   # top 3
        return lower_lines + upper_lines

    def __str__(self) -> str:
        return f"{self.symbol} {self.name} (第{self.number}卦)"

    def display(self) -> None:
        """Print hexagram in traditional top-to-bottom format."""
        print(f"\n{self} — {self.upper.name}上{self.lower.name}下")
        print(f"  上卦: {self.upper}")
        print(f"  下卦: {self.lower}")
        lines = self.lines
        line_names = ["初", "二", "三", "四", "五", "上"]
        polarity_names = ["", "六", "九"]  # 0=placeholder, yin=六, yang=九
        for i in range(5, -1, -1):
            line = lines[i]
            sym = "⚊" if line == 1 else "⚋"
            pol = "九" if line == 1 else "六"
            print(f"  {line_names[i]}{pol}: {sym} {'阳爻' if line == 1 else '阴爻'}")
        print(f"  释义: {self.description}")


def _build_hexagram_lookup() -> dict[tuple[int, int], Hexagram]:
    """Build lookup from (upper_trigram_code, lower_trigram_code) → Hexagram."""
    return {(h.upper.lines, h.lower.lines): h for h in ALL_HEXAGRAMS}


# The 64 hexagrams in King Wen sequence
# Format: (number, name, symbol, upper_code, lower_code, description)
# Unicode hexagram symbols: U+4DC0 (䷀ 乾) to U+4DFF (䷿ 未济)
_HEXAGRAM_DATA: list[tuple[int, str, str, int, int, str]] = [
    (1,  "乾",  "䷀", 7, 7, "天行健，君子以自强不息"),
    (2,  "坤",  "䷁", 0, 0, "地势坤，君子以厚德载物"),
    (3,  "屯",  "䷂", 2, 4, "刚柔始交而难生，动乎险中"),
    (4,  "蒙",  "䷃", 1, 2, "山下有险，险而止，蒙"),
    (5,  "需",  "䷄", 2, 7, "需，有孚，光亨，贞吉"),
    (6,  "讼",  "䷅", 7, 2, "天与水违行，讼"),
    (7,  "师",  "䷆", 0, 2, "地中有水，师"),
    (8,  "比",  "䷇", 2, 0, "地上有水，比"),
    (9,  "小畜", "䷈", 3, 7, "风行天上，小畜"),
    (10, "履",  "䷉", 7, 6, "上天下泽，履"),
    (11, "泰",  "䷊", 0, 7, "天地交，泰"),
    (12, "否",  "䷋", 7, 0, "天地不交，否"),
    (13, "同人", "䷌", 7, 5, "天与火，同人"),
    (14, "大有", "䷍", 5, 7, "火在天上，大有"),
    (15, "谦",  "䷎", 0, 1, "地中有山，谦"),
    (16, "豫",  "䷏", 4, 0, "雷出地奋，豫"),
    (17, "随",  "䷐", 6, 4, "泽中有雷，随"),
    (18, "蛊",  "䷑", 1, 3, "山下有风，蛊"),
    (19, "临",  "䷒", 0, 6, "泽上有地，临"),
    (20, "观",  "䷓", 3, 0, "风行地上，观"),
    (21, "噬嗑", "䷔", 5, 4, "雷电，噬嗑"),
    (22, "贲",  "䷕", 1, 5, "山下有火，贲"),
    (23, "剥",  "䷖", 1, 0, "山附于地，剥"),
    (24, "复",  "䷗", 0, 4, "雷在地中，复"),
    (25, "无妄", "䷘", 7, 4, "天下雷行，无妄"),
    (26, "大畜", "䷙", 1, 7, "天在山中，大畜"),
    (27, "颐",  "䷚", 1, 4, "山下有雷，颐"),
    (28, "大过", "䷛", 6, 3, "泽灭木，大过"),
    (29, "坎",  "䷜", 2, 2, "水洊至，习坎"),
    (30, "离",  "䷝", 5, 5, "明两作，离"),
    (31, "咸",  "䷞", 6, 1, "山上有泽，咸"),
    (32, "恒",  "䷟", 4, 3, "雷风，恒"),
    (33, "遁",  "䷠", 7, 1, "天下有山，遁"),
    (34, "大壮", "䷡", 4, 7, "雷在天上，大壮"),
    (35, "晋",  "䷢", 5, 0, "明出地上，晋"),
    (36, "明夷", "䷣", 0, 5, "明入地中，明夷"),
    (37, "家人", "䷤", 3, 5, "风自火出，家人"),
    (38, "睽",  "䷥", 5, 6, "上火下泽，睽"),
    (39, "蹇",  "䷦", 2, 1, "山上有水，蹇"),
    (40, "解",  "䷧", 4, 2, "雷雨作，解"),
    (41, "损",  "䷨", 1, 6, "山下有泽，损"),
    (42, "益",  "䷩", 3, 4, "风雷，益"),
    (43, "夬",  "䷪", 6, 7, "泽上于天，夬"),
    (44, "姤",  "䷫", 7, 3, "天下有风，姤"),
    (45, "萃",  "䷬", 6, 0, "泽上于地，萃"),
    (46, "升",  "䷭", 0, 3, "地中生木，升"),
    (47, "困",  "䷮", 6, 2, "泽无水，困"),
    (48, "井",  "䷯", 2, 3, "木上有水，井"),
    (49, "革",  "䷰", 6, 5, "泽中有火，革"),
    (50, "鼎",  "䷱", 5, 3, "木上有火，鼎"),
    (51, "震",  "䷲", 4, 4, "洊雷，震"),
    (52, "艮",  "䷳", 1, 1, "兼山，艮"),
    (53, "渐",  "䷴", 3, 1, "山上有木，渐"),
    (54, "归妹", "䷵", 4, 6, "泽上有雷，归妹"),
    (55, "丰",  "䷶", 4, 5, "雷电皆至，丰"),
    (56, "旅",  "䷷", 5, 1, "山上有火，旅"),
    (57, "巽",  "䷸", 3, 3, "随风，巽"),
    (58, "兑",  "䷹", 6, 6, "丽泽，兑"),
    (59, "涣",  "䷺", 3, 2, "风行水上，涣"),
    (60, "节",  "䷻", 2, 6, "泽上有水，节"),
    (61, "中孚", "䷼", 3, 6, "泽上有风，中孚"),
    (62, "小过", "䷽", 4, 1, "山上有雷，小过"),
    (63, "既济", "䷾", 2, 5, "水在火上，既济"),
    (64, "未济", "䷿", 5, 2, "火在水上，未济"),
]


def _build_hexagrams() -> tuple[Hexagram, ...]:
    """Build all 64 hexagrams from the data table."""
    hexagrams = []
    for num, name, symbol, upper_code, lower_code, desc in _HEXAGRAM_DATA:
        upper = TRIGRAMS[upper_code]
        lower = TRIGRAMS[lower_code]
        hexagrams.append(Hexagram(
            number=num,
            name=name,
            symbol=symbol,
            upper=upper,
            lower=lower,
            description=desc,
        ))
    return tuple(hexagrams)


ALL_HEXAGRAMS: tuple[Hexagram, ...] = _build_hexagrams()

# Lookup by number
HEXAGRAM_BY_NUMBER: dict[int, Hexagram] = {h.number: h for h in ALL_HEXAGRAMS}

# Lookup by trigram pair
HEXAGRAM_BY_TRIGRAMS: dict[tuple[int, int], Hexagram] = _build_hexagram_lookup()


def get_hexagram_by_number(num: int) -> Hexagram:
    """Get a hexagram by its King Wen number (1–64)."""
    if num not in HEXAGRAM_BY_NUMBER:
        raise ValueError(f"Hexagram number must be 1–64, got {num}")
    return HEXAGRAM_BY_NUMBER[num]


def get_hexagram_by_trigrams(upper: int, lower: int) -> Hexagram:
    """Get a hexagram by upper and lower trigram codes (0–7)."""
    key = (upper, lower)
    if key not in HEXAGRAM_BY_TRIGRAMS:
        raise ValueError(f"No hexagram found for upper={upper}, lower={lower}")
    return HEXAGRAM_BY_TRIGRAMS[key]


def lines_to_hexagram(lines: list[int]) -> Hexagram:
    """
    Convert 6 line values to a hexagram.

    Args:
        lines: List of 6 integers [bottom, ..., top], 1=yang, 0=yin
               (moving lines: 6=old yin, 7=old yang are also accepted)

    Returns:
        The corresponding Hexagram
    """
    if len(lines) != 6:
        raise ValueError(f"Expected 6 lines, got {len(lines)}")

    # Normalize: 6/8 → 0 (yin), 7/9 → 1 (yang)
    normalized = []
    for l in lines:
        if l in (6, 0):
            normalized.append(0)
        elif l in (7, 1, 9):
            normalized.append(1)
        else:
            normalized.append(l % 2)

    lower_code = normalized[0] | (normalized[1] << 1) | (normalized[2] << 2)
    upper_code = normalized[3] | (normalized[4] << 1) | (normalized[5] << 2)

    return get_hexagram_by_trigrams(upper_code, lower_code)
