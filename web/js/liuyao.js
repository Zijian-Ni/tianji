/**
 * liuyao.js — 六爻 (Liu Yao / Six Lines Divination) JavaScript Port
 *
 * Ports the Python tianji.liuyao package to browser-side JavaScript.
 * Implements trigrams, hexagrams, casting methods, and analysis (装卦).
 *
 * Usage:
 *   const result = LiuYao.castByTime(new Date());
 *   const result = LiuYao.castByNumbers(5, 8, 3);
 *   const result = LiuYao.castByCoins(42);
 *   const analysis = LiuYao.analyze(result);
 */
const LiuYao = (function () {
  'use strict';

  // ════════════════════════════════════════════════════════════════
  //  Eight Trigrams (八卦)
  //
  //  Trigram encoding: 3-bit integer (lines from bottom to top)
  //    bit 0 = bottom line, bit 1 = middle, bit 2 = top
  //    1 = yang (solid ⚊), 0 = yin (broken ⚋)
  //
  //  乾(☰,7) 兑(☱,6) 离(☲,5) 震(☳,4) 巽(☴,3) 坎(☵,2) 艮(☶,1) 坤(☷,0)
  // ════════════════════════════════════════════════════════════════

  var TRIGRAMS = {
    7: { name: '乾', symbol: '☰', lines: 7, element: '金', nature: '天' },
    6: { name: '兑', symbol: '☱', lines: 6, element: '金', nature: '泽' },
    5: { name: '离', symbol: '☲', lines: 5, element: '火', nature: '火' },
    4: { name: '震', symbol: '☳', lines: 4, element: '木', nature: '雷' },
    3: { name: '巽', symbol: '☴', lines: 3, element: '木', nature: '风' },
    2: { name: '坎', symbol: '☵', lines: 2, element: '水', nature: '水' },
    1: { name: '艮', symbol: '☶', lines: 1, element: '土', nature: '山' },
    0: { name: '坤', symbol: '☷', lines: 0, element: '土', nature: '地' }
  };

  /** Lookup trigram by name. */
  var TRIGRAM_BY_NAME = {};
  for (var tk in TRIGRAMS) {
    if (TRIGRAMS.hasOwnProperty(tk)) {
      TRIGRAM_BY_NAME[TRIGRAMS[tk].name] = TRIGRAMS[tk];
    }
  }

  /**
   * Get the 3 line values of a trigram as [bottom, middle, top].
   * @param {number} code  Trigram code 0–7
   * @returns {number[]}
   */
  function trigramLines(code) {
    return [(code >> 2) & 1, (code >> 1) & 1, code & 1];
  }

  // ════════════════════════════════════════════════════════════════
  //  64 Hexagrams — Full King Wen Sequence (文王六十四卦)
  //
  //  Each entry: [number, name, symbol, upper_code, lower_code, description]
  // ════════════════════════════════════════════════════════════════

  var _HEXAGRAM_DATA = [
    [1,  '乾',   '䷀', 7, 7, '天行健，君子以自强不息'],
    [2,  '坤',   '䷁', 0, 0, '地势坤，君子以厚德载物'],
    [3,  '屯',   '䷂', 2, 4, '刚柔始交而难生，动乎险中'],
    [4,  '蒙',   '䷃', 1, 2, '山下有险，险而止，蒙'],
    [5,  '需',   '䷄', 2, 7, '需，有孚，光亨，贞吉'],
    [6,  '讼',   '䷅', 7, 2, '天与水违行，讼'],
    [7,  '师',   '䷆', 0, 2, '地中有水，师'],
    [8,  '比',   '䷇', 2, 0, '地上有水，比'],
    [9,  '小畜', '䷈', 3, 7, '风行天上，小畜'],
    [10, '履',   '䷉', 7, 6, '上天下泽，履'],
    [11, '泰',   '䷊', 0, 7, '天地交，泰'],
    [12, '否',   '䷋', 7, 0, '天地不交，否'],
    [13, '同人', '䷌', 7, 5, '天与火，同人'],
    [14, '大有', '䷍', 5, 7, '火在天上，大有'],
    [15, '谦',   '䷎', 0, 1, '地中有山，谦'],
    [16, '豫',   '䷏', 4, 0, '雷出地奋，豫'],
    [17, '随',   '䷐', 6, 4, '泽中有雷，随'],
    [18, '蛊',   '䷑', 1, 3, '山下有风，蛊'],
    [19, '临',   '䷒', 0, 6, '泽上有地，临'],
    [20, '观',   '䷓', 3, 0, '风行地上，观'],
    [21, '噬嗑', '䷔', 5, 4, '雷电，噬嗑'],
    [22, '贲',   '䷕', 1, 5, '山下有火，贲'],
    [23, '剥',   '䷖', 1, 0, '山附于地，剥'],
    [24, '复',   '䷗', 0, 4, '雷在地中，复'],
    [25, '无妄', '䷘', 7, 4, '天下雷行，无妄'],
    [26, '大畜', '䷙', 1, 7, '天在山中，大畜'],
    [27, '颐',   '䷚', 1, 4, '山下有雷，颐'],
    [28, '大过', '䷛', 6, 3, '泽灭木，大过'],
    [29, '坎',   '䷜', 2, 2, '水洊至，习坎'],
    [30, '离',   '䷝', 5, 5, '明两作，离'],
    [31, '咸',   '䷞', 6, 1, '山上有泽，咸'],
    [32, '恒',   '䷟', 4, 3, '雷风，恒'],
    [33, '遁',   '䷠', 7, 1, '天下有山，遁'],
    [34, '大壮', '䷡', 4, 7, '雷在天上，大壮'],
    [35, '晋',   '䷢', 5, 0, '明出地上，晋'],
    [36, '明夷', '䷣', 0, 5, '明入地中，明夷'],
    [37, '家人', '䷤', 3, 5, '风自火出，家人'],
    [38, '睽',   '䷥', 5, 6, '上火下泽，睽'],
    [39, '蹇',   '䷦', 2, 1, '山上有水，蹇'],
    [40, '解',   '䷧', 4, 2, '雷雨作，解'],
    [41, '损',   '䷨', 1, 6, '山下有泽，损'],
    [42, '益',   '䷩', 3, 4, '风雷，益'],
    [43, '夬',   '䷪', 6, 7, '泽上于天，夬'],
    [44, '姤',   '䷫', 7, 3, '天下有风，姤'],
    [45, '萃',   '䷬', 6, 0, '泽上于地，萃'],
    [46, '升',   '䷭', 0, 3, '地中生木，升'],
    [47, '困',   '䷮', 6, 2, '泽无水，困'],
    [48, '井',   '䷯', 2, 3, '木上有水，井'],
    [49, '革',   '䷰', 6, 5, '泽中有火，革'],
    [50, '鼎',   '䷱', 5, 3, '木上有火，鼎'],
    [51, '震',   '䷲', 4, 4, '洊雷，震'],
    [52, '艮',   '䷳', 1, 1, '兼山，艮'],
    [53, '渐',   '䷴', 3, 1, '山上有木，渐'],
    [54, '归妹', '䷵', 4, 6, '泽上有雷，归妹'],
    [55, '丰',   '䷶', 4, 5, '雷电皆至，丰'],
    [56, '旅',   '䷷', 5, 1, '山上有火，旅'],
    [57, '巽',   '䷸', 3, 3, '随风，巽'],
    [58, '兑',   '䷹', 6, 6, '丽泽，兑'],
    [59, '涣',   '䷺', 3, 2, '风行水上，涣'],
    [60, '节',   '䷻', 2, 6, '泽上有水，节'],
    [61, '中孚', '䷼', 3, 6, '泽上有风，中孚'],
    [62, '小过', '䷽', 4, 1, '山上有雷，小过'],
    [63, '既济', '䷾', 2, 5, '水在火上，既济'],
    [64, '未济', '䷿', 5, 2, '火在水上，未济']
  ];

  /** All 64 hexagram objects, indexed by number (1-based). */
  var HEXAGRAM_BY_NUMBER = {};

  /** Hexagram lookup by (upper, lower) trigram codes. */
  var HEXAGRAM_BY_TRIGRAMS = {};

  // Build hexagram tables
  (function () {
    for (var i = 0; i < _HEXAGRAM_DATA.length; i++) {
      var d = _HEXAGRAM_DATA[i];
      var hex = {
        number: d[0],
        name: d[1],
        symbol: d[2],
        upperCode: d[3],
        lowerCode: d[4],
        upper: TRIGRAMS[d[3]],
        lower: TRIGRAMS[d[4]],
        description: d[5]
      };
      HEXAGRAM_BY_NUMBER[hex.number] = hex;
      HEXAGRAM_BY_TRIGRAMS[d[3] + ',' + d[4]] = hex;
    }
  })();

  /**
   * Get a hexagram by its King Wen number (1–64).
   */
  function getHexagramByNumber(num) {
    var h = HEXAGRAM_BY_NUMBER[num];
    if (!h) throw new Error('Hexagram number must be 1-64, got ' + num);
    return h;
  }

  /**
   * Get a hexagram by upper and lower trigram codes (0–7).
   */
  function getHexagramByTrigrams(upper, lower) {
    var key = upper + ',' + lower;
    var h = HEXAGRAM_BY_TRIGRAMS[key];
    if (!h) throw new Error('No hexagram for upper=' + upper + ', lower=' + lower);
    return h;
  }

  /**
   * Get the 6 line values of a hexagram as [bottom...top], 1=yang, 0=yin.
   */
  function hexagramLines(hex) {
    var lower = trigramLines(hex.lowerCode);
    var upper = trigramLines(hex.upperCode);
    return lower.concat(upper);
  }

  /**
   * Convert 6 raw line values to a hexagram.
   * Lines: 6=old yin→0, 7=young yang→1, 8=young yin→0, 9=old yang→1
   * Also accepts plain 0/1.
   */
  function linesToHexagram(lines) {
    if (lines.length !== 6) throw new Error('Expected 6 lines, got ' + lines.length);
    if (!lines.every(n => [0, 1, 6, 7, 8, 9].includes(n))) throw new RangeError('Invalid line value');
    const [a, b, c, d, e, f] = lines.map(n => n % 2);
    return getHexagramByTrigrams((d << 2) | (e << 1) | f, (a << 2) | (b << 1) | c);
  }

  function castFromLines(rawLines) {
    if (rawLines.length !== 6 || !rawLines.every(n => [6, 7, 8, 9].includes(n))) {
      throw new RangeError('Expected six coin values in 6–9');
    }
    const movingLines = [];
    rawLines.forEach((n, index) => { if (n === 6 || n === 9) movingLines.push(index + 1); });
    const changed = movingLines.length ? linesToHexagram(rawLines.map(n => Number(n === 6 || n === 7))) : null;
    return { method: '铜钱摇卦', input: {}, rawLines: rawLines.slice(), primary: linesToHexagram(rawLines), changed, movingLines };
  }

  function numberedCast(upper, lower, moving) {
    function index(value, count) { return ((value - 1) % count + count) % count; }
    const bits = trigramLines(7 - index(lower, 8)).concat(trigramLines(7 - index(upper, 8)));
    const raw = bits.map(bit => bit ? 7 : 8);
    const position = index(moving, 6);
    raw[position] = bits[position] ? 9 : 6;
    return castFromLines(raw);
  }

  function castByClock(year, month, day, hour) {
    const lunar = Calendar.solarToLunar(year, month, day);
    const upper = (lunar.year - 4) % 12 + 1 + lunar.month + lunar.day;
    const total = upper + Math.floor((hour + 1) / 2) % 12 + 1;
    return { ...numberedCast(upper, total, total), method: '时间起卦', input: { year, month, day, hour } };
  }

  function castByTime(date) {
    if (date) return castByClock(date.getFullYear(), date.getMonth() + 1, date.getDate(), date.getHours());
    const now = new Date(Date.now() + 8 * 3600000);
    return castByClock(now.getUTCFullYear(), now.getUTCMonth() + 1, now.getUTCDate(), now.getUTCHours());
  }

  function castByNumbers(n1, n2, n3) {
    return { ...numberedCast(n1, n2, n3 ?? n1 + n2), method: '数字起卦', input: { n1, n2, n3: n3 ?? null } };
  }

  /**
   * castByCoins — 铜钱摇卦
   *
   * Simulates tossing 3 coins per line (6 lines).
   * Each coin: heads (正面) = 3, tails (反面) = 2.
   *
   * Sum meanings:
   *   6 = 老阴 (3 tails): Yin, changes to Yang
   *   7 = 少阳 (2 tails + 1 head): Yang, stays
   *   8 = 少阴 (1 tail + 2 heads): Yin, stays
   *   9 = 老阳 (3 heads): Yang, changes to Yin
   *
   * @param {number} [seed]  Random seed for reproducibility (null = truly random)
   * @returns {object} CastResult
   */
  function castByCoins(seed) {
    // Simple seeded pseudo-random (mulberry32)
    var rng;
    if (seed !== undefined && seed !== null) {
      var s = seed | 0;
      rng = function () {
        s = (s + 0x6D2B79F5) | 0;
        var t = Math.imul(s ^ (s >>> 15), 1 | s);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    } else {
      rng = Math.random;
    }

    var rawLines = [];
    for (var line = 0; line < 6; line++) {
      var total = 0;
      for (var coin = 0; coin < 3; coin++) {
        total += (rng() < 0.5) ? 2 : 3; // 2=tails, 3=heads
      }
      rawLines.push(total); // 6, 7, 8, or 9
    }

    return { ...castFromLines(rawLines), input: { seed: seed ?? null } };
  }

  // ════════════════════════════════════════════════════════════════
  //  Analysis (装卦) — 世应, 六亲, 六神
  // ════════════════════════════════════════════════════════════════

  /**
   * 世应 (World/Response) lookup table.
   * Maps hexagram number → [worldLine, responseLine] (1-based positions).
   * Based on the 八宫 (Eight Palace) system.
   */
  var SHIYYING_TABLE = {
     1: [6,3],  2: [6,3],  3: [2,5],  4: [2,5],
     5: [4,1],  6: [4,1],  7: [2,5],  8: [2,5],
     9: [4,1], 10: [4,1], 11: [3,6], 12: [3,6],
    13: [3,6], 14: [3,6], 15: [3,6], 16: [3,6],
    17: [1,4], 18: [1,4], 19: [2,5], 20: [2,5],
    21: [5,2], 22: [5,2], 23: [4,1], 24: [4,1],
    25: [4,1], 26: [4,1], 27: [3,6], 28: [3,6],
    29: [6,3], 30: [6,3], 31: [1,4], 32: [1,4],
    33: [3,6], 34: [3,6], 35: [2,5], 36: [2,5],
    37: [2,5], 38: [2,5], 39: [1,4], 40: [1,4],
    41: [3,6], 42: [3,6], 43: [4,1], 44: [4,1],
    45: [2,5], 46: [2,5], 47: [3,6], 48: [3,6],
    49: [1,4], 50: [1,4], 51: [6,3], 52: [6,3],
    53: [3,6], 54: [3,6], 55: [4,1], 56: [4,1],
    57: [6,3], 58: [6,3], 59: [3,6], 60: [3,6],
    61: [2,5], 62: [2,5], 63: [1,4], 64: [1,4]
  };

  /**
   * Six Gods (六神) in standard order.
   */
  var SIX_GODS = ['青龙', '朱雀', '勾陈', '腾蛇', '白虎', '玄武'];

  /**
   * Day-stem element → Six Gods starting position.
   * Element indices: 木=0, 火=1, 土=2, 金=3, 水=4
   */
  var ELEMENT_GOD_START = {
    0: 0,  // 木(甲乙) → 青龙起
    1: 2,  // 火(丙丁) → 勾陈起
    2: 2,  // 土(戊己) → 勾陈起
    3: 4,  // 金(庚辛) → 白虎起
    4: 5   // 水(壬癸) → 玄武起
  };

  /**
   * Palace element map: trigram name → element name.
   */
  var PALACE_ELEMENT_MAP = {
    '乾': '金', '兑': '金', '离': '火', '震': '木',
    '巽': '木', '坎': '水', '艮': '土', '坤': '土'
  };

  /**
   * Element cycle helpers for Six Relatives (六亲).
   * Indices: 木=0, 火=1, 土=2, 金=3, 水=4
   *
   * 相生 cycle: 木→火→土→金→水→木
   */
  var ELEMENT_NAMES = ['木', '火', '土', '金', '水'];
  var ELEMENT_BY_NAME = { '木': 0, '火': 1, '土': 2, '金': 3, '水': 4 };

  /** produces[i] = element produced by i */
  var _PRODUCES = [1, 2, 3, 4, 0]; // 木→火, 火→土, 土→金, 金→水, 水→木

  /** conquers[i] = element conquered by i */
  var _CONQUERS = [2, 3, 4, 0, 1]; // 木克土, 火克金, 土克水, 金克木, 水克火

  /**
   * Standard branch assignment for yang/yin palace lines (bottom to top).
   */
  var YANG_PALACE_BRANCHES = ['子', '寅', '辰', '午', '申', '戌'];
  var YIN_PALACE_BRANCHES  = ['丑', '亥', '酉', '未', '巳', '卯'];

  var BRANCH_ELEMENT = {
    '子': 4, '丑': 2, '寅': 0, '卯': 0, '辰': 2, '巳': 1,
    '午': 1, '未': 2, '申': 3, '酉': 3, '戌': 2, '亥': 4
  };

  /**
   * Compute Six Relative (六亲) name from line element vs palace element.
   * @param {number} lineEl    Element index of the line (0–4)
   * @param {number} palaceEl  Element index of the palace (0–4)
   * @returns {string}
   */
  function _getSixRelative(lineEl, palaceEl) {
    if (lineEl === palaceEl) return '兄弟';
    if (_PRODUCES[palaceEl] === lineEl) return '子孙';
    if (_PRODUCES[lineEl] === palaceEl) return '父母';
    if (_CONQUERS[palaceEl] === lineEl) return '妻财';
    if (_CONQUERS[lineEl] === palaceEl) return '官鬼';
    return '兄弟'; // fallback
  }

  /**
   * analyze — perform full 装卦 analysis on a cast result.
   *
   * Loads 世应 (world/response), 六亲 (six relatives), and 六神 (six gods).
   *
   * @param {object} castResult     Result from castByTime/castByNumbers/castByCoins
   * @param {number} [dayStemElement]  Day-stem element index (0–4) for six-gods order.
   *                                   Default 0 (木/甲日 → 青龙起).
   * @returns {object}  { hexagram, worldLine, responseLine, lines: [...], changed }
   */
  function analyze(castResult, dayStemElement) {
    if (dayStemElement === undefined || dayStemElement === null) dayStemElement = 0;

    var hex = castResult.primary;
    var rawLines = castResult.rawLines;
    var movingLines = castResult.movingLines;

    // 世应 positions
    var sy = SHIYYING_TABLE[hex.number] || [3, 6];
    var worldLine = sy[0];
    var responseLine = sy[1];

    // Palace element from lower trigram
    var palaceElName = PALACE_ELEMENT_MAP[hex.lower.name] || '土';
    var palaceEl = ELEMENT_BY_NAME[palaceElName];

    // Six Gods starting position
    var godStart = ELEMENT_GOD_START[dayStemElement] || 0;

    var LINE_NAMES = ['初', '二', '三', '四', '五', '上'];
    var lines = [];

    for (var i = 0; i < 6; i++) {
      var pos = i + 1;
      var raw = rawLines[i];
      var isYang = (raw === 7 || raw === 9 || raw === 1);
      var isMoving = (movingLines.indexOf(pos) !== -1);

      // Line element (simplified: use yang palace branches)
      var branch = YANG_PALACE_BRANCHES[i];
      var lineEl = BRANCH_ELEMENT[branch];

      var sixRelative = _getSixRelative(lineEl, palaceEl);
      var sixGod = SIX_GODS[(godStart + i) % 6];

      lines.push({
        position: pos,
        name: LINE_NAMES[i],
        isYang: isYang,
        isMoving: isMoving,
        element: ELEMENT_NAMES[lineEl],
        sixRelative: sixRelative,
        sixGod: sixGod,
        isWorld: (pos === worldLine),
        isResponse: (pos === responseLine)
      });
    }

    return {
      hexagram: hex,
      worldLine: worldLine,
      responseLine: responseLine,
      lines: lines,
      changed: castResult.changed,
      movingLines: movingLines
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  Public API
  // ════════════════════════════════════════════════════════════════

  return {
    // Trigrams 八卦
    TRIGRAMS: TRIGRAMS,
    TRIGRAM_BY_NAME: TRIGRAM_BY_NAME,
    trigramLines: trigramLines,

    // Hexagrams 六十四卦
    HEXAGRAM_BY_NUMBER: HEXAGRAM_BY_NUMBER,
    getHexagramByNumber: getHexagramByNumber,
    getHexagramByTrigrams: getHexagramByTrigrams,
    hexagramLines: hexagramLines,
    linesToHexagram: linesToHexagram,

    // Casting 起卦
    castByTime: castByTime,
    castByClock,
    castFromLines,
    castByNumbers: castByNumbers,
    castByCoins: castByCoins,

    // Analysis 装卦
    SHIYYING_TABLE: SHIYYING_TABLE,
    SIX_GODS: SIX_GODS,
    analyze: analyze,

    // Constants
    ELEMENT_NAMES: ELEMENT_NAMES,
    PALACE_ELEMENT_MAP: PALACE_ELEMENT_MAP
  };
})();
