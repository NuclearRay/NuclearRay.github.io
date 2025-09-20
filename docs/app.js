// Game Currency Optimizer - GitHub Pages (static)
// DP algorithms implemented in JS. Custom packages stored in localStorage.

(function () {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  const STORAGE_KEY = 'customPackages';

  function loadCustomPackages() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const arr = JSON.parse(raw);
      return Array.isArray(arr) ? arr : [];
    } catch {
      return [];
    }
  }

  function saveCustomPackages(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }

  function presets(preset) {
    // Align with Python presets (including user-updated LoL values)
    const defaults = [
      { name: 'Starter Pack', cost: 0.99, coins: 100 },
      { name: 'Value Pack', cost: 4.99, coins: 600 },
      { name: 'Popular Pack', cost: 9.99, coins: 1300 },
      { name: 'Great Deal', cost: 19.99, coins: 2800 },
      { name: 'Best Value', cost: 49.99, coins: 7500 },
      { name: 'Ultimate Pack', cost: 99.99, coins: 16000 },
    ];

    if (!preset || preset === '') return defaults;

    switch (preset) {
      case 'starter':
        return [
          { name: "Tiny Pouch", cost: 0.99, coins: 90 },
          { name: "Small Pouch", cost: 2.99, coins: 300 },
          { name: "Starter Bundle", cost: 5.99, coins: 650 },
        ];
      case 'mid_range':
        return [
          { name: "Scout Pack", cost: 3.99, coins: 420 },
          { name: "Adventurer Pack", cost: 7.99, coins: 900 },
          { name: "Explorer Pack", cost: 14.99, coins: 1900 },
          { name: "Champion Pack", cost: 24.99, coins: 3300 },
        ];
      case 'premium':
        return [
          { name: "Premium I", cost: 9.99, coins: 1400 },
          { name: "Premium II", cost: 19.99, coins: 3000 },
          { name: "Premium III", cost: 49.99, coins: 8200 },
          { name: "Premium Ultimate", cost: 99.99, coins: 17000 },
        ];
      case 'league_of_legends':
        return [
          { name: 'Riot Point Small', cost: 4.99, coins: 575 },
          { name: 'Riot Point Medium', cost: 10.99, coins: 1380 },
          { name: 'Riot Point Large', cost: 21.99, coins: 2800 },
          { name: 'Riot Point XL', cost: 34.99, coins: 4500 },
          { name: 'Riot Point Ultimate', cost: 49.99, coins: 6500 },
          { name: 'Riot Point Ultimate X', cost: 99.99, coins: 13500 },
          { name: 'Riot Point Ultimate XX', cost: 244.99, coins: 33500 },
          { name: 'Riot Point Ultimate XXX', cost: 429.99, coins: 60200 },
        ];
      case 'custom':
        const c = loadCustomPackages();
        return c.length ? c : defaults;
      default:
        return defaults;
    }
  }

  // Utilities
  function toEff(pkg) { return pkg.coins / pkg.cost; }

  function renderTable(container, rows, headers) {
    if (!rows || rows.length === 0) {
      container.innerHTML = '<p class="text-secondary">No data.</p>';
      return;
    }
    const thead = `<thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>`;
    const tbody = `<tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody>`;
    container.innerHTML = `<div class="table-responsive"><table class="table table-sm align-middle">${thead}${tbody}</table></div>`;
  }

  // DP: Min cost to reach at least target
  function optimizeMinCost(packages, target) {
    if (target <= 0) return { cost: 0, plan: new Map(), total: 0 };
    const minCoins = Math.min(...packages.map(p => p.coins));
    const ext = target + minCoins;
    const INF = 1e18;
    const dp = new Array(ext + 1).fill(INF);
    const parent = new Array(ext + 1).fill(null);
    dp[0] = 0;

    for (let i = 1; i <= ext; i++) {
      for (const p of packages) {
        if (p.coins <= i) {
          const cost = dp[i - p.coins] + p.cost;
          if (cost < dp[i]) {
            dp[i] = cost;
            parent[i] = p;
          }
        }
      }
    }
    let best = target;
    let bestCost = INF;
    for (let i = target; i <= ext; i++) {
      if (dp[i] < bestCost) { bestCost = dp[i]; best = i; }
    }
    const plan = new Map();
    let cur = best;
    while (cur > 0 && parent[cur]) {
      const p = parent[cur];
      plan.set(p, (plan.get(p) || 0) + 1);
      cur -= p.coins;
    }
    return { cost: bestCost, plan, total: best };
  }

  // DP: Exact sum (unbounded); returns null if impossible
  function exactUnbounded(packages, target) {
    if (target <= 0) return { cost: 0, plan: new Map(), total: 0 };
    const INF = 1e18;
    const dp = new Array(target + 1).fill(INF);
    const parent = new Array(target + 1).fill(null);
    dp[0] = 0;
    for (let i = 1; i <= target; i++) {
      for (const p of packages) {
        if (p.coins <= i) {
          const cost = dp[i - p.coins] + p.cost;
          if (cost < dp[i]) { dp[i] = cost; parent[i] = p; }
        }
      }
    }
    if (dp[target] >= INF) return null;
    const plan = new Map();
    let cur = target;
    while (cur > 0 && parent[cur]) {
      const p = parent[cur];
      plan.set(p, (plan.get(p) || 0) + 1);
      cur -= p.coins;
    }
    if (cur !== 0) return null;
    return { cost: dp[target], plan, total: target };
  }

  function exactOrScaled(packages, target, maxK) {
    const first = exactUnbounded(packages, target);
    if (first) return { k: 1, ...first };
    for (let k = 2; k <= maxK; k++) {
      const res = exactUnbounded(packages, k * target);
      if (res) return { k, ...res };
    }
    return null;
  }

  // Spend optimization (budget, item costs)
  function optimizeSpendUnbounded(budget, costs) {
    const reachable = new Array(budget + 1).fill(false);
    const parent = new Array(budget + 1).fill(null);
    reachable[0] = true;
    for (let i = 1; i <= budget; i++) {
      for (const c of costs) {
        if (c <= i && reachable[i - c]) { reachable[i] = true; parent[i] = c; break; }
      }
    }
    let spent = budget;
    while (spent >= 0 && !reachable[spent]) spent--;
    if (spent < 0) return { spent: 0, counts: {} };
    const counts = {};
    let cur = spent;
    while (cur > 0 && parent[cur] != null) {
      const c = parent[cur];
      counts[c] = (counts[c] || 0) + 1;
      cur -= c;
    }
    return { spent, counts };
  }

  function optimizeSpend01(budget, costs) {
    const n = costs.length;
    const dp = Array.from({ length: n + 1 }, () => new Array(budget + 1).fill(false));
    dp[0][0] = true;
    for (let i = 1; i <= n; i++) {
      const ci = costs[i - 1];
      for (let b = 0; b <= budget; b++) {
        if (dp[i - 1][b]) dp[i][b] = true;
        if (b - ci >= 0 && dp[i - 1][b - ci]) dp[i][b] = true;
      }
    }
    let spent = budget;
    while (spent >= 0 && !dp[n][spent]) spent--;
    if (spent < 0) return { spent: 0, counts: {} };
    const counts = {};
    let b = spent;
    for (let i = n; i >= 1; i--) {
      const ci = costs[i - 1];
      if (dp[i - 1][b]) continue;
      if (b - ci >= 0 && dp[i - 1][b - ci]) { counts[ci] = (counts[ci] || 0) + 1; b -= ci; }
    }
    return { spent, counts };
  }

  // Render custom packages list
  function renderCustomList() {
    const list = loadCustomPackages();
    const container = $('#custom-list');
    if (!container) return;
    if (!list.length) { container.innerHTML = '<p class="text-secondary small">No custom packages yet.</p>'; return; }
    const rows = list.map((x, i) => [
      `${i}`, x.name, `$${x.cost.toFixed(2)}`, `${x.coins}`,
      `<button class="btn btn-sm btn-outline-danger" data-remove="${i}">Remove</button>`
    ]);
    renderTable(container, rows, ['#', 'Name', 'Cost', 'Coins', '']);
    container.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-remove]');
      if (!btn) return;
      const idx = parseInt(btn.getAttribute('data-remove'));
      const items = loadCustomPackages();
      if (idx >= 0 && idx < items.length) {
        items.splice(idx, 1);
        saveCustomPackages(items);
        renderCustomList();
      }
    }, { once: true });
  }

  // Event wiring
  function initEvents() {
    const addBtn = $('#add-custom');
    if (addBtn) {
      addBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const name = $('#c-name').value.trim() || 'Custom Package';
        const cost = parseFloat($('#c-cost').value);
        const coins = parseInt($('#c-coins').value, 10);
        if (!(cost > 0 && coins > 0)) return;
        const items = loadCustomPackages();
        items.push({ name, cost, coins });
        saveCustomPackages(items);
        $('#c-name').value = '';
        $('#c-cost').value = '';
        $('#c-coins').value = '';
        renderCustomList();
      });
    }

    const clearBtn = $('#clear-custom');
    if (clearBtn) {
      clearBtn.addEventListener('click', (e) => {
        e.preventDefault();
        saveCustomPackages([]);
        renderCustomList();
      });
    }

    // Optimize min cost
    const btnOptimize = $('#btn-optimize');
    if (btnOptimize) {
      btnOptimize.addEventListener('click', () => {
        const preset = $('#preset').value;
        const pkgs = preset === 'custom' ? loadCustomPackages() : presets(preset);
        const target = parseInt($('#opt-target').value, 10) || 0;
        const res = optimizeMinCost(pkgs, target);
        const rows = Array.from(res.plan.entries()).map(([p, qty]) => [p.name, `$${p.cost.toFixed(2)}`, `${qty}`, `${p.coins * qty}`, `$${(p.cost * qty).toFixed(2)}`]);
        const container = $('#optimize-result');
        if (!rows.length) {
          container.innerHTML = '<p class="text-secondary">No plan (target may be 0).</p>';
        } else {
          const metrics = `
            <div class="row g-3">
              <div class="col-6 col-md-3"><div class="small text-secondary">Target</div><div class="fs-6">${target}</div></div>
              <div class="col-6 col-md-3"><div class="small text-secondary">Min Cost</div><div class="fs-6">$${res.cost.toFixed(2)}</div></div>
              <div class="col-6 col-md-3"><div class="small text-secondary">Coins</div><div class="fs-6">${res.total}</div></div>
              <div class="col-6 col-md-3"><div class="small text-secondary">Efficiency</div><div class="fs-6">${(res.total / res.cost).toFixed(2)} coins/$</div></div>
            </div>
          `;
          container.innerHTML = metrics;
          const holder = document.createElement('div');
          holder.className = 'mt-3';
          container.appendChild(holder);
          renderTable(holder, rows, ['Package', 'Cost', 'Qty', 'Coins', 'Subtotal']);
        }
      });
    }

    // Exact/Scaled
    const btnExact = $('#btn-exact');
    if (btnExact) {
      btnExact.addEventListener('click', () => {
        const preset = $('#preset').value;
        const pkgs = preset === 'custom' ? loadCustomPackages() : presets(preset);
        const target = parseInt($('#exact-target').value, 10) || 0;
        const maxk = parseInt($('#exact-maxk').value, 10) || 100;
        const res = exactOrScaled(pkgs, target, maxk);
        const container = $('#exact-result');
        if (!res) {
          container.innerHTML = `<div class="alert alert-warning">No exact solution for ${target} or any multiple up to ${maxk}×.</div>`;
          return;
        }
        const rows = Array.from(res.plan.entries()).map(([p, qty]) => [p.name, `$${p.cost.toFixed(2)}`, `${qty}`, `${p.coins * qty}`, `$${(p.cost * qty).toFixed(2)}`]);
        const metrics = `
          <div class="row g-3">
            <div class="col-6 col-md-3"><div class="small text-secondary">Base Target</div><div class="fs-6">${target}</div></div>
            <div class="col-6 col-md-2"><div class="small text-secondary">k</div><div class="fs-6">${res.k}×</div></div>
            <div class="col-6 col-md-3"><div class="small text-secondary">Exact Coins</div><div class="fs-6">${res.total}</div></div>
            <div class="col-6 col-md-4"><div class="small text-secondary">Cost</div><div class="fs-6">$${res.cost.toFixed(2)}</div></div>
          </div>
        `;
        container.innerHTML = metrics;
        const holder = document.createElement('div');
        holder.className = 'mt-3';
        container.appendChild(holder);
        renderTable(holder, rows, ['Package', 'Cost', 'Qty', 'Coins', 'Subtotal']);
      });
    }

    // Spend
    const btnSpend = $('#btn-spend');
    if (btnSpend) {
      btnSpend.addEventListener('click', () => {
        const budget = parseInt($('#spend-budget').value, 10) || 0;
        const costs = ($('#spend-costs').value || '')
          .split(',')
          .map(x => parseInt(x.trim(), 10))
          .filter(x => Number.isFinite(x) && x > 0)
          .sort((a,b)=>a-b);
        const repeat = $('#spend-repeat').value === 'y';
        const res = repeat ? optimizeSpendUnbounded(budget, costs) : optimizeSpend01(budget, costs);
        const container = $('#spend-result');
        const rows = Object.keys(res.counts).sort((a,b)=>b-a).map(k => {
          const c = parseInt(k, 10); const q = res.counts[k]; return [c, q, c*q];
        });
        const metrics = `
          <div class="row g-3">
            <div class="col-4"><div class="small text-secondary">Budget</div><div class="fs-6">${budget}</div></div>
            <div class="col-4"><div class="small text-secondary">Spent</div><div class="fs-6">${res.spent}</div></div>
            <div class="col-4"><div class="small text-secondary">Leftover</div><div class="fs-6">${budget - res.spent}</div></div>
          </div>
        `;
        container.innerHTML = metrics;
        const holder = document.createElement('div');
        holder.className = 'mt-3';
        container.appendChild(holder);
        if (rows.length) {
          renderTable(holder, rows, ['Item Cost', 'Qty', 'Subtotal']);
        } else {
          holder.innerHTML = '<p class="text-secondary">No items could be purchased with the given constraints.</p>';
        }
      });
    }

    // Analyze
    function renderAnalyze() {
      const preset = $('#preset').value;
      const pkgs = preset === 'custom' ? loadCustomPackages() : presets(preset);
      const rows = pkgs
        .map(p => ({ name: p.name, cost: p.cost, coins: p.coins, eff: toEff(p), cpc: p.cost / p.coins }))
        .sort((a, b) => b.eff - a.eff)
        .map(p => [p.name, `$${p.cost.toFixed(2)}`, `${p.coins}`, p.eff.toFixed(2), `$${p.cpc.toFixed(4)}`]);
      renderTable($('#analyze-result'), rows, ['Package', 'Cost', 'Currency', 'Coins/$', '$/Coin']);
    }

    $('#preset').addEventListener('change', () => {
      renderAnalyze();
    });

    renderCustomList();
    renderAnalyze();
  }

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', initEvents);
})();
