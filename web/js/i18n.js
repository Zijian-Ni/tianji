/**
 * i18n.js -- Internationalization module for Tianji (Chinese/English)
 *
 * IIFE that exposes I18n with:
 *   t(key)       - translate a key to current language
 *   setLang(l)   - switch language ('zh' or 'en')
 *   getLang()    - get current language code
 *   toggle()     - flip between zh/en, return new code
 *   translations - raw translation objects (for iteration)
 */
const I18n = (function () {
  'use strict';

  let currentLang = 'zh';

  const translations = {
    /* ================================================================ */
    /*  CHINESE                                                         */
    /* ================================================================ */
    zh: {
      atBoundary: "对照交节时刻", beforeBoundary: "对照交节前一分钟",
      skip: "跳到排盘",
      today: "今日",
      methods: "排盘方式",
      shareChart: "分享排盘",
      birthDetails: "生辰资料",
      solarDate: "公历日期",
      birthClock: "出生时间",
      clockRule: "北京时间 UTC+8，零点换日。性别用于确定大运顺逆。",
      boundaryExample: "立春交节示例",
      useNow: "用此刻",
      termBasis: "交节依据",
      method: "方式",
      castTime: "起卦时间（UTC+8）",
      lunarBirth: "农历生辰",
      ziweiRule: "采用农历生辰，闰月按本月安宫。",
      useBazi: "从八字生辰换算",
      offline: "本地计算 · 离线可用",
      shareDetail: "链接包含当前排盘资料，持有链接的人可以还原这张盘。",
      chartLink: "排盘链接",
      close: "关闭",
      lightAction: "浅色",
      darkAction: "深色",
      baziIntro: "输入公历出生时间，查看四柱、五行与交节时刻。",
      liuyaoIntro: "以时间、报数或铜钱起卦，对照本卦、动爻与变卦。",
      ziweiIntro: "以农历生辰安命身宫，查看十四主星在十二宫的分布。",
      invalidBirth: "请输入 1900-01-31 至 2100-12-31 之间的有效公历日期，并填写出生时间。",
      invalidLunar: "请检查农历日期。小月只有二十九天，闰月须与年份对应。",
      currentJie: "本月交节",
      nextJie: "下月交节",
      pillarsTitle: "四柱命盘",
      cycleTitle: "大运与流年",
      analysisTitle: "格局与神煞",
      stemInfo: "天干",
      branchInfo: "地支",
      yearShort: "年柱",
      monthShort: "月柱",
      dayShort: "日柱",
      hourShort: "时柱",
      strengthInfo: "强弱依据",
      pattern: "格局",
      fav: "用神",
      unfav: "忌神",
      aux: "神煞",
      taiyuan: "胎元",
      minggong: "命宫",
      shangong: "身宫",
      lunarMarker: "农历",
      leap: "闰",
      none: "无",
      elementNote: "按天干与地支藏干加权",
      cycleRule: "起运整岁估算 · 三天折一年",
      timeHint: "取农历年支、月、日和时支起卦。",
      numberHint: "前两数定上下卦，第三数定动爻。留空时取前两数之和。",
      coinHint: "每爻掷三枚铜钱，依次自初爻至上爻。六为老阴，九为老阳，遇六、九则变。",
      waitingCast: "等待起卦",
      waitingHint: "选择一种起卦方法，点「起卦」查看结果。",
      castSummary: "起卦结果",
      rawValues: "爻值",
      palacesTitle: "十二宫命盘",
      palaceJu: "五行局",
      resultCopyHint: "请选中并手动复制链接。",
      boundaryNote: "月柱在交节分钟切换",
      forward: "顺行",
      backward: "逆行",
      strongest: "五行占比",
      lineDetails: "六爻明细",
      bornTime: "出生时刻",
      sharePreview: "排盘预览",
      theme: "切换配色",
      // -- App chrome --
      appTitle: '天机',
      appSubtitle: '中国传统玄学计算',

      // -- Tabs --
      tabBazi: '八字排盘',
      tabLiuyao: '六爻占卜',
      tabZiwei: '紫微斗数',

      // -- BaZi general --
      birthDate: '出生日期',
      birthTime: '出生时辰',
      gender: '性别',
      male: '男',
      female: '女',
      yearPillar: '年柱',
      monthPillar: '月柱',
      dayPillar: '日柱',
      hourPillar: '时柱',
      heavenlyStem: '天干',
      earthlyBranch: '地支',
      dayMaster: '日主',
      tenGods: '十神',
      fiveElements: '五行分析',
      dayMasterStrength: '日主强弱',
      luckPillars: '大运',
      flowYears: '流年',
      relationships: '刑冲合害',
      strong: '身强',
      weak: '身弱',
      neutral: '中和',
      hiddenStems: '藏干',
      nayin: '纳音',
      elementCount: '五行统计',

      // -- Five Elements --
      wood: '木',
      fire: '火',
      earth: '土',
      metal: '金',
      water: '水',

      // -- Heavenly Stems --
      stemJia: '甲', stemYi: '乙', stemBing: '丙', stemDing: '丁',
      stemWu: '戊', stemJi: '己', stemGeng: '庚', stemXin: '辛',
      stemRen: '壬', stemGui: '癸',

      // -- Earthly Branches --
      branchZi: '子', branchChou: '丑', branchYin: '寅', branchMao: '卯',
      branchChen: '辰', branchSi: '巳', branchWu2: '午', branchWei: '未',
      branchShen: '申', branchYou: '酉', branchXu: '戌', branchHai: '亥',

      // -- Zodiac --
      rat: '鼠', ox: '牛', tiger: '虎', rabbit: '兔',
      dragon: '龙', snake: '蛇', horse: '马', goat: '羊',
      monkey: '猴', rooster: '鸡', dog: '狗', pig: '猪',

      // -- Ten Gods --
      bijian: '比肩', jiecai: '劫财', shishen: '食神', shangguan: '伤官',
      piancai: '偏财', zhengcai: '正财', qisha: '七杀', zhengguan: '正官',
      pianyin: '偏印', zhengyin: '正印',

      // -- Polarity --
      yang: '阳',
      yin: '阴',

      // -- Shi-chen (double-hour) names --
      shiChen0: '子时 (23:00-01:00)',
      shiChen1: '丑时 (01:00-03:00)',
      shiChen2: '寅时 (03:00-05:00)',
      shiChen3: '卯时 (05:00-07:00)',
      shiChen4: '辰时 (07:00-09:00)',
      shiChen5: '巳时 (09:00-11:00)',
      shiChen6: '午时 (11:00-13:00)',
      shiChen7: '未时 (13:00-15:00)',
      shiChen8: '申时 (15:00-17:00)',
      shiChen9: '酉时 (17:00-19:00)',
      shiChen10: '戌时 (19:00-21:00)',
      shiChen11: '亥时 (21:00-23:00)',

      // -- Liu Yao --
      castMethod: '起卦方法',
      timeCast: '时间起卦',
      numberCast: '数字起卦',
      coinCast: '铜钱摇卦',
      primaryHex: '本卦',
      changedHex: '变卦',
      movingLines: '动爻',
      worldLine: '世爻',
      responseLine: '应爻',
      sixRelatives: '六亲',
      sixGods: '六神',
      castNow: '起卦',
      hexagram: '卦象',
      hexDescription: '卦辞',
      linePosition: '爻位',
      lineYang: '阳爻',
      lineYin: '阴爻',
      movingMark: '动',
      num1Label: '数字一',
      num2Label: '数字二',
      num3Label: '数字三（可选）',
      noMovingLines: '无动爻',

      // -- Six Gods detail --
      qinglong: '青龙',
      zhuque: '朱雀',
      gouchen: '勾陈',
      tengshe: '腾蛇',
      baihu: '白虎',
      xuanwu: '玄武',

      // -- Six Relatives detail --
      xiongdi: '兄弟',
      zisun: '子孙',
      fumu: '父母',
      qicai: '妻财',
      guangui: '官鬼',

      // -- Zi Wei Dou Shu --
      lunarDate: '农历日期',
      lunarYear: '年',
      lunarMonth: '月',
      lunarDay: '日',
      palace: '宫',
      stars: '星曜',
      convertSolar: '从公历转换',

      // -- 12 Palace names --
      palaceLife: '命宫',
      palaceSiblings: '兄弟宫',
      palaceSpouse: '夫妻宫',
      palaceChildren: '子女宫',
      palaceWealth: '财帛宫',
      palaceHealth: '疾厄宫',
      palaceTravel: '迁移宫',
      palaceServants: '奴仆宫',
      palaceCareer: '官禄宫',
      palaceProperty: '田宅宫',
      palaceFortune: '福德宫',
      palaceParents: '父母宫',

      // -- Palace meanings (tooltip) --
      palaceLifeDesc: '命主本人，性格、外貌、整体运势',
      palaceSiblingsDesc: '兄弟姐妹、朋友、合作关系',
      palaceSpouseDesc: '婚姻、感情、配偶',
      palaceChildrenDesc: '子女、下属、创意',
      palaceWealthDesc: '财运、理财、金钱',
      palaceHealthDesc: '健康、疾病、意外',
      palaceTravelDesc: '出行、搬迁、外在表现',
      palaceServantsDesc: '朋友、下属、人际关系',
      palaceCareerDesc: '事业、名誉、官职',
      palacePropertyDesc: '房产、家宅、家庭环境',
      palaceFortuneDesc: '福气、精神生活、享受',
      palaceParentsDesc: '父母、上司、长辈',

      // -- Major stars --
      starZiwei: '紫微', starTianji: '天机', starTaiyang: '太阳',
      starWuqu: '武曲', starTiantong: '天同', starLianzhen: '廉贞',
      starTianfu: '天府', starTaiyin: '太阴', starTanlang: '贪狼',
      starJumen: '巨门', starTianxiang: '天相', starTianliang: '天梁',
      starQisha2: '七杀', starPojun: '破军',
      noMajorStar: '（无主星）',

      // -- Branch relationships --
      liuhe: '六合',
      sanhe: '三合',
      liuchong: '六冲',
      sanxing: '三刑',
      liuhai: '六害',

      // -- Common UI --
      calculate: '排盘',
      reset: '重置',
      share: '分享',
      copyLink: '复制链接',
      saveImage: '保存图片',
      darkTheme: '暗色主题',
      lightTheme: '亮色主题',
      language: '语言',
      privacy: '隐私声明',
      privacyText: '本工具完全在浏览器本地运行，不收集任何个人数据，不发送任何网络请求。您的出生信息仅用于本地计算，不会被存储或传输。',
      noData: '无数据',
      loading: '计算中...',
      copied: '已复制',
      sharePrompt: '分享此命盘',
      age: '岁',
      year2: '年',
      startAge: '起运年龄',
    },

    /* ================================================================ */
    /*  ENGLISH                                                         */
    /* ================================================================ */
    en: {
      atBoundary: "Compare at boundary", beforeBoundary: "Compare one minute before",
      skip: "Skip to chart",
      today: "Today",
      methods: "Chart tools",
      shareChart: "Share chart",
      birthDetails: "Birth details",
      solarDate: "Gregorian date",
      birthClock: "Birth time",
      clockRule: "Use Beijing time (UTC+8). The day changes at midnight. Gender sets the luck cycle direction.",
      boundaryExample: "Li Chun example",
      useNow: "Use now",
      termBasis: "Month boundaries",
      method: "Method",
      castTime: "Casting time (UTC+8)",
      lunarBirth: "Lunar birth date",
      ziweiRule: "Use the lunar birth date. A leap month takes the same palace month as its regular counterpart.",
      useBazi: "Use Four Pillars birth date",
      offline: "Calculated locally · Works offline",
      shareDetail: "This link contains the chart inputs. Anyone with the link can reproduce the chart.",
      chartLink: "Chart link",
      close: "Close",
      lightAction: "Light",
      darkAction: "Dark",
      baziIntro: "Read the Four Pillars, five elements and solar-term boundaries for a birth time.",
      liuyaoIntro: "Cast by time, numbers or coins. Read the original hexagram, its moving lines and the changed hexagram.",
      ziweiIntro: "Map the life and body palaces and locate the fourteen major stars.",
      invalidBirth: "Enter a valid Gregorian date from 1900-01-31 through 2100-12-31 and a birth time.",
      invalidLunar: "Check the lunar date. A short month has 29 days, and the leap month must match the year.",
      currentJie: "Month began",
      nextJie: "Next boundary",
      pillarsTitle: "Four Pillars chart",
      cycleTitle: "Luck cycles and years",
      analysisTitle: "Pattern and auxiliary stars",
      stemInfo: "Stem",
      branchInfo: "Branch",
      yearShort: "Year",
      monthShort: "Month",
      dayShort: "Day",
      hourShort: "Hour",
      strengthInfo: "Strength factors",
      pattern: "Pattern",
      fav: "Favourable",
      unfav: "Unfavourable",
      aux: "Auxiliary stars",
      taiyuan: "Foetal origin",
      minggong: "Life palace",
      shangong: "Body palace",
      lunarMarker: "Lunar",
      leap: "Leap ",
      none: "None",
      elementNote: "Weighted stems and hidden stems",
      cycleRule: "Whole-year estimate · three days per year",
      timeHint: "Uses the lunar year branch, month, day and hour branch.",
      numberHint: "The first two numbers set the upper and lower trigrams. The third sets the moving line, or defaults to their sum.",
      coinHint: "Three coins per line, from bottom to top. A six or a nine changes.",
      waitingCast: "Ready to cast",
      waitingHint: "Choose a method and select Cast to see the result.",
      castSummary: "Casting result",
      rawValues: "Value",
      palacesTitle: "Twelve palaces",
      palaceJu: "Element bureau",
      resultCopyHint: "Select and copy the link manually.",
      boundaryNote: "Month changes at the listed minute",
      forward: "Forward",
      backward: "Reverse",
      strongest: "Element share",
      lineDetails: "Line details",
      bornTime: "Birth time",
      sharePreview: "Chart preview",
      theme: "Change theme",
      appTitle: 'Tianji',
      appSubtitle: 'Chinese Metaphysics Calculator',

      tabBazi: 'BaZi (Four Pillars)',
      tabLiuyao: 'Liu Yao (I Ching)',
      tabZiwei: 'Zi Wei Dou Shu',

      birthDate: 'Birth Date',
      birthTime: 'Birth Hour',
      gender: 'Gender',
      male: 'Male',
      female: 'Female',
      yearPillar: 'Year',
      monthPillar: 'Month',
      dayPillar: 'Day',
      hourPillar: 'Hour',
      heavenlyStem: 'Stem',
      earthlyBranch: 'Branch',
      dayMaster: 'Day Master',
      tenGods: 'Ten Gods',
      fiveElements: 'Five Elements',
      dayMasterStrength: 'Day Master Strength',
      luckPillars: 'Luck Pillars',
      flowYears: 'Flow Years',
      relationships: 'Relationships',
      strong: 'Strong',
      weak: 'Weak',
      neutral: 'Neutral',
      hiddenStems: 'Hidden Stems',
      nayin: 'Nayin',
      elementCount: 'Element Count',

      wood: 'Wood', fire: 'Fire', earth: 'Earth', metal: 'Metal', water: 'Water',

      stemJia: 'Jia', stemYi: 'Yi', stemBing: 'Bing', stemDing: 'Ding',
      stemWu: 'Wu', stemJi: 'Ji', stemGeng: 'Geng', stemXin: 'Xin',
      stemRen: 'Ren', stemGui: 'Gui',

      branchZi: 'Zi', branchChou: 'Chou', branchYin: 'Yin', branchMao: 'Mao',
      branchChen: 'Chen', branchSi: 'Si', branchWu2: 'Wu', branchWei: 'Wei',
      branchShen: 'Shen', branchYou: 'You', branchXu: 'Xu', branchHai: 'Hai',

      rat: 'Rat', ox: 'Ox', tiger: 'Tiger', rabbit: 'Rabbit',
      dragon: 'Dragon', snake: 'Snake', horse: 'Horse', goat: 'Goat',
      monkey: 'Monkey', rooster: 'Rooster', dog: 'Dog', pig: 'Pig',

      bijian: 'Companion', jiecai: 'Rob Wealth', shishen: 'Eating God', shangguan: 'Hurting Officer',
      piancai: 'Indirect Wealth', zhengcai: 'Direct Wealth', qisha: 'Seven Killings', zhengguan: 'Direct Officer',
      pianyin: 'Indirect Resource', zhengyin: 'Direct Resource',

      yang: 'Yang',
      yin: 'Yin',

      shiChen0: 'Zi (23:00-01:00)',
      shiChen1: 'Chou (01:00-03:00)',
      shiChen2: 'Yin (03:00-05:00)',
      shiChen3: 'Mao (05:00-07:00)',
      shiChen4: 'Chen (07:00-09:00)',
      shiChen5: 'Si (09:00-11:00)',
      shiChen6: 'Wu (11:00-13:00)',
      shiChen7: 'Wei (13:00-15:00)',
      shiChen8: 'Shen (15:00-17:00)',
      shiChen9: 'You (17:00-19:00)',
      shiChen10: 'Xu (19:00-21:00)',
      shiChen11: 'Hai (21:00-23:00)',

      castMethod: 'Casting Method',
      timeCast: 'Time-based',
      numberCast: 'Number-based',
      coinCast: 'Coin Toss',
      primaryHex: 'Primary',
      changedHex: 'Changed',
      movingLines: 'Moving Lines',
      worldLine: 'World',
      responseLine: 'Response',
      sixRelatives: 'Six Relatives',
      sixGods: 'Six Gods',
      castNow: 'Cast',
      hexagram: 'Hexagram',
      hexDescription: 'Description',
      linePosition: 'Line',
      lineYang: 'Yang',
      lineYin: 'Yin',
      movingMark: 'Moving',
      num1Label: 'Number 1',
      num2Label: 'Number 2',
      num3Label: 'Number 3 (optional)',
      noMovingLines: 'No moving lines',

      qinglong: 'Azure Dragon',
      zhuque: 'Vermilion Bird',
      gouchen: 'Hook Snake',
      tengshe: 'Soaring Snake',
      baihu: 'White Tiger',
      xuanwu: 'Black Tortoise',

      xiongdi: 'Sibling',
      zisun: 'Offspring',
      fumu: 'Parent',
      qicai: 'Wealth',
      guangui: 'Officer',

      lunarDate: 'Lunar Date',
      lunarYear: 'Year',
      lunarMonth: 'Month',
      lunarDay: 'Day',
      palace: 'Palace',
      stars: 'Stars',
      convertSolar: 'Convert from Solar',

      palaceLife: 'Life',
      palaceSiblings: 'Siblings',
      palaceSpouse: 'Spouse',
      palaceChildren: 'Children',
      palaceWealth: 'Wealth',
      palaceHealth: 'Health',
      palaceTravel: 'Travel',
      palaceServants: 'Friends',
      palaceCareer: 'Career',
      palaceProperty: 'Property',
      palaceFortune: 'Fortune',
      palaceParents: 'Parents',

      palaceLifeDesc: 'Character, appearance, overall destiny',
      palaceSiblingsDesc: 'Siblings, friends, partnerships',
      palaceSpouseDesc: 'Marriage, romance, partner',
      palaceChildrenDesc: 'Children, subordinates, creativity',
      palaceWealthDesc: 'Finance, money, assets',
      palaceHealthDesc: 'Health, illness, accidents',
      palaceTravelDesc: 'Travel, relocation, public image',
      palaceServantsDesc: 'Friends, subordinates, social circle',
      palaceCareerDesc: 'Career, reputation, rank',
      palacePropertyDesc: 'Property, home, family environment',
      palaceFortuneDesc: 'Blessings, spiritual life, enjoyment',
      palaceParentsDesc: 'Parents, superiors, elders',

      starZiwei: 'Zi Wei', starTianji: 'Tian Ji', starTaiyang: 'Tai Yang',
      starWuqu: 'Wu Qu', starTiantong: 'Tian Tong', starLianzhen: 'Lian Zhen',
      starTianfu: 'Tian Fu', starTaiyin: 'Tai Yin', starTanlang: 'Tan Lang',
      starJumen: 'Ju Men', starTianxiang: 'Tian Xiang', starTianliang: 'Tian Liang',
      starQisha2: 'Qi Sha', starPojun: 'Po Jun',
      noMajorStar: '(No major star)',

      liuhe: 'Six Harmony',
      sanhe: 'Three Harmony',
      liuchong: 'Six Clash',
      sanxing: 'Three Punishment',
      liuhai: 'Six Harm',

      calculate: 'Calculate',
      reset: 'Reset',
      share: 'Share',
      copyLink: 'Copy Link',
      saveImage: 'Save Image',
      darkTheme: 'Dark',
      lightTheme: 'Light',
      language: 'Language',
      privacy: 'Privacy',
      privacyText: 'This tool runs entirely in your browser. No personal data is collected, no network requests are made. Your birth information is used only for local calculation and is never stored or transmitted.',
      noData: 'No data',
      loading: 'Calculating...',
      copied: 'Copied',
      sharePrompt: 'Share this chart',
      age: 'yrs',
      year2: '',
      startAge: 'Start Age',
    }
  };

  /**
   * Translate a key. Returns the key itself if no translation found.
   * @param {string} key
   * @returns {string}
   */
  function t(key) {
    return translations[currentLang]?.[key] ?? key;
  }

  /**
   * Set the active language.
   * @param {'zh'|'en'} lang
   */
  function setLang(lang) {
    if (translations[lang]) {
      currentLang = lang;
    }
  }

  /** @returns {'zh'|'en'} */
  function getLang() {
    return currentLang;
  }

  /**
   * Toggle between zh and en. Returns new language code.
   * @returns {'zh'|'en'}
   */
  function toggle() {
    currentLang = currentLang === 'zh' ? 'en' : 'zh';
    return currentLang;
  }

  return { t, setLang, getLang, toggle, translations };
})();
