/**
 * bazi.js — 八字四柱排盘 (BaZi Four-Pillar Chart) JavaScript Engine
 *
 * Comprehensive BaZi calculation engine including:
 *   - 四柱 (Four Pillars): year, month, day, hour
 *   - 十神 (Ten Gods)
 *   - 五行分析 (Five Elements analysis)
 *   - 日主强弱 (Day Master strength)
 *   - 纳音 (Nayin / Sound-Element)
 *   - 胎元 (Taiyuan / Conception Pillar)
 *   - 命宫 (Minggong / Life Palace)
 *   - 神煞 (Shensha / Divine Stars)
 *   - 大运 (Luck Pillars)
 *   - 流年 (Flow Years)
 *   - 刑冲合害 (Branch Relationships)
 *   - 格局分析 (Pattern Analysis)
 *   - 用神建议 (Favorable Element)
 *
 * Depends on the `Calendar` global from calendar.js.
 *
 * Usage:
 *   var chart = BaZi.createChart(1990, 5, 15, 13, 'male');
 *   var tenGods = BaZi.tenGodsFromChart(chart);
 *   var elements = BaZi.analyzeFiveElements(chart.allStems, chart.allBranches);
 *   var strength = BaZi.analyzeDayMasterStrength(chart);
 *   var luck = BaZi.computeLuckPillars(chart);
 *   var nayin = BaZi.getNayinForChart(chart);
 *   var taiyuan = BaZi.computeTaiyuan(chart);
 *   var minggong = BaZi.computeMinggong(chart);
 *   var shensha = BaZi.computeShensha(chart);
 *   var pattern = BaZi.analyzePattern(chart, strength);
 *   var favorable = BaZi.suggestFavorable(chart, strength, elements);
 *   var rels = BaZi.analyzeRelationships(chart.allBranches);
 */
