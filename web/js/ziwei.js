/**
 * ziwei.js — 紫微斗数 (Zi Wei Dou Shu / Purple Star Astrology) JavaScript Port
 *
 * Ports the Python tianji.ziwei package to browser-side JavaScript.
 * Implements the 12 palaces, 14 major stars, and chart calculation.
 *
 * Usage:
 *   const chart = ZiWei.createChart(1990, 3, 15, 10, 'male');
 *   console.log(chart.palaces);    // 12 palaces with branches
 *   console.log(chart.stars);      // star placements
 */
const ZiWei = (function () {
  'use strict';

  // ════════════════════════════════════════════════════════════════
  //  12 Palaces (十二宫)
  //
  //  The palaces form the skeleton of a Zi Wei chart.
  //  Each governs a specific domain of life.
  // ════════════════════════════════════════════════════════════════

  /**
   * Palace definitions: [name, english, meaning]
   * Order is fixed; earthly-branch assignment rotates based on 命宫 position.
   */
  var PALACE_DEFS = [
    ['命宫',   'Life/Destiny',      '命主本人，性格、外貌、整体运势'],
    ['兄弟宫', 'Siblings',          '兄弟姐妹、朋友、合作关系'],
    ['夫妻宫', 'Spouse',            '婚姻、感情、配偶'],
    ['子女宫', 'Children',          '子女、下属、创意'],
    ['财帛宫', 'Wealth',            '财运、理财、金钱'],
    ['疾厄宫', 'Health',            '健康、疾病、意外'],
    ['迁移宫', 'Travel/Migration',  '出行、搬迁、外在表现'],
    ['奴仆宫', 'Servants/Friends',  '朋友、下属、人际关系'],
    ['官禄宫', 'Career',            '事业、名誉、官职'],
    ['田宅宫', 'Property',          '房产、家宅、家庭环境'],
    ['福德宫', 'Fortune/Virtue',    '福气、精神生活、享受'],
    ['父母宫', 'Parents',           '父母、上司、长辈']
  ];

  /** Palace name list (convenience). */
  var PALACE_NAMES = [];
  for (var pi = 0; pi < PALACE_DEFS.length; pi++) {
    PALACE_NAMES.push(PALACE_DEFS[pi][0]);
  }

  /** Earthly branches in standard order. */
  var BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

  /**
   * buildPalaceRing — build the 12-palace ring starting from the Life Palace.
   *
   * Palaces are arranged counterclockwise (逆时针) from 命宫.
   *
   * @param {number} lifePalacePos  Branch index (0–11) where 命宫 is located
   * @returns {object[]}  Array of 12 palace objects
   */
  function buildPalaceRing(lifePalacePos) {
    var palaces = [];
    for (var i = 0; i < 12; i++) {
      // Counterclockwise: each subsequent palace is at branchIdx - 1
      var branchIdx = ((lifePalacePos - i) % 12 + 12) % 12;
      palaces.push({
        index: i,
        name: PALACE_DEFS[i][0],
        english: PALACE_DEFS[i][1],
        branch: BRANCHES[branchIdx],
        branchIndex: branchIdx,
        meaning: PALACE_DEFS[i][2],
        stars: [] // filled later by star placement
      });
    }
    return palaces;
  }

  // ════════════════════════════════════════════════════════════════
  //  Stars (星曜)
  // ════════════════════════════════════════════════════════════════

  /**
   * 紫微星系 (Zi Wei Group) — offsets relative to 紫微 position.
   *
   * 紫微(0), 天机(-1), 太阳(-3), 武曲(-4), 天同(-5), 廉贞(-8)
   */
  var ZIWEI_GROUP_OFFSETS = {
    '紫微':  0,
    '天机': -1,
    '太阳': -3,
    '武曲': -4,
    '天同': -5,
    '廉贞': -8
  };

  /**
   * 天府星系 (Tian Fu Group) — offsets relative to 天府 position.
   *
   * 天府(0), 太阴(1), 贪狼(2), 巨门(3), 天相(4), 天梁(5), 七杀(6), 破军(10)
   */
  var TIANFU_GROUP_OFFSETS = {
    '天府':  0,
    '太阴':  1,
    '贪狼':  2,
    '巨门':  3,
    '天相':  4,
    '天梁':  5,
    '七杀':  6,
    '破军': 10
  };

  /** All 14 major stars (十四主星). */
  var MAJOR_STARS = Object.keys(ZIWEI_GROUP_OFFSETS).concat(Object.keys(TIANFU_GROUP_OFFSETS));

  /**
   * Place Zi Wei group stars given Zi Wei's palace position.
   * @param {number} ziweiPos  Palace position index (0–11)
   * @returns {object}  { starName: palacePosition, ... }
   */
  function placeZiweiGroup(ziweiPos) {
    var result = {};
    for (var star in ZIWEI_GROUP_OFFSETS) {
      if (ZIWEI_GROUP_OFFSETS.hasOwnProperty(star)) {
        result[star] = ((ziweiPos + ZIWEI_GROUP_OFFSETS[star]) % 12 + 12) % 12;
      }
    }
    return result;
  }

  /**
   * Place Tian Fu group stars given Tian Fu's palace position.
   * @param {number} tianfuPos  Palace position index (0–11)
   * @returns {object}  { starName: palacePosition, ... }
   */
  function placeTianfuGroup(tianfuPos) {
    var result = {};
    for (var star in TIANFU_GROUP_OFFSETS) {
      if (TIANFU_GROUP_OFFSETS.hasOwnProperty(star)) {
        result[star] = ((tianfuPos + TIANFU_GROUP_OFFSETS[star]) % 12 + 12) % 12;
      }
    }
    return result;
  }

  // ════════════════════════════════════════════════════════════════
  //  Chart Calculation (排盘)
  // ════════════════════════════════════════════════════════════════

  /**
   * 五行局 (Wu Xing Ju) table.
   *
   * Indexed by the combined position of year stem and 命宫 branch.
   * Simplified table: indexed by (yearStemIndex * 12 + lifePalaceBranchIndex) → ju value
   *
   * Standard mapping based on 纳音 groupings (2=水二局, 3=木三局, 4=金四局, 5=土五局, 6=火六局):
   */
  var WUXINGJU_TABLE = [2, 6, 5, 3, 4, 2, 6, 5, 3, 4, 2, 6];

  /**
   * computeLifePalacePos — calculate the 命宫 (Life Palace) branch position.
   *
   * Formula: (2 + month - 1 - hourBranch) % 12
   *   where month is the lunar month (1–12) and hourBranch is the 时辰 branch index (0–11).
   *
   * Explanation:
   *   - Base position is 寅 (index 2) for lunar month 1, 子时.
   *   - Each additional month moves one step forward (counterclockwise on chart = +1 index).
   *   - Each additional 时辰 moves one step backward (-1 index).
   *
   * @param {number} lunarMonth   Lunar month 1–12
   * @param {number} hourBranch   Hour branch index 0–11 (子=0, 丑=1, ..., 亥=11)
   * @returns {number}  Branch index 0–11 for 命宫
   */
  function computeLifePalacePos(lunarMonth, hourBranch) {
    return ((2 + lunarMonth - 1 - hourBranch) % 12 + 12) % 12;
  }

  /**
   * computeBodyPalacePos — calculate the 身宫 (Body Palace) branch position.
   *
   * Formula: (2 + month - 1 + hourBranch) % 12
   *
   * @param {number} lunarMonth
   * @param {number} hourBranch
   * @returns {number}
   */
  function computeBodyPalacePos(lunarMonth, hourBranch) {
    return ((2 + lunarMonth - 1 + hourBranch) % 12 + 12) % 12;
  }

  // Without a year stem retain the one-argument legacy lookup. Charts always
  // supply the year stem to derive the life palace's stem and 纳音 element.
  function getWuXingJu(lifePalacePos, yearStemIndex) {
    if (yearStemIndex == null) return WUXINGJU_TABLE[lifePalacePos % 12];
    const stem = (2 + 2 * (yearStemIndex % 5) + (lifePalacePos + 10) % 12) % 10;
    const group = (Math.floor(stem / 2) + Math.floor((lifePalacePos % 6) / 2) + 1) % 5;
    return [3, 4, 2, 6, 5][group];
  }

  /** 五行局 name lookup. */
  var WUXINGJU_NAMES = {
    2: '水二局',
    3: '木三局',
    4: '金四局',
    5: '土五局',
    6: '火六局'
  };

  /**
   * computeZiweiPos — calculate the 紫微星 palace position from lunar day and 五行局.
   *
   * This is the core algorithm of Zi Wei Dou Shu.
   * The position is determined by dividing the lunar day by the Wu Xing Ju number
   * and applying a lookup correction.
   *
   * Algorithm:
   *   1. quotient = ceil(lunarDay / ju)
   *   2. remainder = quotient * ju - lunarDay
   *   3. Apply parity-based correction to get final position
   *
   * @param {number} lunarDay  Day of the lunar month (1–30)
   * @param {number} ju        五行局 number (2, 3, 4, 5, or 6)
   * @returns {number}  Palace position (0–11) for 紫微
   */
  function computeZiweiPos(lunarDay, ju) {
    const quotient = Math.ceil(lunarDay / ju);
    const padding = quotient * ju - lunarDay;
    return (1 + quotient + (padding % 2 === 0 ? padding : -padding) + 12) % 12;
  }

  /**
   * computeTianfuPos — calculate 天府星 position from 紫微 position.
   *
   * Formula: (12 - ziweiPos + 4) % 12
   * Tian Fu mirrors Zi Wei across the 寅申 axis.
   *
   * @param {number} ziweiPos  紫微 palace position (0–11)
   * @returns {number}  天府 palace position (0–11)
   */
  function computeTianfuPos(ziweiPos) {
    return ((12 - ziweiPos + 4) % 12 + 12) % 12;
  }

  /**
   * createChart — build a complete Zi Wei Dou Shu chart.
   *
   * @param {number} lunarYear   Lunar year (used for stem/branch)
   * @param {number} lunarMonth  Lunar month (1–12)
   * @param {number} lunarDay    Lunar day (1–30)
   * @param {number} hour        Birth hour (0–23) — mapped to 时辰 branch index
   * @param {string} [gender]    "male" or "female" (default "male")
   * @returns {object}  Complete chart with palaces and star placements
   */
  function createChart(lunarYear, lunarMonth, lunarDay, hour, gender, isLeap = false) {
    if (!Number.isInteger(hour) || hour < 0 || hour > 23 ||
        !Number.isInteger(lunarMonth) || lunarMonth < 1 || lunarMonth > 12 ||
        !Number.isInteger(lunarDay) || lunarDay < 1 || lunarDay > 30) throw new RangeError('Invalid lunar birth date or time');
    if (typeof Calendar !== 'undefined' && (isLeap || (lunarYear >= 1900 && lunarYear <= 2100))) {
      Calendar.lunarToSolar(lunarYear, lunarMonth, lunarDay, isLeap);
    }
    if (!gender) gender = 'male';

    // Map clock hour to 时辰 branch index (子=0, 丑=1, ...)
    var hourBranch;
    if (hour === 23) {
      hourBranch = 0; // 子时
    } else {
      hourBranch = Math.floor((hour + 1) / 2);
    }

    // Year stem index (for Wu Xing Ju and other derivations)
    var yearStemIdx = ((lunarYear - 4) % 10 + 10) % 10;
    var yearBranchIdx = ((lunarYear - 4) % 12 + 12) % 12;

    // ── 1. 命宫 (Life Palace) position ──
    var lifePalacePos = computeLifePalacePos(lunarMonth, hourBranch);

    // ── 2. 身宫 (Body Palace) position ──
    var bodyPalacePos = computeBodyPalacePos(lunarMonth, hourBranch);

    // ── 3. 五行局 ──
    var ju = getWuXingJu(lifePalacePos, yearStemIdx);

    // ── 4. 紫微星 position ──
    var ziweiPos = computeZiweiPos(lunarDay, ju);

    // ── 5. 天府星 position ──
    var tianfuPos = computeTianfuPos(ziweiPos);

    // ── 6. Build 12 palace ring ──
    var palaces = buildPalaceRing(lifePalacePos);

    // ── 7. Place 14 major stars ──
    var ziweiStars = placeZiweiGroup(ziweiPos);
    var tianfuStars = placeTianfuGroup(tianfuPos);

    // Merge all star placements: { starName: palaceBranchIndex }
    var allStars = {};
    var starName;
    for (starName in ziweiStars) {
      if (ziweiStars.hasOwnProperty(starName)) {
        allStars[starName] = ziweiStars[starName];
      }
    }
    for (starName in tianfuStars) {
      if (tianfuStars.hasOwnProperty(starName)) {
        allStars[starName] = tianfuStars[starName];
      }
    }

    // Attach stars to their respective palaces
    for (starName in allStars) {
      if (allStars.hasOwnProperty(starName)) {
        var starPalaceIdx = allStars[starName];
        // Find the palace at that branch position
        for (var p = 0; p < palaces.length; p++) {
          if (palaces[p].branchIndex === starPalaceIdx) {
            palaces[p].stars.push(starName);
            break;
          }
        }
      }
    }

    return {
      // Input parameters
      lunarYear: lunarYear,
      isLeap,
      lunarMonth: lunarMonth,
      lunarDay: lunarDay,
      hour: hour,
      hourBranch: hourBranch,
      gender: gender,

      // Year stem/branch
      yearStemIndex: yearStemIdx,
      yearBranchIndex: yearBranchIdx,

      // Core positions
      lifePalacePos: lifePalacePos,
      lifePalaceBranch: BRANCHES[lifePalacePos],
      bodyPalacePos: bodyPalacePos,
      bodyPalaceBranch: BRANCHES[bodyPalacePos],

      // 五行局
      wuXingJu: ju,
      wuXingJuName: WUXINGJU_NAMES[ju] || ('局' + ju),

      // Star positions
      ziweiPos: ziweiPos,
      ziweiBranch: BRANCHES[ziweiPos],
      tianfuPos: tianfuPos,
      tianfuBranch: BRANCHES[tianfuPos],

      // Star placement map
      stars: allStars,

      // 12 palaces (each with attached stars)
      palaces: palaces,

      /**
       * Get the palace at a specific branch index.
       * @param {number} branchIdx 0–11
       * @returns {object|null}
       */
      getPalaceAtBranch: function (branchIdx) {
        for (var i = 0; i < palaces.length; i++) {
          if (palaces[i].branchIndex === branchIdx) return palaces[i];
        }
        return null;
      },

      /**
       * Get the palace by name (e.g., '命宫', '财帛宫').
       * @param {string} name
       * @returns {object|null}
       */
      getPalaceByName: function (name) {
        for (var i = 0; i < palaces.length; i++) {
          if (palaces[i].name === name) return palaces[i];
        }
        return null;
      },

      /**
       * Find which palace a star is in.
       * @param {string} starName
       * @returns {object|null}
       */
      findStar: function (starName) {
        if (!(starName in allStars)) return null;
        var branchIdx = allStars[starName];
        for (var i = 0; i < palaces.length; i++) {
          if (palaces[i].branchIndex === branchIdx) {
            return {
              star: starName,
              palace: palaces[i],
              branch: BRANCHES[branchIdx]
            };
          }
        }
        return null;
      }
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  Public API
  // ════════════════════════════════════════════════════════════════

  return {
    // Palace 十二宫
    PALACE_NAMES: PALACE_NAMES,
    PALACE_DEFS: PALACE_DEFS,
    BRANCHES: BRANCHES,
    buildPalaceRing: buildPalaceRing,

    // Stars 星曜
    ZIWEI_GROUP_OFFSETS: ZIWEI_GROUP_OFFSETS,
    TIANFU_GROUP_OFFSETS: TIANFU_GROUP_OFFSETS,
    MAJOR_STARS: MAJOR_STARS,
    placeZiweiGroup: placeZiweiGroup,
    placeTianfuGroup: placeTianfuGroup,

    // Chart calculation 排盘
    computeLifePalacePos: computeLifePalacePos,
    computeBodyPalacePos: computeBodyPalacePos,
    getWuXingJu: getWuXingJu,
    WUXINGJU_NAMES: WUXINGJU_NAMES,
    WUXINGJU_TABLE: WUXINGJU_TABLE,
    computeZiweiPos: computeZiweiPos,
    computeTianfuPos: computeTianfuPos,
    createChart: createChart
  };
})();
