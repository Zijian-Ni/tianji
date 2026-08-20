/* AURORA SKIN · Theme B「链墨」 — 天机 effects (CSP-safe, self-hosted)
   Injects the paper-fiber grain layer and the cinnabar seal in the hero. */
(function () {
  'use strict';
  function boot() {
    if (!document.querySelector('.ink-grain')) {
      var g = document.createElement('div');
      g.className = 'ink-grain';
      g.setAttribute('aria-hidden', 'true');
      document.body.prepend(g);
    }
    var hero = document.querySelector('.hero');
    if (hero && !hero.querySelector('.ink-seal')) {
      var seal = document.createElement('div');
      seal.className = 'ink-seal';
      seal.setAttribute('aria-hidden', 'true');
      seal.textContent = '天机';
      hero.appendChild(seal);
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
