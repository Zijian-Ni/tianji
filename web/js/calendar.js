/**
 * tianji/calendar — 干支历法引擎 (Stem-Branch Calendar Engine)
 *
 * JavaScript port of the Python tianji.calendar package.
 *
 * Provides:
 *   - 天干 (Heavenly Stems): 甲乙丙丁戊己庚辛壬癸
 *   - 地支 (Earthly Branches): 子丑寅卯辰巳午未申酉戌亥
 *   - 干支 (Stem-Branch pairs): 六十甲子 cycle
 *   - 24节气 (Solar Terms) approximate calculation
 *   - 农历 (Lunar Calendar) via compressed lookup table
 *
 * Module pattern (IIFE) — exposes a single `Calendar` global.
 */
const Calendar = (function () {
  "use strict";

  // ────────────────────────────────────────────────────────────────────────
  // Five Elements (五行)
  // ────────────────────────────────────────────────────────────────────────

  var ELEMENTS = ["木", "火", "土", "金", "水"];

  /** 相生 — generation / production cycle */
  var ELEMENT_PRODUCES = {
    "木": "火",
    "火": "土",
    "土": "金",
    "金": "水",
    "水": "木"
  };

  /** 相克 — conquest / destruction cycle */
  var ELEMENT_CONQUERS = {
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "金": "木"
  };

  // ────────────────────────────────────────────────────────────────────────
  // Heavenly Stems (天干)
  // ────────────────────────────────────────────────────────────────────────

  /**
   * Each stem: { char, index, element, polarity }
   * polarity: "阳" (yang) or "阴" (yin)
   */
  var STEMS = [
    { char: "甲", index: 0, element: "木", polarity: "阳" },
    { char: "乙", index: 1, element: "木", polarity: "阴" },
    { char: "丙", index: 2, element: "火", polarity: "阳" },
    { char: "丁", index: 3, element: "火", polarity: "阴" },
    { char: "戊", index: 4, element: "土", polarity: "阳" },
    { char: "己", index: 5, element: "土", polarity: "阴" },
    { char: "庚", index: 6, element: "金", polarity: "阳" },
    { char: "辛", index: 7, element: "金", polarity: "阴" },
    { char: "壬", index: 8, element: "水", polarity: "阳" },
    { char: "癸", index: 9, element: "水", polarity: "阴" }
  ];

  /** Lookup map: char → stem object */
  var _stemByChar = {};
  STEMS.forEach(function (s) { _stemByChar[s.char] = s; });

  function getStem(index) {
    return STEMS[((index % 10) + 10) % 10];
  }

  function getStemByChar(ch) {
    if (!_stemByChar[ch]) { throw new Error("Unknown heavenly stem: " + ch); }
    return _stemByChar[ch];
  }

  // ────────────────────────────────────────────────────────────────────────
  // Earthly Branches (地支)
  // ────────────────────────────────────────────────────────────────────────

  /**
   * Each branch: { char, index, element, polarity, zodiac, hourRange, hiddenStems }
   * hiddenStems is an array of stem characters (藏干).
   */
  var BRANCHES = [
    { char: "子", index: 0,  element: "水", polarity: "阳", zodiac: "鼠", hourRange: "23:00-01:00", hiddenStems: ["癸"] },
    { char: "丑", index: 1,  element: "土", polarity: "阴", zodiac: "牛", hourRange: "01:00-03:00", hiddenStems: ["己", "癸", "辛"] },
    { char: "寅", index: 2,  element: "木", polarity: "阳", zodiac: "虎", hourRange: "03:00-05:00", hiddenStems: ["甲", "丙", "戊"] },
    { char: "卯", index: 3,  element: "木", polarity: "阴", zodiac: "兔", hourRange: "05:00-07:00", hiddenStems: ["乙"] },
    { char: "辰", index: 4,  element: "土", polarity: "阳", zodiac: "龙", hourRange: "07:00-09:00", hiddenStems: ["戊", "乙", "癸"] },
    { char: "巳", index: 5,  element: "火", polarity: "阴", zodiac: "蛇", hourRange: "09:00-11:00", hiddenStems: ["丙", "庚", "戊"] },
    { char: "午", index: 6,  element: "火", polarity: "阳", zodiac: "马", hourRange: "11:00-13:00", hiddenStems: ["丁", "己"] },
    { char: "未", index: 7,  element: "土", polarity: "阴", zodiac: "羊", hourRange: "13:00-15:00", hiddenStems: ["己", "丁", "乙"] },
    { char: "申", index: 8,  element: "金", polarity: "阳", zodiac: "猴", hourRange: "15:00-17:00", hiddenStems: ["庚", "壬", "戊"] },
    { char: "酉", index: 9,  element: "金", polarity: "阴", zodiac: "鸡", hourRange: "17:00-19:00", hiddenStems: ["辛"] },
    { char: "戌", index: 10, element: "土", polarity: "阳", zodiac: "狗", hourRange: "19:00-21:00", hiddenStems: ["戊", "辛", "丁"] },
    { char: "亥", index: 11, element: "水", polarity: "阴", zodiac: "猪", hourRange: "21:00-23:00", hiddenStems: ["壬", "甲"] }
  ];

  var _branchByChar = {};
  BRANCHES.forEach(function (b) { _branchByChar[b.char] = b; });

  function getBranch(index) {
    return BRANCHES[((index % 12) + 12) % 12];
  }

  function getBranchByChar(ch) {
    if (!_branchByChar[ch]) { throw new Error("Unknown earthly branch: " + ch); }
    return _branchByChar[ch];
  }

  /**
   * Get the earthly branch for a clock hour (0-23).
   * 子 23,0 | 丑 1,2 | 寅 3,4 | … | 亥 21,22
   */
  function getBranchForHour(hour) {
    if (hour === 23) { return BRANCHES[0]; }
    return BRANCHES[Math.floor((hour + 1) / 2)];
  }

  /**
   * Return the hidden stem objects for a branch.
   */
  function getHiddenStems(branch) {
    return branch.hiddenStems.map(function (ch) { return getStemByChar(ch); });
  }

  // ────────────────────────────────────────────────────────────────────────
  // Branch relationships
  // ────────────────────────────────────────────────────────────────────────

  /** 六合 — Six Harmonies (pairs that combine) */
  var SIX_HARMONIES = [
    { a: "子", b: "丑", element: "土" },
    { a: "寅", b: "亥", element: "木" },
    { a: "卯", b: "戌", element: "火" },
    { a: "辰", b: "酉", element: "金" },
    { a: "巳", b: "申", element: "水" },
    { a: "午", b: "未", element: "火" }
  ];

  /** 三合 — Three Harmonies (triads) */
  var THREE_HARMONIES = [
    { a: "申", b: "子", c: "辰", element: "水" },
    { a: "亥", b: "卯", c: "未", element: "木" },
    { a: "寅", b: "午", c: "戌", element: "火" },
    { a: "巳", b: "酉", c: "丑", element: "金" }
  ];

  /** 六冲 — Six Conflicts (opposing branches) */
  var SIX_CONFLICTS = [
    ["子", "午"], ["丑", "未"], ["寅", "申"],
    ["卯", "酉"], ["辰", "戌"], ["巳", "亥"]
  ];

  /** 三刑 — Three Punishments */
  var THREE_PUNISHMENTS = [
    ["寅", "巳", "申"],   // 无恩之刑
    ["丑", "戌", "未"],   // 持势之刑
    ["子", "卯"],          // 无礼之刑
    ["辰", "辰"],          // 自刑
    ["午", "午"],
    ["酉", "酉"],
    ["亥", "亥"]
  ];

  /** 六害 — Six Harms */
  var SIX_HARMS = [
    ["子", "未"], ["丑", "午"], ["寅", "巳"],
    ["卯", "辰"], ["申", "亥"], ["酉", "戌"]
  ];

  // ────────────────────────────────────────────────────────────────────────
  // Ten Gods (十神) — stem relationship
  // ────────────────────────────────────────────────────────────────────────

  /**
   * Compute the relationship of `other` stem relative to Day Master `dm`.
   * Returns the Chinese name of the Ten God (十神).
   *
   * @param {object} dm    — Day Master stem object
   * @param {object} other — Another stem object
   * @returns {string} Ten God name
   */
  function stemRelationship(dm, other) {
    var sameElement  = dm.element === other.element;
    var samePolarity = dm.polarity === other.polarity;
    var dmProduces   = ELEMENT_PRODUCES[dm.element] === other.element;
    var producesDm   = ELEMENT_PRODUCES[other.element] === dm.element;
    var dmConquers   = ELEMENT_CONQUERS[dm.element] === other.element;
    var conquersDm   = ELEMENT_CONQUERS[other.element] === dm.element;

    if (sameElement)  { return samePolarity ? "比肩" : "劫财"; }
    if (dmProduces)   { return samePolarity ? "食神" : "伤官"; }
    if (producesDm)   { return samePolarity ? "偏印" : "正印"; }
    if (dmConquers)   { return samePolarity ? "偏财" : "正财"; }
    if (conquersDm)   { return samePolarity ? "七杀" : "正官"; }

    throw new Error("Cannot determine relationship between " + dm.char + " and " + other.char);
  }

  // ────────────────────────────────────────────────────────────────────────
  // 六十甲子 (60-Cycle / Jiazi)
  // ────────────────────────────────────────────────────────────────────────

  /** Build all 60 stem-branch pairs. */
  var JIAZI_CYCLE = [];
  (function () {
    for (var i = 0; i < 60; i++) {
      JIAZI_CYCLE.push({
        stem:   getStem(i % 10),
        branch: getBranch(i % 12),
        index:  i,
        char:   getStem(i % 10).char + getBranch(i % 12).char
      });
    }
  })();

  var _jiaziByChar = {};
  JIAZI_CYCLE.forEach(function (sb) { _jiaziByChar[sb.char] = sb; });

  function getJiazi(index) {
    return JIAZI_CYCLE[((index % 60) + 60) % 60];
  }

  function getJiaziByChar(ch) {
    if (!_jiaziByChar[ch]) { throw new Error("Unknown stem-branch: " + ch); }
    return _jiaziByChar[ch];
  }

  // Reference epoch: 1900-01-01 = 甲戌 (index 10)
  // Verified: with index 10, 1949-10-01 = 甲子, 2004-07-21 = 辛丑
  var _REFERENCE_DATE = new Date(Date.UTC(1900, 0, 1)); // months are 0-based
  var _REFERENCE_INDEX = 10;

  /**
   * Number of whole days between two UTC-midnight Date objects.
   */
  function _daysBetween(a, b) {
    var MS_PER_DAY = 86400000;
    return Math.round((b.getTime() - a.getTime()) / MS_PER_DAY);
  }

  /**
   * Create a UTC Date from (year, month, day). month is 1-based.
   */
  function _utcDate(y, m, d) {
    return new Date(Date.UTC(y, m - 1, d));
  }

  /**
   * Convert a JS Date (or {year,month,day}) to its 60-cycle index.
   */
  function jiaziIndexForDate(d) {
    d = d instanceof Date ? _utcDate(d.getFullYear(), d.getMonth() + 1, d.getDate()) : _utcDate(d.year, d.month, d.day);
    var delta = _daysBetween(_REFERENCE_DATE, d);
    return ((_REFERENCE_INDEX + delta) % 60 + 60) % 60;
  }

  /**
   * Get the StemBranch for a given date (day pillar).
   */
  function dateToJiazi(d) {
    return getJiazi(jiaziIndexForDate(d));
  }

  // ────────────────────────────────────────────────────────────────────────
  // 24 Solar Terms (二十四节气)
  // ────────────────────────────────────────────────────────────────────────

  var SOLAR_TERMS = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
  ];

  /** Solar longitude for each term. 小寒=285°, each +15°. */
  var _TERM_LONGITUDES = {};
  SOLAR_TERMS.forEach(function (name, i) {
    _TERM_LONGITUDES[name] = (285 + i * 15) % 360;
  });

  /**
   * Approximate Julian Day when the sun reaches a given ecliptic longitude.
   * Uses Meeus simplified formula for the vernal equinox + mean-motion offset.
   */
  function _solarLongitudeToJDE(year, targetLon) {
    var Y = (year - 2000) / 1000.0;
    var jdeEquinox = 2451623.80984
                   + 365242.37404 * Y
                   + 0.05169 * Y * Y
                   - 0.00411 * Y * Y * Y
                   - 0.00057 * Y * Y * Y * Y;

    var deltaLon = targetLon;
    if (deltaLon < 0)   { deltaLon += 360; }
    if (deltaLon > 180) { deltaLon -= 360; }

    var daysApprox = deltaLon / (360.0 / 365.25);
    return jdeEquinox + daysApprox;
  }

  /**
   * Convert Julian Day Number to a UTC Date object.
   * JDE 2451545.0 = 2000-01-01 12:00 UTC.
   */
  function _jdeToDate(jde) {
    var MS_PER_DAY = 86400000;
    var deltaDays = jde - 2451545.0;
    // 2000-01-01 12:00 UTC
    var baseMs = Date.UTC(2000, 0, 1, 12, 0, 0);
    var ms = baseMs + deltaDays * MS_PER_DAY;
    return new Date(ms);
  }

  /**
   * Get the approximate date of a solar term for a given year.
   * Accuracy: +/- 1-2 days for 1900-2100.
   *
   * @param {number} year — Gregorian year
   * @param {string} term — Solar term name (e.g. "立春")
   * @returns {{ year, month, day }} date components (UTC)
   */
  function approximateSolarTermDate(year, term) {
    if (_TERM_LONGITUDES[term] === undefined) {
      throw new Error("Unknown solar term: " + term);
    }
    var lon = _TERM_LONGITUDES[term];
    var jde = _solarLongitudeToJDE(year, lon);
    var d   = _jdeToDate(jde);

    var resultYear = d.getUTCFullYear();

    // If the computed date ended up in a wrong year, try adjusting
    if (resultYear !== year) {
      var tryYear = (resultYear < year) ? year + 1 : year - 1;
      var jde2 = _solarLongitudeToJDE(tryYear, lon);
      var d2   = _jdeToDate(jde2);
      if (Math.abs(d2.getUTCFullYear() - year) < Math.abs(resultYear - year)) {
        d = d2;
      }
    }

    return { year: d.getUTCFullYear(), month: d.getUTCMonth() + 1, day: d.getUTCDate() };
  }

  const almanac = typeof TianjiAlmanac !== 'undefined' ? TianjiAlmanac : require('./almanac.js');

  // These millisecond values encode Beijing wall-clock fields in UTC slots.
  // Never feed them through local Date getters or device DST rules.
  function termWallMillis(year, name) {
    const termIndex = SOLAR_TERMS.indexOf(name);
    if (termIndex < 0) throw new RangeError('Unknown solar term: ' + name);
    const row = almanac.termMinutes[year - almanac.termStart];
    if (row) return Date.UTC(year, 0, 1) + row[termIndex] * 60000;
    const d = approximateSolarTermDate(year, name);
    return Date.UTC(d.year, d.month - 1, d.day);
  }

  function getSolarTermDate(year, term) {
    const d = new Date(termWallMillis(year, term));
    return { year: d.getUTCFullYear(), month: d.getUTCMonth() + 1, day: d.getUTCDate() };
  }

  function lichunDate(year) {
    return getSolarTermDate(year, '立春');
  }

  function monthWindow(wallMillis) {
    const d = new Date(wallMillis);
    const year = d.getUTCFullYear(), month = d.getUTCMonth();
    function boundary(offset) {
      const m = month + offset;
      const term = SOLAR_TERMS[((m + 12) % 12) * 2];
      return { term, millis: termWallMillis(year + Math.floor(m / 12), term) };
    }
    const current = boundary(0);
    return current.millis <= wallMillis
      ? { previous: current, next: boundary(1) }
      : { previous: boundary(-1), next: current };
  }

  /**
   * Get all 12 monthly boundary solar terms (节) for a given year.
   * These are the terms that start each Chinese month:
   *   立春, 惊蛰, 清明, 立夏, 芒种, 小暑, 立秋, 白露, 寒露, 立冬, 大雪, 小寒
   *
   * @returns {Array<{term: string, year: number, month: number, day: number}>}
   *          sorted by date
   */
  function getMonthBoundaryDates(year) {
    var monthlyTerms = [
      "立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
      "立秋", "白露", "寒露", "立冬", "大雪", "小寒"
    ];

    var results = monthlyTerms.map(function (term) {
      var d = getSolarTermDate(year, term);
      return { term: term, year: d.year, month: d.month, day: d.day };
    });

    results.sort(function (a, b) {
      return _utcDate(a.year, a.month, a.day) - _utcDate(b.year, b.month, b.day);
    });
    return results;
  }

  // ────────────────────────────────────────────────────────────────────────
  // Lunar months in civil-day order. A negative length marks a leap month.
  const lunarEpoch = Date.parse(almanac.lunarStart + 'T00:00:00Z');
  const lunarFirstYear = new Date(lunarEpoch).getUTCFullYear();
  const yearStarts = [0];
  for (const row of almanac.lunarMonths) {
    yearStarts.push(yearStarts[yearStarts.length - 1] + row.reduce((sum, n) => sum + Math.abs(n), 0));
  }

  function solarToLunar(year, month, day) {
    const target = _utcDate(year, month, day);
    let offset = (target.getTime() - lunarEpoch) / 86400000;
    if (!Number.isInteger(offset) || target.getUTCMonth() + 1 !== month || target.getUTCDate() !== day ||
        offset < 0 || offset >= yearStarts[yearStarts.length - 1]) {
      throw new RangeError('Invalid or unsupported Gregorian date');
    }
    let yearIndex = Math.min(year - lunarFirstYear, almanac.lunarMonths.length - 1);
    if (offset < yearStarts[yearIndex]) yearIndex--;
    offset -= yearStarts[yearIndex];
    let number = 0;
    for (const length of almanac.lunarMonths[yearIndex]) {
      if (length > 0) number++;
      if (offset < Math.abs(length)) {
        return { year: lunarFirstYear + yearIndex, month: number, day: offset + 1, isLeap: length < 0 };
      }
      offset -= Math.abs(length);
    }
    throw new RangeError('Incomplete lunar year');
  }

  function lunarToSolar(year, month, day, isLeap = false) {
    const index = year - lunarFirstYear;
    const months = almanac.lunarMonths[index];
    if (!months) throw new RangeError('Lunar year must be in 1900–2100');
    let offset = yearStarts[index], number = 0;
    for (const length of months) {
      if (length > 0) number++;
      if (number === month && (length < 0) === isLeap) {
        if (!Number.isInteger(day) || day < 1 || day > Math.abs(length)) throw new RangeError('Invalid lunar day');
        const d = new Date(lunarEpoch + (offset + day - 1) * 86400000);
        return { year: d.getUTCFullYear(), month: d.getUTCMonth() + 1, day: d.getUTCDate() };
      }
      offset += Math.abs(length);
    }
    throw new RangeError('Invalid lunar month');
  }

  var _LUNAR_DAY_NAMES = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
  ];

  var _LUNAR_MONTH_NAMES = [
    "正", "二", "三", "四", "五", "六",
    "七", "八", "九", "十", "冬", "腊"
  ];

  /**
   * Format a Gregorian date as a Chinese lunar date string.
   * @returns {string} e.g. "农历2024年正月初一"
   */
  function formatLunarDate(year, month, day) {
    var ld = solarToLunar(year, month, day);
    var leapStr = ld.isLeap ? "闰" : "";
    return "农历" + ld.year + "年" + leapStr + ld.month + "月" + ld.day + "日";
  }

  /**
   * Format a Gregorian date as a traditional Chinese lunar date string.
   * @returns {string} e.g. "农历2024年正月初一"
   */
  function formatLunarDateTraditional(year, month, day) {
    var ld = solarToLunar(year, month, day);
    var leapStr = ld.isLeap ? "闰" : "";
    var monthName = _LUNAR_MONTH_NAMES[ld.month - 1];
    var dayName   = _LUNAR_DAY_NAMES[ld.day - 1];
    return "农历" + ld.year + "年" + leapStr + monthName + "月" + dayName;
  }

  // ────────────────────────────────────────────────────────────────────────
  // Additional helpers for BaZi engine
  // ────────────────────────────────────────────────────────────────────────

  /**
   * Get the element index (0-4: 木火土金水) for a stem by index.
   */
  function stemElement(stemIndex) {
    var s = getStem(stemIndex);
    return ELEMENTS.indexOf(s.element);
  }

  /**
   * Get element index that `elIdx` produces (相生).
   * @param {number} elIdx — element index 0-4
   * @returns {number} produced element index
   */
  function elementProduces(elIdx) {
    var el = ELEMENTS[elIdx];
    return ELEMENTS.indexOf(ELEMENT_PRODUCES[el]);
  }

  /**
   * Get element index that `elIdx` conquers (相克).
   */
  function elementConquers(elIdx) {
    var el = ELEMENTS[elIdx];
    return ELEMENTS.indexOf(ELEMENT_CONQUERS[el]);
  }

  /**
   * Get 立春 Date object for a given year.
   * @returns {Date} — local time Date
   */
  function getLiChunDate(year) {
    var d = lichunDate(year);
    return new Date(d.year, d.month - 1, d.day);
  }

  /**
   * Get a solar term date as a local Date object.
   */
  function getSolarTermAsDate(year, termName) {
    var d = getSolarTermDate(year, termName);
    return new Date(d.year, d.month - 1, d.day);
  }

  /**
   * Get hidden stem indices for a branch by index.
   * @param {number} branchIndex — 0-11
   * @returns {number[]} array of stem indices
   */
  function getHiddenStemIndices(branchIndex) {
    var branch = getBranch(branchIndex);
    return branch.hiddenStems.map(function (ch) {
      return getStemByChar(ch).index;
    });
  }

  /**
   * Compute Ten God by stem indices (convenience wrapper).
   */
  function stemRelationshipByIndex(dmIndex, otherIndex) {
    return stemRelationship(getStem(dmIndex), getStem(otherIndex));
  }

  // ────────────────────────────────────────────────────────────────────────
  // Public API
  // ────────────────────────────────────────────────────────────────────────

  return {
    // Data tables
    STEMS:              STEMS,
    BRANCHES:           BRANCHES,
    ELEMENTS:           ELEMENTS,
    JIAZI_CYCLE:        JIAZI_CYCLE,
    SOLAR_TERMS:        SOLAR_TERMS,

    // Element cycles
    ELEMENT_PRODUCES:   ELEMENT_PRODUCES,
    ELEMENT_CONQUERS:   ELEMENT_CONQUERS,

    // Stem functions
    getStem:            getStem,
    getStemByChar:      getStemByChar,

    // Branch functions
    getBranch:          getBranch,
    getBranchByChar:    getBranchByChar,
    getBranchForHour:   getBranchForHour,
    getHiddenStems:     getHiddenStems,

    // 60-cycle functions
    getJiazi:           getJiazi,
    getJiaziByChar:     getJiaziByChar,
    dateToJiazi:        dateToJiazi,
    jiaziIndexForDate:  jiaziIndexForDate,

    // Solar terms
    getSolarTermDate:       getSolarTermDate,
    termWallMillis,
    monthWindow,
    lichunDate:             lichunDate,
    getMonthBoundaryDates:  getMonthBoundaryDates,

    // Lunar calendar
    solarToLunar:               solarToLunar,
    lunarToSolar:               lunarToSolar,
    formatLunarDate:            formatLunarDate,
    formatLunarDateTraditional: formatLunarDateTraditional,

    // Ten Gods
    stemRelationship:   stemRelationship,

    // Branch relationships
    SIX_HARMONIES:      SIX_HARMONIES,
    THREE_HARMONIES:    THREE_HARMONIES,
    SIX_CONFLICTS:      SIX_CONFLICTS,
    THREE_PUNISHMENTS:  THREE_PUNISHMENTS,
    SIX_HARMS:          SIX_HARMS,

    // Additional helpers
    stemElement:              stemElement,
    elementProduces:          elementProduces,
    elementConquers:          elementConquers,
    getLiChunDate:            getLiChunDate,
    getSolarTermAsDate:       getSolarTermAsDate,
    getHiddenStemIndices:     getHiddenStemIndices,
    stemRelationshipByIndex:  stemRelationshipByIndex
  };
})();

// Node.js / CommonJS export (no-op in browsers)
if (typeof module !== "undefined" && module.exports) {
  module.exports = Calendar;
}
