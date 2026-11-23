/* Chart presentation. All chart values come from the local calculation engines. */
const TianjiViews = (() => {
    'use strict';
    const t = I18n.t;
    const elementKeys = { 木: 'wood', 火: 'fire', 土: 'earth', 金: 'metal', 水: 'water' };
    const pillarKeys = ['yearShort', 'monthShort', 'dayShort', 'hourShort'];
    const hiddenKeys = ['年支藏干', '月支藏干', '日支藏干', '时支藏干'];
    const zodiacKeys = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake', 'horse', 'goat', 'monkey', 'rooster', 'dog', 'pig'];
    const godKeys = {
        比肩: 'bijian',
        劫财: 'jiecai',
        食神: 'shishen',
        伤官: 'shangguan',
        偏财: 'piancai',
        正财: 'zhengcai',
        七杀: 'qisha',
        正官: 'zhengguan',
        偏印: 'pianyin',
        正印: 'zhengyin',
    };
    const palaceKeys = [
        'palaceLife',
        'palaceSiblings',
        'palaceSpouse',
        'palaceChildren',
        'palaceWealth',
        'palaceHealth',
        'palaceTravel',
        'palaceServants',
        'palaceCareer',
        'palaceProperty',
        'palaceFortune',
        'palaceParents',
    ];
    const starKeys = {
        紫微: 'starZiwei',
        天机: 'starTianji',
        太阳: 'starTaiyang',
        武曲: 'starWuqu',
        天同: 'starTiantong',
        廉贞: 'starLianzhen',
        天府: 'starTianfu',
        太阴: 'starTaiyin',
        贪狼: 'starTanlang',
        巨门: 'starJumen',
        天相: 'starTianxiang',
        天梁: 'starTianliang',
        七杀: 'starQisha2',
        破军: 'starPojun',
    };
    const termEnglish = [
        'Minor Cold',
        'Major Cold',
        'Start of Spring',
        'Rain Water',
        'Awakening of Insects',
        'Spring Equinox',
        'Clear and Bright',
        'Grain Rain',
        'Start of Summer',
        'Grain Full',
        'Grain in Ear',
        'Summer Solstice',
        'Minor Heat',
        'Major Heat',
        'Start of Autumn',
        'End of Heat',
        'White Dew',
        'Autumn Equinox',
        'Cold Dew',
        'Frost Descent',
        'Start of Winter',
        'Minor Snow',
        'Major Snow',
        'Winter Solstice',
    ];

    function termName(name) {
        return I18n.getLang() === 'zh' ? name : termEnglish[Calendar.SOLAR_TERMS.indexOf(name)];
    }

    function monthBounds(wall) {
        const { previous, next } = Calendar.monthWindow(wall);
        return [previous, next]
            .map((boundary, i) => {
                const clock = new Date(boundary.millis).toISOString().slice(0, 16).replace('T', ' ');
                return `<div class="term"><span>${t(i === 0 ? 'currentJie' : 'nextJie')}</span><strong>${termName(boundary.term)}</strong><time>${clock}</time></div>`;
            })
            .join('');
    }

    function lunarText(year, month, day) {
        if (I18n.getLang() === 'zh') return Calendar.formatLunarDateTraditional(year, month, day);
        const lunar = Calendar.solarToLunar(year, month, day);
        return `Lunar ${lunar.year} / ${lunar.isLeap ? 'leap ' : ''}${lunar.month} / ${lunar.day}`;
    }

    function pillarCard(pillar, i, gods) {
        const stem = Calendar.getStem(pillar.stemIndex),
            branch = Calendar.getBranch(pillar.branchIndex);
        const label = pillarKeys[i];
        const god = i === 2 ? t('dayMaster') : t(godKeys[gods[['年干', '月干', '日干', '时干'][i]].god]);
        const hidden = gods[hiddenKeys[i]];
        return `<div class="pillar${i === 2 ? ' day-pillar' : ''}">
      <h3>${t(label)}</h3><span class="god">${god}</span>
      <div class="glyph ${elementKeys[stem.element]}">${stem.char}</div><div class="glyph ${elementKeys[branch.element]}">${branch.char}</div>
      <p class="pillar-nayin">${BaZi.getNayin(pillar.jiaziIndex)}</p>
      <p class="hidden-stems"><span>${t('hiddenStems')}</span> ${hidden.map((h) => `<abbr title="${t(godKeys[h.god])}">${h.stem}</abbr>`).join(' ')}</p>
    </div>`;
    }

    function boundaryComparison(wall) {
        const window = Calendar.monthWindow(wall);
        const day = (millis) => new Date(millis).toISOString().slice(0, 10);
        const boundary = [window.previous, window.next].find((b) => day(b.millis) === day(wall));
        if (!boundary) return '';
        const before = wall < boundary.millis;
        const target = before ? boundary.millis : boundary.millis - 60000;
        return `<p class="compare"><span>${termName(boundary.term)} · ${new Date(boundary.millis).toISOString().slice(11, 16)} UTC+8</span>
      <button type="button" data-boundary-target="${target}">${t(before ? 'atBoundary' : 'beforeBoundary')}</button></p>`;
    }

    function bazi(chart, wall) {
        const { birthYear, birthMonth, birthDay } = chart;
        const gods = BaZi.tenGodsFromChart(chart);
        const strength = BaZi.analyzeDayMasterStrength(chart);
        const elements = BaZi.analyzeFiveElements(chart.allStems, chart.allBranches);
        const pattern = BaZi.analyzePattern(chart, strength);
        const favorable = BaZi.suggestFavorable(chart, strength, elements);
        const shensha = BaZi.computeShensha(chart);
        const relationships = BaZi.analyzeRelationships(chart.allBranches).relationships;
        const luck = BaZi.computeLuckPillars(chart);
        const flow = BaZi.computeFlowYears(chart, new Date(Date.now() + 8 * 3600000).getUTCFullYear(), 10);
        const tai = BaZi.computeTaiyuan(chart),
            ming = BaZi.computeMinggong(chart);
        const bars = elements.details
            .map(
                (
                    d,
                ) => `<div class="element-row ${elementKeys[d.element]}"><span>${t(elementKeys[d.element])}</span>
      <div class="bar"><i style="width:${d.percent}%"></i></div><b>${d.percent}%</b></div>`,
            )
            .join('');
        const scores = Object.fromEntries(elements.details.map((d) => [d.element, d.score]));
        const hiddenGods = chart.pillars.map((pillar, i) => {
            const stems = gods[hiddenKeys[i]].map((h) => `${h.stem} · ${t(godKeys[h.god])}`);
            return `<dt>${t(pillarKeys[i])} · ${t(zodiacKeys[pillar.branchIndex])}</dt><dd>${stems.join(' / ')}</dd>`;
        }).join('');
        const iso = [birthYear, String(birthMonth).padStart(2, '0'), String(birthDay).padStart(2, '0')].join(
            '-',
        );
        const hour =
            String(chart.birthHour).padStart(2, '0') + ':' + String(chart.birthMinute).padStart(2, '0');
        const blocks = `<article class="card chart-card">
      <div class="result-heading"><h2>${t('pillarsTitle')}</h2><span class="chart-time">${iso} · ${hour}</span></div>
      <p class="lunar-line">${lunarText(birthYear, birthMonth, birthDay)}</p>
      ${boundaryComparison(wall)}<div class="pillars">${chart.pillars.map((p, i) => pillarCard(p, i, gods)).join('')}</div>
      <div class="summary-row"><span>${t('dayMaster')} <b>${chart.dayMasterChar} · ${t(elementKeys[chart.dayMasterElement])}</b></span>
      <span>${t('taiyuan')} <b>${tai.char} · ${tai.nayin}</b></span><span>${t('minggong')} <b>${ming.char} · ${ming.nayin}</b></span></div>
    </article>
    <article class="card"><h2>${t('fiveElements')}</h2><p class="hint caption">${t('elementNote')}</p>
      <div class="elements"><canvas id="radar-canvas" width="200" height="200" aria-hidden="true"></canvas><div class="bars">${bars}</div></div>
    </article>
    <details class="card disclosure" id="pattern-details"><summary>${t('analysisTitle')}</summary><div class="analysis">
      <h3>${t('dayMasterStrength')} · ${strength.level} (${strength.score.toFixed(1)})</h3><ul>${strength.factors.map((v) => `<li>${v}</li>`).join('')}</ul>
      <h3>${t('hiddenStems')} · ${t('tenGods')}</h3><dl>${hiddenGods}</dl>
      <h3>${t('pattern')} · ${pattern.pattern}</h3><p>${pattern.description}</p>
      <dl><dt>${t('fav')}</dt><dd>${favorable.favorable.join('、')}</dd><dt>${t('unfav')}</dt><dd>${favorable.unfavorable.join('、')}</dd></dl>
      <p>${favorable.suggestion}</p><h3>${t('aux')}</h3><div class="tags">${shensha.map((s) => `<span>${s.name} · ${s.pillar}</span>`).join('') || t('none')}</div>
      <h3>${t('relationships')}</h3><p>${relationships.map((r) => r.description).join(' · ') || t('none')}</p>
    </div></details>
    <details class="card disclosure" id="luck-details"><summary>${t('cycleTitle')}</summary><div class="analysis">
      <h3>${t('luckPillars')} · ${t(luck.isForward ? 'forward' : 'backward')}</h3><p>${t('startAge')} ${luck.startAge} ${t('age')} · ${t('cycleRule')}</p>
      <div class="cycles">${luck.pillars.map((p) => `<div><small>${p.startAge}–${p.endAge} ${t('age')}</small><b>${p.char}</b><span>${p.nayin}</span><small>${p.startYear}–${p.endYear}</small></div>`).join('')}</div>
      <h3>${t('flowYears')}</h3><div class="cycles">${flow.map((y) => `<div><small>${y.year}</small><b>${y.char}</b><span>${t(godKeys[y.tenGod])}</span><small>${y.nayin}</small></div>`).join('')}</div>
    </div></details>`;
        return { html: blocks, scores };
    }

    function liuyao(result) {
        if (!result)
            return `<div class="card empty"><span aria-hidden="true">☷</span><h2>${t('waitingCast')}</h2><p>${t('waitingHint')}</p></div>`;
        const diagrams = [result.primary, result.changed].filter(Boolean).map(
            (hex, i) => `<div class="hex">
      <h3>${t(i ? 'changedHex' : 'primaryHex')}</h3>${buildHexagramSVG(LiuYao.hexagramLines(hex), i ? [] : result.movingLines)}
      <b>${hex.name}</b><span>${t('hexagram')} ${hex.number} · ${hex.upper.symbol} / ${hex.lower.symbol}</span><p>${hex.description}</p></div>`,
        );
        const names =
            I18n.getLang() === 'zh'
                ? ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
                : ['1', '2', '3', '4', '5', '6'];
        const rows = result.rawLines.map(
            (raw, i) =>
                `<tr><th scope="row">${names[i]}</th><td>${raw}</td><td>${t(raw % 2 ? 'lineYang' : 'lineYin')}</td><td>${result.movingLines.includes(i + 1) ? t('movingMark') : '—'}</td></tr>`,
        );
        return `<article class="card"><h2>${t('castSummary')}</h2><div class="hex-pair">${diagrams.join('')}</div><p class="cast-moving">${t('movingLines')} · ${result.movingLines.map((i) => names[i - 1]).join('、') || t('noMovingLines')}</p></article>
      <details class="card disclosure" id="line-details"><summary>${t('lineDetails')}</summary><table><thead><tr>${['linePosition', 'rawValues', 'yin', 'movingMark'].map((key, i) => `<th>${i === 2 ? t('yin') + '/' + t('yang') : t(key)}</th>`).join('')}</tr></thead><tbody>${rows.reverse().join('')}</tbody></table></details>`;
    }

    function ziwei(chart, isLeap) {
        const ordered = [5, 6, 7, 8, 4, 9, 3, 10, 2, 1, 0, 11];
        const cells = ordered
            .map((branch) => {
                const p = chart.getPalaceAtBranch(branch);
                const life = branch === chart.lifePalacePos,
                    body = branch === chart.bodyPalacePos;
                return `<div class="palace p${branch}${life ? ' life-palace' : ''}"><div><b>${t(palaceKeys[p.index])}</b><span>${p.branch}</span></div>
        <p>${p.stars.map((star) => t(starKeys[star])).join(' · ') || t('noMajorStar')}</p>${body ? '<small>' + t('shangong') + '</small>' : ''}</div>`;
            })
            .join('');
        return `<article class="card"><div class="result-heading"><h2>${t('palacesTitle')}</h2><span class="chart-time">${t('lunarMarker')} ${chart.lunarYear} / ${isLeap ? t('leap') : ''}${chart.lunarMonth} / ${chart.lunarDay}</span></div>
      <div class="palace-grid">${cells}<div class="palace-center"><strong>${chart.wuXingJuName}</strong><span>${t('minggong')} · ${chart.lifePalaceBranch}</span><span>${t('shangong')} · ${chart.bodyPalaceBranch}</span></div></div></article>`;
    }

    function drawRadarChart(canvas, scores, animate) {
        if (!canvas || !canvas.getContext) return;
        var ctx = canvas.getContext('2d');
        var dpr = window.devicePixelRatio || 1;
        var rect = canvas.getBoundingClientRect();
        var W = rect.width || 200;
        var H = rect.height || 200;
        canvas.width = W * dpr;
        canvas.height = H * dpr;
        canvas.style.width = W + 'px';
        canvas.style.height = H + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        var cx = W / 2,
            cy = H / 2;
        var R = Math.min(W, H) * 0.36;
        var labels = ['木', '火', '土', '金', '水'];
        var theme = getComputedStyle(canvas);
        var colors = Object.fromEntries(
            labels.map((el) => [el, theme.getPropertyValue('--' + elementKeys[el]).trim()]),
        );
        var vals = labels.map(function (l) {
            return scores[l] || 0;
        });
        var maxVal = Math.max.apply(null, vals.concat([1]));
        var angleStep = (2 * Math.PI) / 5;
        var startAngle = -Math.PI / 2;
        var isDark = document.documentElement.getAttribute('data-theme') !== 'light';

        function vtx(i, frac) {
            var a = startAngle + i * angleStep;
            return { x: cx + R * frac * Math.cos(a), y: cy + R * frac * Math.sin(a) };
        }

        function drawFrame(progress) {
            ctx.clearRect(0, 0, W, H);

            // Grid rings (4 levels)
            ctx.strokeStyle = isDark ? 'rgba(212, 175, 55, 0.1)' : 'rgba(0, 0, 0, 0.08)';
            ctx.lineWidth = 0.5;
            [0.25, 0.5, 0.75, 1].forEach(function (frac) {
                ctx.beginPath();
                for (var i = 0; i <= 5; i++) {
                    var v = vtx(i % 5, frac);
                    if (i === 0) ctx.moveTo(v.x, v.y);
                    else ctx.lineTo(v.x, v.y);
                }
                ctx.closePath();
                ctx.stroke();
            });

            // Axis lines
            ctx.strokeStyle = isDark ? 'rgba(212, 175, 55, 0.08)' : 'rgba(0, 0, 0, 0.06)';
            for (var a = 0; a < 5; a++) {
                var v1 = vtx(a, 1);
                ctx.beginPath();
                ctx.moveTo(cx, cy);
                ctx.lineTo(v1.x, v1.y);
                ctx.stroke();
            }

            // Data polygon with gradient fill
            ctx.beginPath();
            for (var d = 0; d < 5; d++) {
                var frac = (vals[d] / maxVal) * progress;
                var vd = vtx(d, frac);
                if (d === 0) ctx.moveTo(vd.x, vd.y);
                else ctx.lineTo(vd.x, vd.y);
            }
            ctx.closePath();

            // Radial gradient fill
            var grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, R);
            if (isDark) {
                grad.addColorStop(0, 'rgba(212, 175, 55, 0.3)');
                grad.addColorStop(1, 'rgba(192, 57, 43, 0.15)');
            } else {
                grad.addColorStop(0, 'rgba(212, 175, 55, 0.25)');
                grad.addColorStop(1, 'rgba(192, 57, 43, 0.1)');
            }
            ctx.fillStyle = grad;
            ctx.fill();

            // Stroke
            ctx.strokeStyle = isDark ? 'rgba(212, 175, 55, 0.6)' : 'rgba(180, 140, 40, 0.5)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Data points with glow
            for (var p = 0; p < 5; p++) {
                var fp = (vals[p] / maxVal) * progress;
                var vp = vtx(p, fp);
                // Dot
                ctx.beginPath();
                ctx.arc(vp.x, vp.y, 4, 0, 2 * Math.PI);
                ctx.fillStyle = colors[labels[p]];
                ctx.fill();
                ctx.strokeStyle = isDark ? '#0a0a0f' : '#fff';
                ctx.lineWidth = 1.5;
                ctx.stroke();
            }

            // Labels
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            for (var lb = 0; lb < 5; lb++) {
                var vl = vtx(lb, 1.22);
                var elKey = { 木: 'wood', 火: 'fire', 土: 'earth', 金: 'metal', 水: 'water' }[labels[lb]];
                ctx.font = 'bold 13px system-ui, sans-serif';
                ctx.fillStyle = colors[labels[lb]];
                ctx.fillText(I18n.t(elKey), vl.x, vl.y - 8);
                ctx.font = '11px system-ui, sans-serif';
                ctx.fillStyle = isDark ? 'rgba(232, 224, 208, 0.7)' : 'rgba(28, 24, 16, 0.6)';
                ctx.fillText(vals[lb].toFixed(1), vl.x, vl.y + 8);
            }
        }

        // Animation: expand from center
        if (animate !== false && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            var start = null;
            var duration = 600;
            function step(ts) {
                if (!start) start = ts;
                var elapsed = ts - start;
                var t = Math.min(elapsed / duration, 1);
                // Ease out cubic
                var p = 1 - Math.pow(1 - t, 3);
                drawFrame(p);
                if (t < 1) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        } else {
            drawFrame(1);
        }
    }

    // -----------------------------------------------------------------------
    //  SVG Hexagram Visualization
    // -----------------------------------------------------------------------

    /**
     * Build an SVG string for a hexagram (6 lines, bottom to top).
     * @param {Array<number>} lines  [0|1, ...] bottom to top, 1=yang
     * @param {Array<number>} movingPositions  1-based positions of moving lines
     * @returns {string} SVG markup
     */
    function buildHexagramSVG(lines, movingPositions) {
        var w = 200,
            lineH = 24,
            gap = 8,
            padY = 16;
        var h = 6 * lineH + 5 * gap + 2 * padY;
        var svg =
            '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="' +
            w +
            '" height="' +
            h +
            '" viewBox="0 0 ' +
            w +
            ' ' +
            h +
            '">';

        var isDark = document.documentElement.getAttribute('data-theme') !== 'light';
        var strokeColor = isDark ? '#e8e0d0' : '#1c1810';
        var movingColor = isDark ? '#f4a48b' : '#963c2c';
        var lineW = 132,
            lx = (w - lineW) / 2;

        for (var i = 5; i >= 0; i--) {
            var row = 5 - i; // visual row 0=top
            var y = padY + row * (lineH + gap) + lineH / 2;
            var isMoving = movingPositions.indexOf(i + 1) !== -1;
            var color = isMoving ? movingColor : strokeColor;
            var sw = 4;

            if (lines[i] === 1) {
                // Yang: solid line
                svg +=
                    '<line x1="' +
                    lx +
                    '" y1="' +
                    y +
                    '" x2="' +
                    (lx + lineW) +
                    '" y2="' +
                    y +
                    '" stroke="' +
                    color +
                    '" stroke-width="' +
                    sw +
                    '" stroke-linecap="round"';
                if (isMoving) svg += ' class="moving-line"';
                svg += '/>';
            } else {
                // Yin: broken line with gap
                var half = (lineW - 20) / 2;
                svg +=
                    '<line x1="' +
                    lx +
                    '" y1="' +
                    y +
                    '" x2="' +
                    (lx + half) +
                    '" y2="' +
                    y +
                    '" stroke="' +
                    color +
                    '" stroke-width="' +
                    sw +
                    '" stroke-linecap="round"';
                if (isMoving) svg += ' class="moving-line"';
                svg += '/>';
                svg +=
                    '<line x1="' +
                    (lx + half + 20) +
                    '" y1="' +
                    y +
                    '" x2="' +
                    (lx + lineW) +
                    '" y2="' +
                    y +
                    '" stroke="' +
                    color +
                    '" stroke-width="' +
                    sw +
                    '" stroke-linecap="round"';
                if (isMoving) svg += ' class="moving-line"';
                svg += '/>';
            }

            // Position label (left)
            var posNames =
                I18n.getLang() === 'zh'
                    ? ['初', '二', '三', '四', '五', '上']
                    : ['1', '2', '3', '4', '5', '6'];
            svg +=
                '<text x="' +
                (lx - 14) +
                '" y="' +
                (y + 1) +
                '" text-anchor="end" font-size="12" fill="' +
                color +
                '">' +
                posNames[i] +
                '</text>';

            // Moving marker (right)
            if (isMoving) {
                svg +=
                    '<circle cx="' +
                    (lx + lineW + 14) +
                    '" cy="' +
                    y +
                    '" r="5" fill="' +
                    movingColor +
                    '" opacity="0.8"/>';
            }
        }
        svg += '</svg>';
        return svg;
    }

    function enableDragScroll(container) {
        if (!container) return;
        var isDown = false,
            startX,
            scrollLeft;
        container.addEventListener('mousedown', function (e) {
            isDown = true;
            startX = e.pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
            container.style.cursor = 'grabbing';
        });
        container.addEventListener('mouseleave', function () {
            isDown = false;
            container.style.cursor = 'grab';
        });
        container.addEventListener('mouseup', function () {
            isDown = false;
            container.style.cursor = 'grab';
        });
        container.addEventListener('mousemove', function (e) {
            if (!isDown) return;
            e.preventDefault();
            var x = e.pageX - container.offsetLeft;
            container.scrollLeft = scrollLeft - (x - startX);
        });
    }

    return {
        bazi,
        monthBounds,
        lunarText,
        liuyao,
        ziwei,
        buildHexagramSVG,
        drawRadarChart,
        enableDragScroll,
    };
})();
