/**
 * chart_module.js
 * ===============
 * 실제 주가 차트 렌더링 모듈
 * stocks_data.js 에서 PRICE_DATA를 읽어 Canvas에 그림
 *
 * 기간별 샘플링 전략:
 *   1w  = 매일 종가 (5 거래일)
 *   2w  = 2일 간격 종가 (10 거래일 → 5포인트)
 *   3w  = 3일 간격 (15 거래일 → 5포인트)
 *   4w  = 4일 간격 (20 거래일 → 5포인트)
 *   2m  = 2일 간격 (40 거래일 → 20포인트)
 *   3m  = 매일 (60 거래일)
 *   6m  = 2일 간격 (120 거래일 → 60포인트)
 *   9m  = 3일 간격 (180 거래일 → 60포인트)
 *   12m = 4일 간격 (250 거래일 → 62포인트)
 */

const PERIOD_CONFIG = {
  "1w":  { tradingDays: 5,   step: 1,  label: "1주"   },
  "2w":  { tradingDays: 10,  step: 2,  label: "2주"   },
  "3w":  { tradingDays: 15,  step: 3,  label: "3주"   },
  "4w":  { tradingDays: 20,  step: 4,  label: "4주"   },
  "2m":  { tradingDays: 40,  step: 2,  label: "2개월" },
  "3m":  { tradingDays: 60,  step: 1,  label: "3개월" },
  "6m":  { tradingDays: 120, step: 2,  label: "6개월" },
  "9m":  { tradingDays: 180, step: 3,  label: "9개월" },
  "12m": { tradingDays: 250, step: 4,  label: "12개월"},
};

/**
 * 기간 설정에 따라 종가 배열을 샘플링
 * @param {number[]} allCloses - 전체 종가 배열 (오래된→최신 순)
 * @param {string}   period    - "1w" | "2w" | ... | "12m"
 * @returns {{ prices: number[], startPrice: number }}
 */
function samplePrices(allCloses, period) {
  const cfg = PERIOD_CONFIG[period] || PERIOD_CONFIG["3m"];
  const slice = allCloses.slice(-cfg.tradingDays);

  const sampled = [];
  for (let i = 0; i < slice.length; i += cfg.step) {
    sampled.push(slice[i]);
  }
  // 마지막 데이터(최신)는 반드시 포함
  if (sampled[sampled.length - 1] !== slice[slice.length - 1]) {
    sampled.push(slice[slice.length - 1]);
  }

  return {
    prices: sampled,
    startPrice: slice[0],
  };
}

/**
 * 숫자 → 만원·억원 단위 표기
 */
function fmtPrice(n) {
  if (n >= 100000000) return (n / 100000000).toFixed(0) + "억";
  if (n >= 10000)     return (n / 10000).toFixed(1) + "만";
  return n.toLocaleString();
}

/**
 * Canvas에 주가 차트 그리기
 * @param {HTMLCanvasElement} canvas
 * @param {number}   stockId
 * @param {string}   period   "1w" | "2w" | ... | "12m"
 * @param {string}   color    hex color
 * @param {number}   height   canvas height in px
 * @param {boolean}  showVol  거래량 막대 표시 여부
 */
