// script.js - scanning flow + animation + fetch results

document.addEventListener("DOMContentLoaded", () => {
    const scanBtn = document.getElementById("scanAgainBtn");
    scanBtn.addEventListener("click", startScan);
    startScan(); // start immediately
  });
  
  function getScanningHTML() {
    return `
      <div class="h-full flex flex-col items-center justify-center text-center">
        <div id="radar" class="relative w-40 h-40 rounded-full overflow-hidden bg-black/10 flex items-center justify-center">
          <canvas id="radarCanvas" width="160" height="160"></canvas>
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
            <span class="text-4xl">📡</span>
          </div>
        </div>
        <h2 class="text-2xl font-bold mt-8">Scanning...</h2>
        <p class="mt-2 text-white/70 max-w-xs">Looking for devices on your network. This takes a few seconds.</p>
      </div>
    `;
  }
  
  function startScan() {
    document.getElementById("scanAgainBtn").classList.add("hidden");
    const screen = document.getElementById("screen");
    screen.innerHTML = getScanningHTML();
    startPixelFlicker("radarCanvas");
    // After 3s, fetch real results
    setTimeout(fetchResults, 3000);
  }
  
  async function fetchResults() {
    try {
      const res = await fetch("/api/events?n=50");
      if (!res.ok) throw new Error("Network response was not ok");
      const data = await res.json();
      renderResults(data.events || []);
    } catch (err) {
      console.error(err);
      renderResults([], "Unable to reach server.");
    }
  }
  
  function renderResults(events, errorMsg) {
    const screen = document.getElementById("screen");
    let html = `
      <div class="h-full flex flex-col">
        <h2 class="text-xl font-bold mb-4">Scan Results</h2>
        <div id="results-container" class="space-y-3 overflow-y-auto flex-1 pr-1">
    `;
    if (errorMsg) {
      html += `<div class="text-red-400 p-3 rounded-lg bg-red-900/10">${errorMsg}</div>`;
    }
    if (!events || events.length === 0) {
      html += `<div class="flex items-center justify-center flex-1 text-white/60">No network activity captured yet. Try again after some browsing.</div>`;
    } else {
      events.forEach(e => {
        const verdict = (e.verdict || '').toUpperCase();
        const colorBg = verdict === 'RISK' ? 'bg-red-600/20' : verdict === 'SAFE' ? 'bg-green-600/15' : 'bg-yellow-600/15';
        const textColor = verdict === 'RISK' ? 'text-red-300' : verdict === 'SAFE' ? 'text-green-300' : 'text-yellow-300';
        const title = e.process_name ? `${e.process_name} (pid ${e.pid ?? '?'})` : `pid ${e.pid ?? '?'}`;
        const left = e.laddr ? e.laddr : '';
        const right = e.raddr ? e.raddr : '';
        const ts = e.timestamp ? new Date(e.timestamp * (e.timestamp > 10_000_000_000 ? 1 : 1000)).toLocaleString() : '';
        html += `
          <div class="p-3 rounded-lg ${colorBg} flex justify-between items-center">
            <div>
              <div class="font-semibold">${escapeHtml(title)}</div>
              <div class="text-xs text-white/60">${escapeHtml(ts)}</div>
              <div class="text-xs text-white/60">${escapeHtml(left)} → ${escapeHtml(right)}</div>
            </div>
            <div class="text-sm ${textColor} text-right">${escapeHtml((e.verdict || '').toString())}</div>
          </div>
        `;
      });
    }
  
    html += `</div></div>`;
    screen.innerHTML = html;
    document.getElementById("scanAgainBtn").classList.remove("hidden");
  }
  
  // sanitize simple text
  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, (m)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }
  
  /* ---------------- PIXEL FLICKER (simple, efficient) ---------------- */
  function startPixelFlicker(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let w = canvas.width, h = canvas.height;
    const gap = 6;
    const pixels = [];
  
    function init() {
      pixels.length = 0;
      for (let x = 0; x < w; x += gap) {
        for (let y = 0; y < h; y += gap) {
          pixels.push({
            x, y,
            size: Math.floor(gap * 0.8),
            base: Math.random() * 0.6 + 0.3,
            phase: Math.random() * Math.PI * 2,
            speed: (Math.random() * 0.02) + 0.01
          });
        }
      }
    }
  
    function resize() {
      // keep CSS size in sync if container changes
      const rect = canvas.getBoundingClientRect();
      const scaleX = Math.round(rect.width);
      const scaleY = Math.round(rect.height);
      if (scaleX !== w || scaleY !== h) {
        w = canvas.width = scaleX;
        h = canvas.height = scaleY;
        init();
      }
    }
  
    function draw(t) {
      ctx.clearRect(0,0,w,h);
      for (let p of pixels) {
        const alpha = Math.max(0, Math.min(1, p.base + Math.sin(p.phase + t * p.speed) * 0.5));
        ctx.fillStyle = `rgba(233,69,96,${alpha})`; // pink-red
        ctx.fillRect(p.x, p.y, p.size, p.size);
      }
      requestAnimationFrame(draw);
    }
  
    // initialize with current visible size
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
    w = canvas.width;
    h = canvas.height;
    init();
    let resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(parent);
    requestAnimationFrame((ts)=>draw(ts/1000));
  }
  