const BaZi = (function () {
  'use strict';

  // ────────────────────────────────────────────────────────────────
  // Calendar accessor — safely resolve at call time
  // ────────────────────────────────────────────────────────────────
  function _C() {
    if (typeof Calendar === 'undefined') {
      throw new Error('BaZi: Calendar global not found. Load calendar.js first.');
    }
    return Calendar;
  }

  // ────────────────────────────────────────────────────────────────
  // Bridge helpers — thin wrappers over Calendar object API
  // ────────────────────────────────────────────────────────────────

  /** Get stem character by index. */
  function _stemChar(idx) { return _C().getStem(idx).char; }
  /** Get branch character by index. */
  function _branchChar(idx) { return _C().getBranch(idx).char; }
  /** Get stem-branch string for a jiazi index. */
  function _jiaziChar(stemIdx, branchIdx) { return _stemChar(stemIdx) + _branchChar(branchIdx); }
  /** Get element string of a stem by index. */
  function _stemElStr(idx) { return _C().getStem(idx).element; }
  /** Get element index (0-4: 木火土金水) of a stem. */
  function _stemElIdx(idx) { return _C().stemElement(idx); }
  /** Get element index from string. */
  function _elIdx(elStr) { return _C().ELEMENTS.indexOf(elStr); }
  /** Positive mod. */
  function _mod(n, m) { return ((n % m) + m) % m; }
  // A public Date denotes its local civil fields; internal numeric arguments
  // encode those fields directly so the device timezone cannot alter a chart.
  function wallMillis(value) {
    if (typeof value === 'number') return value;
    return Date.UTC(value.getFullYear(), value.getMonth(), value.getDate(), value.getHours(), value.getMinutes());
  }

  // ────────────────────────────────────────────────────────────────
  // Constants
  // ────────────────────────────────────────────────────────────────

  /** 五虎遁月法: year-stem%5 → starting stem index for 寅月 */
  var WUHU_TABLE = { 0: 2, 1: 4, 2: 6, 3: 8, 4: 0 };

  /** 五鼠遁时法: day-stem%5 → starting stem index for 子时 */
  var WUSHU_TABLE = { 0: 0, 1: 2, 2: 4, 3: 6, 4: 8 };

  /** Monthly branch indices: BaZi month 1..12 → branch index. 寅(2)→丑(1). */
  var MONTH_BRANCH_INDICES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1];

  /** Element names. */
  var ELEMENT_NAMES = ['木', '火', '土', '金', '水'];

  /** Hidden-stem weights: main=1.0, middle=0.6, residual=0.4 */
  var HIDDEN_STEM_WEIGHTS = [1.0, 0.6, 0.4];

  // ════════════════════════════════════════════════════════════════
  //  纳音 (Nayin / Sound-Element) — 六十甲子纳音表
  // ════════════════════════════════════════════════════════════════

  /**
   * 纳音五行 table: index = floor(jiaziIndex / 2).
   * Each pair of consecutive jiazi shares the same nayin.
   */
  var NAYIN_TABLE = [
    '海中金', '炉中火', '大林木', '路旁土', '剑锋金',  //  0-9:  甲子~癸酉
    '山头火', '涧下水', '城头土', '白蜡金', '杨柳木',  // 10-19: 甲戌~癸未
    '泉中水', '屋上土', '霹雳火', '松柏木', '长流水',  // 20-29: 甲申~癸巳
    '沙中金', '山下火', '平地木', '壁上土', '金箔金',  // 30-39: 甲午~癸卯
    '佛灯火', '天河水', '大驿土', '钗钏金', '桑柘木',  // 40-49: 甲辰~癸丑
    '大溪水', '沙中土', '天上火', '石榴木', '大海水'   // 50-59: 甲寅~癸亥
  ];

  /** Get nayin string for a jiazi index. */
  function getNayin(jiaziIndex) {
    return NAYIN_TABLE[Math.floor(_mod(jiaziIndex, 60) / 2)];
  }

  /** Get nayin info for all four pillars. */
  function getNayinForChart(chart) {
    var pillars = chart.pillars;
    return pillars.map(function (p) {
      return {
        pillar: p.char,
        nayin: getNayin(p.jiaziIndex)
      };
    });
  }

  // ════════════════════════════════════════════════════════════════
  //  四柱计算 — Four Pillar Computation
  // ════════════════════════════════════════════════════════════════

  /**
   * 年柱 — Year Pillar.
   * Year changes at 立春, not Jan 1.
   */
  function computeYearPillar(date) {
    var C = _C();
    var millis = wallMillis(date);
    var year = new Date(millis).getUTCFullYear();
    if (millis < C.termWallMillis(year, '立春')) year -= 1;

    var idx = _mod(year - 4, 60);
    var stemIdx = idx % 10;
    var branchIdx = idx % 12;
    return {
      stemIndex: stemIdx,
      branchIndex: branchIdx,
      char: _jiaziChar(stemIdx, branchIdx),
      jiaziIndex: idx
    };
  }

  /**
   * 月柱 — Month Pillar (uses 五虎遁月法).
   * Month determined by 节气 boundaries.
   */
  function computeMonthPillar(date, yearStemIndex) {
    var term = _C().monthWindow(wallMillis(date)).previous.term;
    var branchIdx = (_C().SOLAR_TERMS.indexOf(term) / 2 + 1) % 12;
    var baseStem = WUHU_TABLE[yearStemIndex % 5];
    var monthOffset = MONTH_BRANCH_INDICES.indexOf(branchIdx);
    if (monthOffset === -1) monthOffset = 0;

    var stemIdx = (baseStem + monthOffset) % 10;
    var jiaziIdx = _stemBranchToJiazi(stemIdx, branchIdx);
    return {
      stemIndex: stemIdx,
      branchIndex: branchIdx,
      char: _jiaziChar(stemIdx, branchIdx),
      jiaziIndex: jiaziIdx,
      monthNumber: monthOffset + 1  // BaZi month 1-12
    };
  }

  /**
   * 日柱 — Day Pillar.
   * Reference: 1900-01-01 = 甲戌 (index 10).
   * Verified: 1949-10-01 = 甲子, 2004-07-21 = 辛丑.
   */
  function computeDayPillar(date) {
    var civil = new Date(wallMillis(date));
    var idx = _C().jiaziIndexForDate({ year: civil.getUTCFullYear(), month: civil.getUTCMonth() + 1, day: civil.getUTCDate() });
    var stemIdx = idx % 10;
    var branchIdx = idx % 12;
    return {
      stemIndex: stemIdx,
      branchIndex: branchIdx,
      char: _jiaziChar(stemIdx, branchIdx),
      jiaziIndex: idx
    };
  }

  /**
   * 时柱 — Hour Pillar (uses 五鼠遁时法).
   * @param {number} hour  Clock hour 0-23
   * @param {number} dayStemIndex  0-9
   */
  function computeHourPillar(hour, dayStemIndex) {
    var branchIdx = (hour === 23) ? 0 : Math.floor((hour + 1) / 2);
    var baseStem = WUSHU_TABLE[dayStemIndex % 5];
    var stemIdx = (baseStem + branchIdx) % 10;
    var jiaziIdx = _stemBranchToJiazi(stemIdx, branchIdx);
    return {
      stemIndex: stemIdx,
      branchIndex: branchIdx,
      char: _jiaziChar(stemIdx, branchIdx),
      jiaziIndex: jiaziIdx
    };
  }

  /** Find 60-cycle index for stem/branch pair. @private */
  function _stemBranchToJiazi(stemIdx, branchIdx) {
    for (var i = 0; i < 60; i++) {
      if (i % 10 === stemIdx && i % 12 === branchIdx) return i;
    }
    return 0;
  }

  /**
   * createChart — build a complete BaZi chart.
   * @param {number} year    Gregorian year
   * @param {number} month   1-12
   * @param {number} day     1-31
   * @param {number} hour    0-23 (default 12)
   * @param {string} gender  "male" or "female"
   */
  function createChart(year, month, day, hour, gender, minute = 0) {
    if (hour === undefined || hour === null) hour = 12;
    if (!gender) gender = 'male';

    const millis = Date.UTC(year, month - 1, day, hour, minute);
    const civil = new Date(millis);
    if (!Number.isInteger(minute) || civil.getUTCFullYear() !== year || civil.getUTCMonth() + 1 !== month ||
        civil.getUTCDate() !== day || civil.getUTCHours() !== hour || civil.getUTCMinutes() !== minute) {
      throw new RangeError('Invalid birth date or time');
    }
    var yearP = computeYearPillar(millis);
    var monthP = computeMonthPillar(millis, yearP.stemIndex);
    var dayP = computeDayPillar(millis);
    var hourP = computeHourPillar(hour, dayP.stemIndex);
    var dayMasterIdx = dayP.stemIndex;

    return {
      birthYear: year,
      birthMonth: month,
      birthDay: day,
      birthHour: hour,
      birthMinute: minute,
      birthDatetime: new Date(year, month - 1, day, hour, minute),
      gender: gender,
      yearPillar: yearP,
      monthPillar: monthP,
      dayPillar: dayP,
      hourPillar: hourP,
      dayMasterIndex: dayMasterIdx,
      dayMasterChar: _stemChar(dayMasterIdx),
      dayMasterElement: _stemElStr(dayMasterIdx),
      dayMasterElementIndex: _stemElIdx(dayMasterIdx),

      get allStems() {
        return [yearP.stemIndex, monthP.stemIndex, dayP.stemIndex, hourP.stemIndex];
      },
      get allBranches() {
        return [yearP.branchIndex, monthP.branchIndex, dayP.branchIndex, hourP.branchIndex];
      },
      get pillars() {
        return [yearP, monthP, dayP, hourP];
      }
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  十神 (Ten Gods)
  // ════════════════════════════════════════════════════════════════

  /** Compute Ten God of `otherIdx` relative to Day Master `dmIdx`. */
  function computeTenGod(dmIdx, otherIdx) {
    return _C().stemRelationshipByIndex(dmIdx, otherIdx);
  }

  /**
   * Ten Gods for every position in the chart (stems + hidden stems).
   */
  function tenGodsFromChart(chart) {
    var C = _C();
    var dm = chart.dayMasterIndex;
    var result = {};

    var pillarNames = ['年干', '月干', '日干', '时干'];
    var stemIndices = chart.allStems;
    for (var i = 0; i < 4; i++) {
      if (i === 2) continue;
      result[pillarNames[i]] = {
        stemIndex: stemIndices[i],
        stem: _stemChar(stemIndices[i]),
        god: computeTenGod(dm, stemIndices[i])
      };
    }

    var branchLabels = ['年支藏干', '月支藏干', '日支藏干', '时支藏干'];
    var branchIndices = chart.allBranches;
    for (var b = 0; b < 4; b++) {
      var hidden = C.getHiddenStemIndices(branchIndices[b]);
      if (hidden && hidden.length > 0) {
        var arr = [];
        for (var h = 0; h < hidden.length; h++) {
          arr.push({
            stemIndex: hidden[h],
            stem: _stemChar(hidden[h]),
            god: computeTenGod(dm, hidden[h])
          });
        }
        result[branchLabels[b]] = arr;
      }
    }
    return result;
  }

  // ════════════════════════════════════════════════════════════════
  //  五行分析 (Five Elements Analysis)
  // ════════════════════════════════════════════════════════════════

  /**
   * Weighted five-element scores from stems and branches.
   */
  function analyzeFiveElements(stemIndices, branchIndices) {
    var C = _C();
    var scores = [0, 0, 0, 0, 0]; // 木火土金水

    for (var s = 0; s < stemIndices.length; s++) {
      scores[C.stemElement(stemIndices[s])] += 1.0;
    }

    for (var b = 0; b < branchIndices.length; b++) {
      var hidden = C.getHiddenStemIndices(branchIndices[b]);
      for (var h = 0; h < hidden.length; h++) {
        var w = h < HIDDEN_STEM_WEIGHTS.length ? HIDDEN_STEM_WEIGHTS[h] : 0.3;
        scores[C.stemElement(hidden[h])] += w;
      }
    }

    var strongest = 0, weakest = 0;
    var missing = [];
    for (var i = 0; i < 5; i++) {
      if (scores[i] > scores[strongest]) strongest = i;
      if (scores[i] < scores[weakest]) weakest = i;
      if (scores[i] === 0) missing.push(i);
    }

    // 生克关系描述
    var total = 0;
    for (var t = 0; t < 5; t++) total += scores[t];
    var details = [];
    for (var d = 0; d < 5; d++) {
      var pct = total > 0 ? (scores[d] / total * 100).toFixed(1) : '0.0';
      var status = '';
      if (scores[d] >= total * 0.3) status = '旺';
      else if (scores[d] >= total * 0.15) status = '中';
      else if (scores[d] > 0) status = '弱';
      else status = '缺';
      details.push({
        element: ELEMENT_NAMES[d],
        score: scores[d],
        percent: pct,
        status: status
      });
    }

    return {
      scores: scores,
      strongest: strongest,
      weakest: weakest,
      missing: missing,
      details: details,
      total: total,
      summary: function () {
        return details.map(function (d) {
          return d.element + ':' + d.score.toFixed(1) + '(' + d.status + ')';
        }).join(' ');
      }
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  日主强弱 (Day Master Strength)
  // ════════════════════════════════════════════════════════════════

  var MONTH_SUPPORT = {
    '寅': [3, 2, -1, -1, 1],   '卯': [3, 2, -1, -1, 1],
    '辰': [1, 1, 2, 0, -1],
    '巳': [1, 3, 2, -1, -1],   '午': [1, 3, 2, -1, -1],
    '未': [-1, 1, 2, 1, -1],
    '申': [-1, -1, 1, 3, 2],   '酉': [-1, -1, 1, 3, 2],
    '戌': [-1, 0, 2, 1, -1],
    '亥': [2, -1, -1, 1, 3],   '子': [2, -1, -1, 1, 3],
    '丑': [-1, -1, 2, 1, 1]
  };

  var STRENGTH_LEVELS = {
    VERY_STRONG: '极旺',
    STRONG: '身强',
    NEUTRAL: '中和',
    WEAK: '身弱',
    VERY_WEAK: '极弱'
  };

  function analyzeDayMasterStrength(chart) {
    var C = _C();
    var dmElIdx = chart.dayMasterElementIndex;
    var score = 0;
    var factors = [];

    // 1. 得令
    var monthBranchChar = _branchChar(chart.monthPillar.branchIndex);
    var support = MONTH_SUPPORT[monthBranchChar];
    if (support) {
      var monthScore = support[dmElIdx];
      score += monthScore;
      if (monthScore > 0) {
        factors.push('得令: ' + monthBranchChar + '月生' + ELEMENT_NAMES[dmElIdx] + ' (+' + monthScore + ')');
      } else if (monthScore < 0) {
        factors.push('失令: ' + monthBranchChar + '月克' + ELEMENT_NAMES[dmElIdx] + ' (' + monthScore + ')');
      }
    }

    // 2. 得地
    var branchChecks = [
      { label: '年支', branchIdx: chart.yearPillar.branchIndex },
      { label: '日支', branchIdx: chart.dayPillar.branchIndex },
      { label: '时支', branchIdx: chart.hourPillar.branchIndex }
    ];
    for (var bi = 0; bi < branchChecks.length; bi++) {
      var bCheck = branchChecks[bi];
      var hidden = _C().getHiddenStemIndices(bCheck.branchIdx);
      for (var hi = 0; hi < hidden.length; hi++) {
        var hsElIdx = C.stemElement(hidden[hi]);
        if (hsElIdx === dmElIdx) {
          score += 0.5;
          factors.push('得地: ' + bCheck.label + _branchChar(bCheck.branchIdx) +
            '藏' + _stemChar(hidden[hi]) + '(' + ELEMENT_NAMES[dmElIdx] + ') (+0.5)');
        } else if (C.elementProduces(hsElIdx) === dmElIdx) {
          score += 0.3;
          factors.push('得地: ' + bCheck.label + '藏干生日主 (+0.3)');
        }
      }
    }

    // 3. 得势
    var stemChecks = [
      { label: '年干', stemIdx: chart.yearPillar.stemIndex },
      { label: '月干', stemIdx: chart.monthPillar.stemIndex },
      { label: '时干', stemIdx: chart.hourPillar.stemIndex }
    ];
    for (var si = 0; si < stemChecks.length; si++) {
      var sCheck = stemChecks[si];
      var sElIdx = C.stemElement(sCheck.stemIdx);
      if (sElIdx === dmElIdx) {
        score += 1.0;
        factors.push('得势: ' + sCheck.label + _stemChar(sCheck.stemIdx) + '比劫 (+1.0)');
      } else if (C.elementProduces(sElIdx) === dmElIdx) {
        score += 0.7;
        factors.push('得势: ' + sCheck.label + _stemChar(sCheck.stemIdx) + '生日主 (+0.7)');
      }
    }

    var level;
    if (score >= 6) level = STRENGTH_LEVELS.VERY_STRONG;
    else if (score >= 3) level = STRENGTH_LEVELS.STRONG;
    else if (score >= 1) level = STRENGTH_LEVELS.NEUTRAL;
    else if (score >= -1) level = STRENGTH_LEVELS.WEAK;
    else level = STRENGTH_LEVELS.VERY_WEAK;

    return {
      score: score,
      level: level,
      isStrong: score >= 1.5,
      factors: factors
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  胎元 (Taiyuan / Conception Pillar)
  // ════════════════════════════════════════════════════════════════

  /**
   * 胎元 = 月柱天干进一位 + 月柱地支进三位
   */
  function computeTaiyuan(chart) {
    var mStem = chart.monthPillar.stemIndex;
    var mBranch = chart.monthPillar.branchIndex;
    var stemIdx = (mStem + 1) % 10;
    var branchIdx = (mBranch + 3) % 12;
    var jiaziIdx = _stemBranchToJiazi(stemIdx, branchIdx);
    return {
      stemIndex: stemIdx,
      branchIndex: branchIdx,
      char: _jiaziChar(stemIdx, branchIdx),
      jiaziIndex: jiaziIdx,
      nayin: getNayin(jiaziIdx)
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  命宫 (Minggong / Life Palace)
  // ════════════════════════════════════════════════════════════════

  /**
   * 命宫计算:
   * 从卯宫起正月(寅月)逆数到出生月, 再从出生月起子时顺数到出生时辰.
   * 公式: 命宫地支 = (4 - monthNumber + hourBranchIndex + 12) % 12
   * 命宫天干: 用五虎遁月法从年干推算
   */
  function computeMinggong(chart) {
    var monthNum = chart.monthPillar.monthNumber || (MONTH_BRANCH_INDICES.indexOf(chart.monthPillar.branchIndex) + 1);
    var hourBranch = chart.hourPillar.branchIndex;

    var branchIdx = _mod(4 - monthNum + hourBranch, 12);

    // 命宫天干: 找到命宫所对应的月份序号, 用五虎遁月法
    var mgMonthNum = MONTH_BRANCH_INDICES.indexOf(branchIdx) + 1;
    if (mgMonthNum <= 0) mgMonthNum = 1;
    var baseStem = WUHU_TABLE[chart.yearPillar.stemIndex % 5];
    var stemIdx = (baseStem + mgMonthNum - 1) % 10;
    var jiaziIdx = _stemBranchToJiazi(stemIdx, branchIdx);

    return {
      stemIndex: stemIdx,
      branchIndex: branchIdx,
      char: _jiaziChar(stemIdx, branchIdx),
      jiaziIndex: jiaziIdx,
      nayin: getNayin(jiaziIdx)
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  神煞 (Shensha / Divine Stars)
  // ════════════════════════════════════════════════════════════════

  /**
   * 天乙贵人: 甲戊庚牛羊(丑未), 乙己鼠猴乡(子申),
   *           丙丁猪鸡位(亥酉), 壬癸兔蛇藏(卯巳),
   *           六辛逢马虎(午寅).
   * day stem index → [branch indices]
   */
  var TIANYI_GUIREN = {
    0: [1, 7],  1: [0, 8],  2: [11, 9], 3: [11, 9], 4: [1, 7],
    5: [0, 8],  6: [1, 7],  7: [6, 2],  8: [3, 5],  9: [3, 5]
  };

  /** 文昌贵人: day stem index → branch index */
  var WENCHANG = [5, 6, 8, 9, 8, 9, 11, 0, 2, 3];

  /** 禄神: day stem index → branch index */
  var LUSHEN = [2, 3, 5, 6, 5, 6, 8, 9, 11, 0];

  /** 羊刃: day stem index → branch index (禄前一位) */
  var YANGREN = [3, 4, 6, 7, 6, 7, 9, 10, 0, 1];

  /** 三合局 groups for 驿马/桃花/华盖/将星 */
  var SANHE_GROUPS = [[8, 0, 4], [11, 3, 7], [2, 6, 10], [5, 9, 1]];
  var YIMA_RESULT = [2, 5, 8, 11];     // 驿马
  var TAOHUA_RESULT = [9, 0, 3, 6];    // 桃花
  var HUAGAI_RESULT = [4, 7, 10, 1];   // 华盖
  var JIANGXING_RESULT = [0, 3, 6, 9]; // 将星

  /** 天德: month branch index → stem char (if pillar stem matches, 天德 present) */
  var TIANDE = {
    2: '丁', 3: '申', 4: '壬', 5: '辛', 6: '亥', 7: '甲',
    8: '癸', 9: '寅', 10: '丙', 11: '乙', 0: '巳', 1: '庚'
  };

  /** 月德: month branch → stem char */
  var YUEDE_MAP = {
    2: '丙', 3: '甲', 4: '壬', 5: '庚', 6: '丙', 7: '甲',
    8: '壬', 9: '庚', 10: '丙', 11: '甲', 0: '壬', 1: '庚'
  };

  /** Find which 三合 group a branch belongs to. */
  function _sanheGroup(branchIdx) {
    for (var i = 0; i < SANHE_GROUPS.length; i++) {
      if (SANHE_GROUPS[i].indexOf(branchIdx) !== -1) return i;
    }
    return 0;
  }

  /**
   * Compute all 神煞 for a chart.
   * Returns array of { name, pillar, branch, description }.
   */
  function computeShensha(chart) {
    var result = [];
    var dmStem = chart.dayMasterIndex;
    var yearBranch = chart.yearPillar.branchIndex;
    var dayBranch = chart.dayPillar.branchIndex;
    var monthBranch = chart.monthPillar.branchIndex;
    var allBranches = chart.allBranches;
    var allStems = chart.allStems;
    var pillarNames = ['年', '月', '日', '时'];

    // 天乙贵人 (based on day stem, check all branches)
    var tianyiBranches = TIANYI_GUIREN[dmStem] || [];
    for (var i = 0; i < 4; i++) {
      if (tianyiBranches.indexOf(allBranches[i]) !== -1) {
        result.push({ name: '天乙贵人', pillar: pillarNames[i], branch: _branchChar(allBranches[i]) });
      }
    }

    // 文昌贵人 (based on day stem, check all branches)
    var wcBranch = WENCHANG[dmStem];
    for (var w = 0; w < 4; w++) {
      if (allBranches[w] === wcBranch) {
        result.push({ name: '文昌贵人', pillar: pillarNames[w], branch: _branchChar(allBranches[w]) });
      }
    }

    // 驿马 (based on day branch or year branch)
    var yimaTarget = YIMA_RESULT[_sanheGroup(dayBranch)];
    for (var ym = 0; ym < 4; ym++) {
      if (allBranches[ym] === yimaTarget) {
        result.push({ name: '驿马', pillar: pillarNames[ym], branch: _branchChar(allBranches[ym]) });
      }
    }

    // 桃花 (based on day branch or year branch)
    var thTarget = TAOHUA_RESULT[_sanheGroup(dayBranch)];
    for (var th = 0; th < 4; th++) {
      if (allBranches[th] === thTarget) {
        result.push({ name: '桃花', pillar: pillarNames[th], branch: _branchChar(allBranches[th]) });
      }
    }

    // 华盖 (based on day branch or year branch)
    var hgTarget = HUAGAI_RESULT[_sanheGroup(dayBranch)];
    for (var hg = 0; hg < 4; hg++) {
      if (allBranches[hg] === hgTarget) {
        result.push({ name: '华盖', pillar: pillarNames[hg], branch: _branchChar(allBranches[hg]) });
      }
    }

    // 将星 (based on year branch)
    var jsTarget = JIANGXING_RESULT[_sanheGroup(yearBranch)];
    for (var js = 0; js < 4; js++) {
      if (allBranches[js] === jsTarget) {
        result.push({ name: '将星', pillar: pillarNames[js], branch: _branchChar(allBranches[js]) });
      }
    }

    // 天德 (based on month branch, check all stems)
    var tdStemChar = TIANDE[monthBranch];
    if (tdStemChar) {
      for (var td = 0; td < 4; td++) {
        if (_stemChar(allStems[td]) === tdStemChar) {
          result.push({ name: '天德', pillar: pillarNames[td], branch: _stemChar(allStems[td]) });
        }
      }
    }

    // 月德 (based on month branch, check all stems)
    var ydStemChar = YUEDE_MAP[monthBranch];
    if (ydStemChar) {
      for (var yd = 0; yd < 4; yd++) {
        if (_stemChar(allStems[yd]) === ydStemChar) {
          result.push({ name: '月德', pillar: pillarNames[yd], branch: _stemChar(allStems[yd]) });
        }
      }
    }

    // 禄神 (based on day stem, check all branches)
    var luTarget = LUSHEN[dmStem];
    for (var lu = 0; lu < 4; lu++) {
      if (allBranches[lu] === luTarget) {
        result.push({ name: '禄神', pillar: pillarNames[lu], branch: _branchChar(allBranches[lu]) });
      }
    }

    // 羊刃 (based on day stem, check all branches)
    var yrTarget = YANGREN[dmStem];
    for (var yr = 0; yr < 4; yr++) {
      if (allBranches[yr] === yrTarget) {
        result.push({ name: '羊刃', pillar: pillarNames[yr], branch: _branchChar(allBranches[yr]) });
      }
    }

    return result;
  }

  // ════════════════════════════════════════════════════════════════
  //  大运 (Luck Pillars)
  // ════════════════════════════════════════════════════════════════

  /**
   * Compute 大运 with precise start age.
   * Direction: male+yang OR female+yin → forward.
   * Start age: days to nearest 节 ÷ 3.
   */
  function computeLuckPillars(chart, numPillars) {
    if (!numPillars) numPillars = 8;
    var C = _C();

    var yearStemIdx = chart.yearPillar.stemIndex;
    var yearIsYang = (yearStemIdx % 2 === 0);
    var isMale = (chart.gender === 'male' || chart.gender === '男');
    var isForward = (yearIsYang && isMale) || (!yearIsYang && !isMale);
    var direction = isForward ? '顺行' : '逆行';

    // Find nearest 节 boundary
    var birth = Date.UTC(chart.birthYear, chart.birthMonth - 1, chart.birthDay, chart.birthHour, chart.birthMinute || 0);
    var bounds = C.monthWindow(birth);
    var jie = isForward && birth !== bounds.previous.millis ? bounds.next : bounds.previous;
    var startAge = Math.max(1, Math.floor(Math.abs(jie.millis - birth) / (3 * 86400000)));

    // Birth year for computing calendar years
    var birthYear = chart.birthYear;

    var monthIdx = chart.monthPillar.jiaziIndex;
    var pillars = [];
    for (var i = 0; i < numPillars; i++) {
      var idx;
      if (isForward) {
        idx = _mod(monthIdx + i + 1, 60);
      } else {
        idx = _mod(monthIdx - i - 1, 60);
      }
      var stemIdx = idx % 10;
      var branchIdx = idx % 12;
      var age = startAge + i * 10;
      pillars.push({
        stemIndex: stemIdx,
        branchIndex: branchIdx,
        char: _jiaziChar(stemIdx, branchIdx),
        jiaziIndex: idx,
        nayin: getNayin(idx),
        startAge: age,
        endAge: age + 9,
        startYear: birthYear + age,
        endYear: birthYear + age + 9
      });
    }

    return {
      pillars: pillars,
      startAge: startAge,
      direction: direction,
      isForward: isForward
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  流年 (Flow Years)
  // ════════════════════════════════════════════════════════════════

  function computeFlowYears(chart, startYear, count) {
    if (!count) count = 10;
    var dm = chart.dayMasterIndex;
    var results = [];

    for (var i = 0; i < count; i++) {
      var y = startYear + i;
      var idx = _mod(y - 4, 60);
      var stemIdx = idx % 10;
      var branchIdx = idx % 12;
      results.push({
        year: y,
        stemIndex: stemIdx,
        branchIndex: branchIdx,
        char: _jiaziChar(stemIdx, branchIdx),
        jiaziIndex: idx,
        nayin: getNayin(idx),
        tenGod: computeTenGod(dm, stemIdx)
      });
    }
    return results;
  }

  // ════════════════════════════════════════════════════════════════
  //  刑冲合害 (Branch Relationships)
  // ════════════════════════════════════════════════════════════════

  var REL_SIX_HARMONIES = [
    ['子', '丑', '土'], ['寅', '亥', '木'], ['卯', '戌', '火'],
    ['辰', '酉', '金'], ['巳', '申', '水'], ['午', '未', '火']
  ];
  var REL_THREE_HARMONIES = [
    ['申', '子', '辰', '水'], ['亥', '卯', '未', '木'],
    ['寅', '午', '戌', '火'], ['巳', '酉', '丑', '金']
  ];
  var REL_SIX_CONFLICTS = [
    ['子', '午'], ['丑', '未'], ['寅', '申'],
    ['卯', '酉'], ['辰', '戌'], ['巳', '亥']
  ];
  var REL_THREE_PUNISHMENTS = [
    ['寅', '巳', '申'], ['丑', '戌', '未'],
    ['子', '卯'],
    ['辰', '辰'], ['午', '午'], ['酉', '酉'], ['亥', '亥']
  ];
  var REL_SIX_HARMS = [
    ['子', '未'], ['丑', '午'], ['寅', '巳'],
    ['卯', '辰'], ['申', '亥'], ['酉', '戌']
  ];

  function analyzeRelationships(branchIndices) {
    var chars = branchIndices.map(function (idx) { return _branchChar(idx); });
    var relationships = [];

    // 六合
    REL_SIX_HARMONIES.forEach(function (sh) {
      if (chars.indexOf(sh[0]) !== -1 && chars.indexOf(sh[1]) !== -1) {
        relationships.push({
          kind: '六合', branches: [sh[0], sh[1]],
          resultElement: sh[2], description: sh[0] + sh[1] + '合' + sh[2]
        });
      }
    });

    // 三合 / 半三合
    REL_THREE_HARMONIES.forEach(function (th) {
      var found = [];
      for (var ti = 0; ti < 3; ti++) {
        if (chars.indexOf(th[ti]) !== -1) found.push(th[ti]);
      }
      if (found.length >= 2) {
        relationships.push({
          kind: found.length === 3 ? '三合' : '半三合',
          branches: found, resultElement: th[3],
          description: found.join('') + (found.length === 3 ? '三合' : '半合') + th[3] + '局'
        });
      }
    });

    // 六冲
    REL_SIX_CONFLICTS.forEach(function (sc) {
      if (chars.indexOf(sc[0]) !== -1 && chars.indexOf(sc[1]) !== -1) {
        relationships.push({
          kind: '六冲', branches: [sc[0], sc[1]], description: sc[0] + sc[1] + '相冲'
        });
      }
    });

    // 三刑 / 自刑
    REL_THREE_PUNISHMENTS.forEach(function (pg) {
      if (pg.length === 3) {
        var pFound = [];
        for (var pi = 0; pi < 3; pi++) {
          if (chars.indexOf(pg[pi]) !== -1) pFound.push(pg[pi]);
        }
        if (pFound.length >= 2) {
          relationships.push({ kind: '三刑', branches: pFound, description: pFound.join('') + '相刑' });
        }
      } else if (pg[0] === pg[1]) {
        var count = 0;
        for (var ci = 0; ci < chars.length; ci++) {
          if (chars[ci] === pg[0]) count++;
        }
        if (count >= 2) {
          relationships.push({ kind: '自刑', branches: [pg[0], pg[1]], description: pg[0] + '自刑' });
        }
      } else {
        if (chars.indexOf(pg[0]) !== -1 && chars.indexOf(pg[1]) !== -1) {
          relationships.push({ kind: '相刑', branches: [pg[0], pg[1]], description: pg[0] + pg[1] + '相刑' });
        }
      }
    });

    // 六害
    REL_SIX_HARMS.forEach(function (shm) {
      if (chars.indexOf(shm[0]) !== -1 && chars.indexOf(shm[1]) !== -1) {
        relationships.push({ kind: '六害', branches: [shm[0], shm[1]], description: shm[0] + shm[1] + '相害' });
      }
    });

    return { branches: chars, relationships: relationships };
  }

  // ════════════════════════════════════════════════════════════════
  //  格局分析 (Pattern Analysis)
  // ════════════════════════════════════════════════════════════════

  /**
   * Determine chart pattern (格局) based on month branch's main hidden stem.
   */
  function analyzePattern(chart, strength) {
    var C = _C();
    var dm = chart.dayMasterIndex;
    var monthBranch = chart.monthPillar.branchIndex;
    var hidden = C.getHiddenStemIndices(monthBranch);
    if (!strength) strength = analyzeDayMasterStrength(chart);

    // Check for 建禄格 and 羊刃格 first
    var luTarget = LUSHEN[dm];
    var yrTarget = YANGREN[dm];
    if (monthBranch === luTarget) {
      return { pattern: '建禄格', description: '月支为日主之禄，自身力量强，喜财官泄秀。' };
    }
    if (monthBranch === yrTarget) {
      return { pattern: '羊刃格', description: '月支为日主之羊刃，性格刚强，宜官杀制刃。' };
    }

    // Use month branch's main hidden stem (透干优先)
    // Check if any hidden stem is 透出 (appears in year/month/hour stem)
    var monthStem = chart.monthPillar.stemIndex;
    var otherStems = [chart.yearPillar.stemIndex, monthStem, chart.hourPillar.stemIndex];
    var patternStem = -1;

    for (var h = 0; h < hidden.length; h++) {
      for (var s = 0; s < otherStems.length; s++) {
        if (hidden[h] === otherStems[s] && hidden[h] !== dm) {
          patternStem = hidden[h];
          break;
        }
      }
      if (patternStem >= 0) break;
    }

    // Fallback to main hidden stem
    if (patternStem < 0 && hidden.length > 0) {
      patternStem = hidden[0];
      if (patternStem === dm && hidden.length > 1) patternStem = hidden[1];
    }

    if (patternStem < 0) {
      return { pattern: '杂气格', description: '格局不纯，需综合分析。' };
    }

    var tenGod = computeTenGod(dm, patternStem);
    var patternName = tenGod + '格';
    var descriptions = {
      '比肩格': '月令比肩当权，自立自强，宜官杀财星调候。',
      '劫财格': '月令劫财旺盛，争夺之象，宜官杀制之。',
      '食神格': '食神制杀，秀气流通，文雅有才华。',
      '伤官格': '伤官见官，是非纷争；伤官生财则富。',
      '偏财格': '偏财格主慷慨大方，善于理财。',
      '正财格': '正财格主勤俭持家，稳健守成。',
      '七杀格': '七杀格主威严果断，宜食神制杀。',
      '正官格': '正官格主端正守礼，利于仕途。',
      '偏印格': '偏印格主聪慧多思，但易犹豫不决。',
      '正印格': '正印格主仁厚好学，文昌之命。'
    };

    return {
      pattern: patternName,
      description: descriptions[patternName] || '格局以' + tenGod + '为用，需结合全局分析。',
      keyGod: tenGod
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  用神/忌神建议 (Favorable Element Suggestion)
  // ════════════════════════════════════════════════════════════════

  /**
   * Suggest favorable (用神) and unfavorable (忌神) elements.
   * Simplified: based on Day Master strength.
   */
  function suggestFavorable(chart, strength, elements) {
    var C = _C();
    var dmElIdx = chart.dayMasterElementIndex;
    if (!strength) strength = analyzeDayMasterStrength(chart);
    if (!elements) elements = analyzeFiveElements(chart.allStems, chart.allBranches);

    // Element that produces DM (印)
    var producerIdx = -1;
    for (var i = 0; i < 5; i++) {
      if (C.elementProduces(i) === dmElIdx) { producerIdx = i; break; }
    }
    // Element that DM produces (食伤)
    var childIdx = C.elementProduces(dmElIdx);
    // Element that DM conquers (财)
    var wealthIdx = C.elementConquers(dmElIdx);
    // Element that conquers DM (官杀)
    var officerIdx = -1;
    for (var j = 0; j < 5; j++) {
      if (C.elementConquers(j) === dmElIdx) { officerIdx = j; break; }
    }

    var favorable = [];
    var unfavorable = [];

    if (strength.isStrong) {
      // 身强: 用神 = 克泄耗 (官杀, 食伤, 财)
      if (officerIdx >= 0) favorable.push(ELEMENT_NAMES[officerIdx] + '(官杀)');
      if (childIdx >= 0) favorable.push(ELEMENT_NAMES[childIdx] + '(食伤)');
      if (wealthIdx >= 0) favorable.push(ELEMENT_NAMES[wealthIdx] + '(财)');
      // 忌神 = 生扶 (印, 比劫)
      if (producerIdx >= 0) unfavorable.push(ELEMENT_NAMES[producerIdx] + '(印)');
      unfavorable.push(ELEMENT_NAMES[dmElIdx] + '(比劫)');
    } else {
      // 身弱: 用神 = 生扶 (印, 比劫)
      if (producerIdx >= 0) favorable.push(ELEMENT_NAMES[producerIdx] + '(印)');
      favorable.push(ELEMENT_NAMES[dmElIdx] + '(比劫)');
      // 忌神 = 克泄耗
      if (officerIdx >= 0) unfavorable.push(ELEMENT_NAMES[officerIdx] + '(官杀)');
      if (childIdx >= 0) unfavorable.push(ELEMENT_NAMES[childIdx] + '(食伤)');
      if (wealthIdx >= 0) unfavorable.push(ELEMENT_NAMES[wealthIdx] + '(财)');
    }

    return {
      favorable: favorable,
      unfavorable: unfavorable,
      suggestion: strength.isStrong
        ? '日主偏强，宜用' + favorable.join('、') + '克泄耗之。'
        : '日主偏弱，宜用' + favorable.join('、') + '生扶助之。'
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  农历转换 (Lunar Date)
  // ════════════════════════════════════════════════════════════════

  /** Get lunar date info for a solar date. */
  function getLunarDate(year, month, day) {
    var C = _C();
    var lunar = C.solarToLunar(year, month, day);
    var traditional = C.formatLunarDateTraditional(year, month, day);
    return {
      year: lunar.year,
      month: lunar.month,
      day: lunar.day,
      isLeap: lunar.isLeap,
      traditional: traditional
    };
  }

  // ════════════════════════════════════════════════════════════════
  //  Public API
  // ════════════════════════════════════════════════════════════════

  return {
    // 四柱
    computeYearPillar: computeYearPillar,
    computeMonthPillar: computeMonthPillar,
    computeDayPillar: computeDayPillar,
    computeHourPillar: computeHourPillar,
    createChart: createChart,

    // 十神
    computeTenGod: computeTenGod,
    tenGodsFromChart: tenGodsFromChart,

    // 五行
    analyzeFiveElements: analyzeFiveElements,

    // 日主强弱
    analyzeDayMasterStrength: analyzeDayMasterStrength,

    // 纳音
    getNayin: getNayin,
    getNayinForChart: getNayinForChart,

    // 胎元
    computeTaiyuan: computeTaiyuan,

    // 命宫
    computeMinggong: computeMinggong,

    // 神煞
    computeShensha: computeShensha,

    // 大运
    computeLuckPillars: computeLuckPillars,

    // 流年
    computeFlowYears: computeFlowYears,

    // 刑冲合害
    analyzeRelationships: analyzeRelationships,

    // 格局
    analyzePattern: analyzePattern,

    // 用神
    suggestFavorable: suggestFavorable,

    // 农历
    getLunarDate: getLunarDate,

    // Constants
    ELEMENT_NAMES: ELEMENT_NAMES,
    HIDDEN_STEM_WEIGHTS: HIDDEN_STEM_WEIGHTS,
    STRENGTH_LEVELS: STRENGTH_LEVELS,
    NAYIN_TABLE: NAYIN_TABLE,
    WUHU_TABLE: WUHU_TABLE,
    WUSHU_TABLE: WUSHU_TABLE,
    MONTH_BRANCH_INDICES: MONTH_BRANCH_INDICES
  };
})();
