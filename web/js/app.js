/* Offline chart controls and share links. */
const TianjiApp = (() => {
    'use strict';
    const $ = (id) => document.getElementById(id);
    const t = I18n.t;
    const tabs = ['bazi', 'liuyao', 'ziwei'];
    const titles = { bazi: 'tabBazi', liuyao: 'tabLiuyao', ziwei: 'tabZiwei' };
    const pad = (n) => String(n).padStart(2, '0');
    const monthNames = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊'];
    let activeTab = 'bazi';
    let lastCast = null;

    function beijingNow() {
        return new Date(Date.now() + 8 * 3600000).toISOString().slice(0, 16);
    }

    function setNow() {
        const [date, time] = beijingNow().split('T');
        $('bazi-date').value = date;
        $('bazi-time').value = time;
    }

    function gender(tab) {
        return $(tab + '-form').elements[tab + '-gender'].value;
    }

    function setGender(tab, value) {
        $(tab + '-form').elements[tab + '-gender'].value = value === 'female' ? 'female' : 'male';
    }

    function inputsBazi() {
        if (!$('bazi-form').checkValidity()) return null;
        const [year, month, day] = $('bazi-date').value.split('-').map(Number);
        const [hour, minute] = $('bazi-time').value.split(':').map(Number);
        return { year, month, day, hour, minute };
    }

    function replaceResult(tab, html) {
        const area = $(tab + '-result');
        const opened = Array.from(area.querySelectorAll('details[open]'), (d) => d.id);
        area.innerHTML = html;
        opened.forEach((id) => {
            if ($(id)) $(id).open = true;
        });
    }

    function unavailable(tab, message) {
        replaceResult(tab, `<p class="card validation">${t(message)}</p>`);
        if (activeTab === tab) $('share-btn').disabled = true;
    }

    function calculateBazi() {
        const input = inputsBazi();
        $('term-card').hidden = !input;
        if (!input) {
            unavailable('bazi', 'invalidBirth');
            return;
        }
        const { year, month, day, hour, minute } = input;
        const chart = BaZi.createChart(year, month, day, hour, gender('bazi'), minute);
        const wall = Date.UTC(year, month - 1, day, hour, minute);
        const view = TianjiViews.bazi(chart, wall);
        replaceResult('bazi', view.html);
        $('term-window').innerHTML = TianjiViews.monthBounds(wall);
        if (activeTab === 'bazi') {
            $('share-btn').disabled = false;
            TianjiViews.drawRadarChart($('radar-canvas'), view.scores, false);
        }
    }

    function updateCastMethod() {
        const method = $('liuyao-method').value;
        for (const name of ['time', 'number']) {
            const group = $('liuyao-' + name + '-inputs');
            group.hidden = method !== name;
            group.querySelectorAll('input').forEach((input) => {
                input.disabled = group.hidden;
            });
        }
        $('cast-hint').textContent = t(method + 'Hint');
    }

    function renderCast() {
        replaceResult('liuyao', TianjiViews.liuyao(lastCast));
        $('share-btn').disabled = !lastCast;
    }

    function castLiuyao() {
        if (!$('liuyao-form').reportValidity()) return;
        const method = $('liuyao-method').value;
        if (method === 'time') {
            const [y, m, d, h] = $('cast-time').value.split(/[-T:]/).map(Number);
            lastCast = LiuYao.castByClock(y, m, d, h);
        } else if (method === 'number') {
            const n3 = $('liuyao-num3').value;
            lastCast = LiuYao.castByNumbers(
                +$('liuyao-num1').value,
                +$('liuyao-num2').value,
                n3 ? Number(n3) : null,
            );
        } else {
            lastCast = LiuYao.castByCoins();
        }
        renderCast();
    }

    function monthChoices(value) {
        const sel = $('ziwei-month');
        const year = Number($('ziwei-year').value);
        const months = TianjiAlmanac.lunarMonths[year - 1900] || [];
        let number = 0;
        sel.replaceChildren(
            ...months.map((length) => {
                if (length > 0) number++;
                const name = I18n.getLang() === 'zh' ? monthNames[number - 1] + '月' : String(number);
                return new Option((length < 0 ? t('leap') : '') + name, (length < 0 ? 'L' : '') + number);
            }),
        );
        sel.value = value || '4';
        if (!sel.value && months.length) sel.value = (value || '1').replace('L', '');
    }

    function calculateZiwei() {
        const year = Number($('ziwei-year').value),
            day = Number($('ziwei-day').value);
        const value = $('ziwei-month').value,
            month = Number(value.replace('L', '')),
            leap = value.startsWith('L');
        if (!$('ziwei-form').checkValidity() || !value) {
            unavailable('ziwei', 'invalidLunar');
            return;
        }
        let chart;
        try {
            // A selector value represents a double-hour; the engine takes a 24-hour clock.
            chart = ZiWei.createChart(year, month, day, Number($('ziwei-hour').value) * 2, gender('ziwei'), leap);
        } catch (error) {
            if (!(error instanceof RangeError)) throw error;
            unavailable('ziwei', 'invalidLunar');
            return;
        }
        replaceResult('ziwei', TianjiViews.ziwei(chart, leap));
        if (activeTab === 'ziwei') $('share-btn').disabled = false;
    }

    function useBirthDate() {
        const input = inputsBazi();
        if (!input) {
            switchTab('bazi');
            $('bazi-form').reportValidity();
            return;
        }
        const lunar = Calendar.solarToLunar(input.year, input.month, input.day);
        $('ziwei-year').value = lunar.year;
        monthChoices((lunar.isLeap ? 'L' : '') + lunar.month);
        $('ziwei-day').value = lunar.day;
        $('ziwei-hour').value = Math.floor((input.hour + 1) / 2) % 12;
        setGender('ziwei', gender('bazi'));
        calculateZiwei();
    }

    function switchTab(tab) {
        if (!tabs.includes(tab)) return;
        activeTab = tab;
        for (const name of tabs) {
            const active = name === tab;
            $('panel-' + name).hidden = !active;
            $('tab-' + name).setAttribute('aria-selected', String(active));
            $('tab-' + name).tabIndex = active ? 0 : -1;
        }
        $('panel-title').textContent = t(titles[tab]);
        $('panel-description').textContent = t(tab + 'Intro');
        document.title = t(titles[tab]) + ' · ' + t('appTitle');
        if (tab === 'bazi') calculateBazi();
        if (tab === 'liuyao') {
            updateCastMethod();
            renderCast();
        }
        if (tab === 'ziwei') calculateZiwei();
    }

    function applyLanguage() {
        const zh = I18n.getLang() === 'zh';
        document.documentElement.lang = zh ? 'zh-CN' : 'en';
        document.querySelectorAll('[data-i18n]').forEach((el) => {
            el.textContent = t(el.dataset.i18n);
        });
        document.querySelectorAll('[data-aria]').forEach((el) => {
            el.setAttribute('aria-label', t(el.dataset.aria));
        });
        const lang = $('lang-toggle');
        lang.textContent = zh ? 'EN' : '中文';
        lang.lang = zh ? 'en' : 'zh-CN';
        lang.setAttribute('aria-label', zh ? 'Switch to English' : '切换至中文');
        $('theme-label').textContent = t(
            document.documentElement.dataset.theme === 'light' ? 'darkAction' : 'lightAction',
        );
        const hour = $('ziwei-hour'),
            saved = hour.value || '7';
        hour.replaceChildren(...Array.from({ length: 12 }, (_, i) => new Option(t('shiChen' + i), i)));
        hour.value = saved;
        monthChoices($('ziwei-month').value);
        const date = beijingNow().slice(0, 10);
        const [y, m, d] = date.split('-').map(Number);
        $('today-date').textContent = date.replaceAll('-', '.') + '  ·  ' + TianjiViews.lunarText(y, m, d);
    }

    function toggleLang() {
        I18n.toggle();
        applyLanguage();
        switchTab(activeTab);
    }

    function toggleTheme() {
        const root = document.documentElement;
        root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
        $('theme-label').textContent = t(root.dataset.theme === 'light' ? 'darkAction' : 'lightAction');
        switchTab(activeTab);
    }

    function shareState() {
        if (activeTab === 'bazi') {
            return {
                tab: activeTab,
                date: $('bazi-date').value,
                time: $('bazi-time').value,
                gender: gender('bazi'),
            };
        }
        if (activeTab === 'ziwei') {
            return {
                tab: activeTab,
                y: $('ziwei-year').value,
                m: $('ziwei-month').value,
                d: $('ziwei-day').value,
                h: $('ziwei-hour').value,
                gender: gender('ziwei'),
            };
        }
        const method = $('liuyao-method').value;
        const state = { tab: activeTab, method, lines: lastCast.rawLines };
        if (method === 'time') state.time = $('cast-time').value;
        if (method === 'number') state.numbers = [1, 2, 3].map((n) => $('liuyao-num' + n).value);
        return state;
    }

    function restore() {
        const hash = location.hash.slice(1);
        if (!hash || hash.length > 2048) return;
        try {
            const data = JSON.parse(atob(hash));
            if (!data || !tabs.includes(data.tab)) return;
            if (data.tab === 'bazi') {
                const oldHour = Number(data.hour);
                // v0.3 shared a branch index, using the first clock hour in its range.
                const legacy =
                    Number.isInteger(oldHour) && oldHour >= 0 && oldHour < 12
                        ? pad(oldHour === 0 ? 23 : oldHour * 2 - 1) + ':00'
                        : '';
                $('bazi-date').value = data.date || '';
                $('bazi-time').value = data.time || legacy;
                setGender('bazi', data.gender);
            } else if (data.tab === 'ziwei') {
                $('ziwei-year').value = data.y;
                monthChoices(String(data.m));
                $('ziwei-day').value = data.d;
                $('ziwei-hour').value = data.h;
                setGender('ziwei', data.gender);
            } else {
                if (!['time', 'number', 'coin'].includes(data.method) || !Array.isArray(data.lines)) return;
                const cast = LiuYao.castFromLines(data.lines);
                $('liuyao-method').value = data.method;
                if (data.method === 'time') $('cast-time').value = data.time || '';
                if (data.method === 'number' && Array.isArray(data.numbers)) {
                    [1, 2, 3].forEach((n) => {
                        $('liuyao-num' + n).value = data.numbers[n - 1] || '';
                    });
                }
                lastCast = cast;
            }
            activeTab = data.tab;
            return true;
        } catch {
            /* Incomplete links fall back to the opened workspace. */
        }
    }

    function openShare() {
        if ($('share-btn').disabled) return;
        const url = new URL(location.href);
        url.hash = btoa(JSON.stringify(shareState()));
        $('share-url').value = url.href;
        $('copy-status').textContent = '';
        $('share-modal').showModal();
    }

    async function copyShareLink() {
        const field = $('share-url');
        if (!$('share-modal').open) openShare();
        if (!$('share-modal').open) return;
        field.focus();
        field.select();
        let copied = false;
        try {
            if (navigator.clipboard) {
                await navigator.clipboard.writeText(field.value);
                copied = true;
            }
        } catch {
            /* Keep the URL selected for the browser's copy fallback. */
        }
        if (!copied) {
            try {
                copied = document.execCommand('copy');
            } catch {
                /* Manual copy remains available. */
            }
        }
        $('copy-status').textContent = t(copied ? 'copied' : 'resultCopyHint');
    }

    function init() {
        document.documentElement.dataset.theme = matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
        setNow();
        $('cast-time').value = beijingNow();
        applyLanguage();
        restore();
        switchTab(activeTab);
        window.addEventListener('hashchange', () => { if (restore()) switchTab(activeTab); });
        tabs.forEach((name, i) => {
            const tab = $('tab-' + name);
            tab.addEventListener('click', () => switchTab(name));
            tab.addEventListener('keydown', (event) => {
                const next = { ArrowLeft: (i + 2) % 3, ArrowRight: (i + 1) % 3, Home: 0, End: 2 }[event.key];
                if (next === undefined) return;
                event.preventDefault();
                switchTab(tabs[next]);
                $('tab-' + tabs[next]).focus();
            });
        });
        $('theme-toggle').addEventListener('click', toggleTheme);
        $('lang-toggle').addEventListener('click', toggleLang);
        $('bazi-form').addEventListener('change', calculateBazi);
        $('bazi-form').addEventListener('submit', (e) => {
            e.preventDefault();
            calculateBazi();
        });
        $('example-btn').addEventListener('click', () => {
            $('bazi-date').value = '2025-02-03';
            $('bazi-time').value = '22:10';
            calculateBazi();
        });
        $('bazi-result').addEventListener('click', (event) => {
            const button = event.target.closest('[data-boundary-target]');
            if (!button) return;
            const time = new Date(Number(button.dataset.boundaryTarget)).toISOString();
            $('bazi-date').value = time.slice(0, 10);
            $('bazi-time').value = time.slice(11, 16);
            calculateBazi();
            $('bazi-result').querySelector('[data-boundary-target]')?.focus();
        });
        $('now-btn').addEventListener('click', () => {
            setNow();
            calculateBazi();
        });
        $('liuyao-form').addEventListener('input', () => {
            lastCast = null;
            updateCastMethod();
            renderCast();
        });
        $('liuyao-form').addEventListener('submit', (e) => {
            e.preventDefault();
            castLiuyao();
        });
        $('ziwei-form').addEventListener('change', (e) => {
            if (e.target.id === 'ziwei-year') monthChoices($('ziwei-month').value);
            calculateZiwei();
        });
        $('ziwei-form').addEventListener('submit', (e) => {
            e.preventDefault();
            calculateZiwei();
        });
        $('use-bazi').addEventListener('click', useBirthDate);
        $('share-btn').addEventListener('click', openShare);
        $('copy-url-btn').addEventListener('click', copyShareLink);
        $('close-share').addEventListener('click', () => $('share-modal').close());
    }

    document.addEventListener('DOMContentLoaded', init);
    return {
        switchTab,
        calculateBazi,
        castLiuyao,
        calculateZiwei,
        toggleTheme,
        toggleLang,
        copyShareLink,
        drawRadarChart: TianjiViews.drawRadarChart,
        buildHexagramSVG: TianjiViews.buildHexagramSVG,
        enableDragScroll: TianjiViews.enableDragScroll,
    };
})();