function drawPriceChart(canvas, stockId, period, color, height = 80, showVol = false) {
  const data = (typeof PRICE_DATA !== "undefined") ? PRICE_DATA[String(stockId)] : null;
  if (!data || !data.closes || data.closes.length < 5) {
    // fallback: PRICE_DATA 없으면 기존 스파크라인(CHART_DATA) 사용
    drawFallbackSpark(canvas, stockId, period, color, height);
    return;
  }

  const { prices, startPrice } = samplePrices(data.closes, period);
  const volumes = data.volumes ? data.volumes.slice(-PERIOD_CONFIG[period].tradingDays) : [];

  const W = canvas.width  = canvas.offsetWidth || canvas.parentElement?.offsetWidth || 300;
  const H = canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, W, H);

  // ── 레이아웃 ──────────────────────────────────────────────
  const PAD_TOP    = 8;
  const PAD_BOTTOM = showVol ? 20 : 4;  // 거래량 영역
  const PAD_LEFT   = 8;
  const PAD_RIGHT  = 8;
  const chartH     = H - PAD_TOP - PAD_BOTTOM;

  // ── 배경 ────────────────────────────────────────────────
  ctx.fillStyle = "#fafcff";
  ctx.fillRect(0, 0, W, H);

  const minP  = Math.min(...prices);
  const maxP  = Math.max(...prices);
  const range = maxP - minP || 1;

  // Y축 여백 10%
  const margin = range * 0.1;
  const yMin   = minP - margin;
  const yMax   = maxP + margin;
  const yRange = yMax - yMin;

  const xs = i => PAD_LEFT + (i / (prices.length - 1)) * (W - PAD_LEFT - PAD_RIGHT);
  const ys = p => PAD_TOP  + (1 - (p - yMin) / yRange) * chartH;

  // ── 수평 그리드 (3줄) ──────────────────────────────────
  ctx.strokeStyle = "rgba(0,0,0,0.05)";
  ctx.lineWidth = 1;
  ctx.setLineDash([3, 3]);
  [0.25, 0.5, 0.75].forEach(r => {
    const y = PAD_TOP + r * chartH;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  });
  ctx.setLineDash([]);

  // ── 등락 기준선 (시작가) ───────────────────────────────
  const baseY = ys(startPrice);
  if (baseY > PAD_TOP && baseY < PAD_TOP + chartH) {
    ctx.strokeStyle = "rgba(0,0,0,0.12)";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(0, baseY); ctx.lineTo(W, baseY); ctx.stroke();
    ctx.setLineDash([]);
  }

  // ── 색상 결정 (등락) ──────────────────────────────────
  const lastPrice = prices[prices.length - 1];
  const isUp   = lastPrice >= startPrice;
  const lineColor = color; // 섹터 컬러 유지 (또는 isUp ? "#cc2233" : "#1565c0")

  // ── 그라디언트 채우기 ──────────────────────────────────
  const grad = ctx.createLinearGradient(0, PAD_TOP, 0, PAD_TOP + chartH);
  grad.addColorStop(0, lineColor + "44");
  grad.addColorStop(1, lineColor + "06");

  ctx.beginPath();
  ctx.moveTo(xs(0), PAD_TOP + chartH);
  prices.forEach((p, i) => ctx.lineTo(xs(i), ys(p)));
  ctx.lineTo(xs(prices.length - 1), PAD_TOP + chartH);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // ── 라인 ─────────────────────────────────────────────
  ctx.beginPath();
  ctx.strokeStyle = lineColor;
  ctx.lineWidth   = 2;
  ctx.lineJoin    = "round";
  prices.forEach((p, i) => {
    if (i === 0) ctx.moveTo(xs(0), ys(p));
    else         ctx.lineTo(xs(i), ys(p));
  });
  ctx.stroke();

  // ── 현재가 닷 ────────────────────────────────────────
  const lx = xs(prices.length - 1);
  const ly = ys(lastPrice);
  ctx.beginPath();
  ctx.arc(lx, ly, 4, 0, Math.PI * 2);
  ctx.fillStyle   = lineColor;
  ctx.fill();
  ctx.strokeStyle = "#fff";
  ctx.lineWidth   = 1.5;
  ctx.stroke();

  // ── 현재가 라벨 ──────────────────────────────────────
  const priceTxt = lastPrice.toLocaleString();
  const txtW     = ctx.measureText(priceTxt).width + 8;
  const lblX     = Math.min(lx - txtW / 2, W - txtW - 2);
  const lblY     = ly < PAD_TOP + 16 ? ly + 14 : ly - 8;

  ctx.font      = "bold 10px 'JetBrains Mono', monospace";
  ctx.fillStyle = lineColor;
  ctx.fillText(priceTxt, Math.max(2, lblX), lblY);

  // ── 거래량 막대 ──────────────────────────────────────
  if (showVol && volumes.length > 0) {
    const volSlice  = volumes.slice(-PERIOD_CONFIG[period].tradingDays);
    const maxVol    = Math.max(...volSlice);
    const volH      = 14; // px
    const volTop    = H - volH;
    const barW      = Math.max(1, (W - PAD_LEFT - PAD_RIGHT) / volSlice.length - 1);

    volSlice.forEach((v, i) => {
      const bH  = (v / maxVol) * volH;
      const bX  = PAD_LEFT + (i / volSlice.length) * (W - PAD_LEFT - PAD_RIGHT);
      ctx.fillStyle = lineColor + "55";
      ctx.fillRect(bX, volTop + volH - bH, barW, bH);
    });
  }
}

/**
 * PRICE_DATA 없을 때 기존 CHART_DATA로 폴백
 */
function drawFallbackSpark(canvas, stockId, period, color, height) {
  const all = (typeof CHART_DATA !== "undefined") ? CHART_DATA[stockId] : null;
  if (!all) return;

  const cfg    = PERIOD_CONFIG[period] || PERIOD_CONFIG["3m"];
  const slice  = all.slice(-cfg.tradingDays);
  const pts    = [];
  for (let i = 0; i < slice.length; i += cfg.step) pts.push(slice[i]);
  if (pts[pts.length-1] !== slice[slice.length-1]) pts.push(slice[slice.length-1]);

  // 0~100 → 상대 위치로 렌더 (간이 버전)
  const W = canvas.width  = canvas.offsetWidth || 300;
  const H = canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#fafcff"; ctx.fillRect(0, 0, W, H);

  const n  = pts.length;
  const xs = i => i / (n-1) * W;
  const ys = v => (1 - v/100) * H;

  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, color + "44"); grad.addColorStop(1, color + "06");
  ctx.beginPath(); ctx.moveTo(xs(0), H);
  pts.forEach((v, i) => ctx.lineTo(xs(i), ys(v)));
  ctx.lineTo(xs(n-1), H); ctx.closePath();
  ctx.fillStyle = grad; ctx.fill();

  ctx.beginPath(); ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.lineJoin = "round";
  pts.forEach((v, i) => { if (!i) ctx.moveTo(xs(0), ys(v)); else ctx.lineTo(xs(i), ys(v)); });
  ctx.stroke();
}

/**
 * 카드에 표시할 현재가 정보 HTML 생성
 * @param {number} stockId
 * @returns {string} HTML string
 */
function getPriceInfoHTML(stockId) {
  const data = (typeof PRICE_DATA !== "undefined") ? PRICE_DATA[String(stockId)] : null;
  if (!data) return "";

  const chgUp  = data.chgAmt >= 0;
  const color  = chgUp ? "#cc2233" : "#1565c0";
  const arrow  = chgUp ? "▲" : "▼";
  const sign   = chgUp ? "+" : "";

  return `
    <span style="color:${color};font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:800">
      ${data.current.toLocaleString()}원
    </span>
    <span style="color:${color};font-size:11px;margin-left:6px">
      ${arrow} ${sign}${data.chgAmt.toLocaleString()} (${sign}${data.chgPct}%)
    </span>
    <span style="font-size:9px;color:#94a3b8;margin-left:6px">${data.updatedAt}</span>
  `;
}
