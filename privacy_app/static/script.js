const appDiv = document.getElementById('app');

function showScanning() {
  appDiv.innerHTML = `
    <div class="flex flex-col items-center justify-center h-full w-full bg-[#1A1A2E]">
      <div class="flex flex-col items-center justify-center">
        <div class="rounded-full bg-white/10 flex items-center justify-center w-32 h-32 mb-6 border-4 border-white/20">
          <span class="text-5xl">📡</span>
          <canvas id="scan-canvas" width="80" height="80" class="absolute left-0 top-0 w-32 h-32 rounded-full"></canvas>
        </div>
        <h2 class="text-3xl font-bold mt-2 text-white">Scanning...</h2>
        <p class="mt-3 text-white/70 max-w-xs text-center">Looking for devices on your network.</p>
      </div>
    </div>
  `;
  pixelFlicker();
}

function pixelFlicker() {
  const canvas = document.getElementById('scan-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let running = true;
  function draw() {
    if (!running) return;
    for (let y = 0; y < 80; y++) {
      for (let x = 0; x < 80; x++) {
        ctx.fillStyle = `rgba(233,69,96,${Math.random() * 0.2})`;
        ctx.fillRect(x, y, 1, 1);
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
  // Stop animation when results are shown
  window.stopFlicker = () => { running = false; };
}

function showResults(devices) {
  window.stopFlicker && window.stopFlicker();
  appDiv.innerHTML = `
    <div class="flex flex-col items-center justify-center h-full w-full bg-[#1A1A2E]">
      <h2 class="text-2xl font-bold mb-4 text-white text-center">Scan Results</h2>
      <div class="overflow-y-auto w-full px-2" style="max-height: 400px;">
        ${devices.map(d => `
          <div class="rounded-lg p-4 mb-4 flex justify-between items-center shadow-lg ${d.leak ? 'bg-red-500/30 border border-red-500' : 'bg-green-500/30 border border-green-500'}">
            <div class="text-lg font-bold text-white">${d.name}</div>
            <div class="font-semibold ${d.leak ? 'text-red-400' : 'text-green-400'}">${d.status}</div>
          </div>
        `).join('')}
      </div>
      <button id="scan-again" class="fixed bottom-10 right-10 bg-[#E94560] text-white font-bold py-3 px-8 rounded-full shadow-lg hover:scale-105 transition">Scan Again</button>
    </div>
  `;
  document.getElementById('scan-again').onclick = startScan;
}

function startScan() {
  showScanning();
  setTimeout(() => {
    fetch('/scan')
      .then(res => res.json())
      .then(showResults);
  }, 3000);
}

window.onload = startScan;
