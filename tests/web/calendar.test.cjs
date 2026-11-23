const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '../..');
const context = vm.createContext({});
for (const name of ['almanac', 'calendar', 'bazi', 'ziwei', 'liuyao']) {
    vm.runInContext(fs.readFileSync(path.join(root, 'web/js', name + '.js'), 'utf8'), context);
}
const { Calendar, BaZi, ZiWei, LiuYao } = vm.runInContext('({ Calendar, BaZi, ZiWei, LiuYao })', context);
const fixtures = require('../fixtures/calendar_cases.json');

test('browser uses the same ephemeris and lunar months as the installed Python package', () => {
    assert.deepEqual(require('../../web/js/almanac.js'), require('../../src/tianji/calendar/almanac.json'));
});

test('published solar terms and exact pillar boundaries in Beijing time', () => {
    for (const [year, term, stamp] of fixtures.solar_terms) {
        assert.equal(new Date(Calendar.termWallMillis(year, term)).toISOString().slice(0, 16), stamp);
    }
    for (const [stamp, y, m] of fixtures.pillars) {
        const [year, month, day, hour, minute] = stamp.split(/[-T:]/).map(Number);
        const chart = BaZi.createChart(year, month, day, hour, 'male', minute);
        assert.equal(chart.yearPillar.char, y);
        assert.equal(chart.monthPillar.char, m);
    }
});

test('lunar conversion includes short months, leap months and published new years', () => {
    for (const [stamp, y, m, d, leap] of fixtures.lunar) {
        const parts = stamp.split('-').map(Number);
        const lunar = Calendar.solarToLunar(...parts);
        assert.deepEqual([lunar.year, lunar.month, lunar.day, lunar.isLeap], [y, m, d, leap]);
        const solar = Calendar.lunarToSolar(y, m, d, leap);
        assert.deepEqual([solar.year, solar.month, solar.day], parts);
    }
    assert.throws(() => Calendar.lunarToSolar(2025, 6, 30, true));
    assert.throws(() => Calendar.lunarToSolar(2025, 5, 1, true));
    assert.throws(() => Calendar.solarToLunar(2025, 2, 30));
    assert.throws(() => Calendar.solarToLunar(1900, 1, 30));
});

test('sexagenary days depend on the entered civil date, including DST and skipped local dates', () => {
    for (const [year, month, day] of [
        [1990, 5, 15],
        [2024, 3, 10],
        [2011, 12, 30],
    ]) {
        for (const hour of [0, 2, 12, 23]) {
            const chart = BaZi.createChart(year, month, day, hour);
            assert.equal(chart.dayPillar.char, Calendar.dateToJiazi({ year, month, day }).char);
        }
    }
    assert.equal(BaZi.createChart(1990, 5, 15, 0).dayPillar.char, '庚辰');
});

test('cast numbers, raw coin lines, and the Plum Blossom worked example', () => {
    for (const [n1, n2, n3, primary, changed, moving] of fixtures.numbers) {
        const cast = LiuYao.castByNumbers(n1, n2, n3);
        assert.equal(cast.primary.number, primary);
        assert.equal(cast.changed.number, changed);
        assert.deepEqual(Array.from(cast.movingLines), moving);
    }
    assert.deepEqual(Array.from(LiuYao.castByClock(2025, 1, 16, 16).rawLines), [9, 8, 7, 7, 7, 8]);
    assert.equal(LiuYao.castFromLines([7, 7, 7, 7, 7, 7]).changed, null);
    assert.equal(LiuYao.castFromLines([9, 9, 9, 9, 9, 9]).changed.number, 2);
    for (let i = 1; i <= 64; i++) {
        assert.equal(LiuYao.linesToHexagram(LiuYao.hexagramLines(LiuYao.getHexagramByNumber(i))).number, i);
    }
});

test('classical Zi Wei placements including a non-midnight birth', () => {
    for (const [year, month, day, hour, life, body, sibling, ju, zw, tf] of fixtures.ziwei) {
        const c = ZiWei.createChart(year, month, day, hour);
        assert.deepEqual(
            [
                c.lifePalaceBranch,
                c.bodyPalaceBranch,
                c.getPalaceByName('兄弟宫').branch,
                c.wuXingJu,
                c.ziweiBranch,
                c.tianfuBranch,
            ],
            [life, body, sibling, ju, zw, tf],
        );
        assert.equal(Object.keys(c.stars).length, 14);
    }
});
