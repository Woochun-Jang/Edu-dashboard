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
 *
 * v1.1 변경사항:
 *   - TradingView 일봉차트 링크 버튼 추가 (_injectTVLink)
 *   - PRICE_DATA 엔트리에 "code" 필드 필요 (예: "475960")
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
 */
function samplePrices(allCloses, period) {
  const cfg = PERIOD_CONFIG[period] || PERIOD_CONFIG["3m"];
  const slice = allCloses.slice(-cfg.tradingDays);

  const sampled = [];
  for (let i = 0; i < slice.length; i += cfg.step) {
    sampled.push(slice[i]);
  }
  if (sampled[sampled.length - 1] !== slice[slice.length - 1]) {
    sampled.push(slice[slice.length - 1]);
  }

  return { prices: sampled, startPrice: slice[0] };
}

/**
 * 숫자 → 만원·억원 단위 표기
 */
function fmtPrice(n) {
  if (n >= 100000000) return (n / 100000000).toFixed(0) + "억";
  if (n >= 10000)     return (n / 10000).toFixed(1) + "만";
  return n.toLocaleString();
}

/* ─────────────────────────────────────────────────────────
 * TradingView 일봉차트 링크 버튼
 * ───────────────────────────────────────────────────────── */

/**
 * 종목코드 → TradingView KRX 일봉 URL
 * @param {string} code  종목코드 (예: "475960")
 */
function _getTVUrl(code) {
  return "https://kr.tradingview.com/chart/?symbol=KRX%3A" + code + "&interval=D";
}

/**
 * canvas 부모 요소에 TradingView 링크 버튼 삽입
 * (중복 삽입 방지 포함)
 * @param {HTMLCanvasElement} canvas
 * @param {string|null}       code      종목코드 (없으면 삽입 안함)
 * @param {boolean}           isDetail  상세 페이지 여부 (크기 조정)
 */
function _injectTVLink(canvas, code, isDetail) {
  if (!code) return;
  const parent = canvas.parentElement;
  if (!parent || parent.querySelector(".tv-link-btn")) return;

  /* 부모에 relative 위치 부여 (버튼 절대 위치 기준) */
  if (getComputedStyle(parent).position === "static") {
    parent.style.position = "relative";
  }

  const a = document.createElement("a");
  a.className  = "tv-link-btn";
  a.href       = _getTVUrl(code);
  a.target     = "_blank";
  a.rel        = "noopener noreferrer";
  a.title      = "TradingView에서 일봉차트 보기";

  if (isDetail) {
    /* 상세 페이지: 텍스트 포함 버튼 */
    a.innerHTML = "📈&nbsp;일봉차트";
    a.style.cssText = [
      "position:absolute",
      "top:7px",
      "right:8px",
      "font-size:10px",
      "font-weight:700",
      "color:#1565c0",
      "text-decoration:none",
      "background:rgba(238,244,255,0.93)",
      "border:1px solid #90caf9",
      "border-radius:4px",
      "padding:3px 10px",
      "cursor:pointer",
      "z-index:10",
      "transition:background 0.12s,box-shadow 0.12s",
      "box-shadow:0 1px 4px rgba(21,101,192,0.10)",
      "letter-spacing:0.02em",
    ].join(";");
    a.onmouseover = function() {
      this.style.background = "#dbeafe";
      this.style.boxShadow  = "0 2px 8px rgba(21,101,192,0.18)";
    };
    a.onmouseout = function() {
      this.style.background = "rgba(238,244,255,0.93)";
      this.style.boxShadow  = "0 1px 4px rgba(21,101,192,0.10)";
    };
  } else {
    /* 카드 스파크차트: 아이콘만 */
    a.innerHTML = "📈";
    a.style.cssText = [
      "position:absolute",
      "top:4px",
      "right:4px",
      "font-size:11px",
      "text-decoration:none",
      "background:rgba(238,244,255,0.88)",
      "border:1px solid #90caf9",
      "border-radius:3px",
      "padding:1px 4px",
      "cursor:pointer",
      "z-index:10",
      "line-height:1.5",
      "transition:background 0.1s",
    ].join(";");
    a.onmouseover = function() { this.style.background = "rgba(219,234,254,0.95)"; };
    a.onmouseout  = function() { this.style.background = "rgba(238,244,255,0.88)"; };
  }

  parent.appendChild(a);
}

/* ─────────────────────────────────────────────────────────
 * 메인 차트 렌더러
 * ───────────────────────────────────────────────────────── */

/**
 * Canvas에 주가 차트 그리기
 * @param {HTMLCanvasElement} canvas
 * @param {number}   stockId
 * @param {string}   period   "1w" | "2w" | ... | "12m"
 * @param {string}   color    hex color
 * @param {number}   height   canvas height in px  (≥120 이면 상세 페이지로 판단)
 * @param {boolean}  showVol  거래량 막대 표시 여부
 */
function drawPriceChart(canvas, stockId, period, color, height = 80, showVol = false) {
  const data = (typeof PRICE_DATA !== "undefined") ? PRICE_DATA[String(stockId)] : null;
  if (!data || !data.closes || data.closes.length < 5) {
    drawFallbackSpark(canvas, stockId, period, color, height);
    return;
  }

  const { prices, startPrice } = samplePrices(data.closes, period);
  const volumes = data.volumes ? data.volumes.slice(-PERIOD_CONFIG[period].tradingDays) : [];

  const W = canvas.width  = canvas.offsetWidth || canvas.parentElement?.offsetWidth || 300;
  const H = canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, W, H);

  const PAD_TOP    = 8;
  const PAD_BOTTOM = showVol ? 20 : 4;
  const PAD_LEFT   = 8;
  const PAD_RIGHT  = 8;
  const chartH     = H - PAD_TOP - PAD_BOTTOM;

  ctx.fillStyle = "#fafcff";
  ctx.fillRect(0, 0, W, H);

  const minP  = Math.min(...prices);
  const maxP  = Math.max(...prices);
  const range = maxP - minP || 1;
  const margin = range * 0.1;
  const yMin   = minP - margin;
  const yMax   = maxP + margin;
  const yRange = yMax - yMin;

  const xs = i => PAD_LEFT + (i / (prices.length - 1)) * (W - PAD_LEFT - PAD_RIGHT);
  const ys = p => PAD_TOP  + (1 - (p - yMin) / yRange) * chartH;

  /* 수평 그리드 */
  ctx.strokeStyle = "rgba(0,0,0,0.05)";
  ctx.lineWidth = 1;
  ctx.setLineDash([3, 3]);
  [0.25, 0.5, 0.75].forEach(r => {
    const y = PAD_TOP + r * chartH;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  });
  ctx.setLineDash([]);

  /* 등락 기준선 */
  const baseY = ys(startPrice);
  if (baseY > PAD_TOP && baseY < PAD_TOP + chartH) {
    ctx.strokeStyle = "rgba(0,0,0,0.12)";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(0, baseY); ctx.lineTo(W, baseY); ctx.stroke();
    ctx.setLineDash([]);
  }

  const lastPrice = prices[prices.length - 1];
  const lineColor = color;

  /* 그라디언트 채우기 */
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

  /* 라인 */
  ctx.beginPath();
  ctx.strokeStyle = lineColor;
  ctx.lineWidth   = 2;
  ctx.lineJoin    = "round";
  prices.forEach((p, i) => {
    if (i === 0) ctx.moveTo(xs(0), ys(p));
    else         ctx.lineTo(xs(i), ys(p));
  });
  ctx.stroke();

  /* 현재가 닷 */
  const lx = xs(prices.length - 1);
  const ly = ys(lastPrice);
  ctx.beginPath();
  ctx.arc(lx, ly, 4, 0, Math.PI * 2);
  ctx.fillStyle   = lineColor;
  ctx.fill();
  ctx.strokeStyle = "#fff";
  ctx.lineWidth   = 1.5;
  ctx.stroke();

  /* 현재가 라벨 */
  const priceTxt = lastPrice.toLocaleString();
  const txtW     = ctx.measureText(priceTxt).width + 8;
  const lblX     = Math.min(lx - txtW / 2, W - txtW - 2);
  const lblY     = ly < PAD_TOP + 16 ? ly + 14 : ly - 8;
  ctx.font      = "bold 10px 'JetBrains Mono', monospace";
  ctx.fillStyle = lineColor;
  ctx.fillText(priceTxt, Math.max(2, lblX), lblY);

  /* 거래량 막대 */
  if (showVol && volumes.length > 0) {
    const volSlice = volumes.slice(-PERIOD_CONFIG[period].tradingDays);
    const maxVol   = Math.max(...volSlice);
    const volH     = 14;
    const volTop   = H - volH;
    const barW     = Math.max(1, (W - PAD_LEFT - PAD_RIGHT) / volSlice.length - 1);
    volSlice.forEach((v, i) => {
      const bH = (v / maxVol) * volH;
      const bX = PAD_LEFT + (i / volSlice.length) * (W - PAD_LEFT - PAD_RIGHT);
      ctx.fillStyle = lineColor + "55";
      ctx.fillRect(bX, volTop + volH - bH, barW, bH);
    });
  }

  /* ── TradingView 일봉 링크 버튼 삽입 ── */
  _injectTVLink(canvas, data.code || null, height >= 120);
}

/* ─────────────────────────────────────────────────────────
 * Fallback: PRICE_DATA 없을 때 CHART_DATA로 렌더
 * ───────────────────────────────────────────────────────── */

function drawFallbackSpark(canvas, stockId, period, color, height) {
  const all = (typeof CHART_DATA !== "undefined") ? CHART_DATA[stockId] : null;
  if (!all) return;

  const cfg   = PERIOD_CONFIG[period] || PERIOD_CONFIG["3m"];
  const slice = all.slice(-cfg.tradingDays);
  const pts   = [];
  for (let i = 0; i < slice.length; i += cfg.step) pts.push(slice[i]);
  if (pts[pts.length - 1] !== slice[slice.length - 1]) pts.push(slice[slice.length - 1]);

  const W = canvas.width  = canvas.offsetWidth || 300;
  const H = canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#fafcff"; ctx.fillRect(0, 0, W, H);

  const n  = pts.length;
  const xs = i => i / (n - 1) * W;
  const ys = v => (1 - v / 100) * H;

  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, color + "44"); grad.addColorStop(1, color + "06");
  ctx.beginPath(); ctx.moveTo(xs(0), H);
  pts.forEach((v, i) => ctx.lineTo(xs(i), ys(v)));
  ctx.lineTo(xs(n - 1), H); ctx.closePath();
  ctx.fillStyle = grad; ctx.fill();

  ctx.beginPath(); ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.lineJoin = "round";
  pts.forEach((v, i) => { if (!i) ctx.moveTo(xs(0), ys(v)); else ctx.lineTo(xs(i), ys(v)); });
  ctx.stroke();

  /* fallback에서도 PRICE_DATA에 code가 있으면 링크 삽입 */
  const data = (typeof PRICE_DATA !== "undefined") ? PRICE_DATA[String(stockId)] : null;
  if (data?.code) _injectTVLink(canvas, data.code, height >= 120);
}

/* ─────────────────────────────────────────────────────────
 * 카드용 현재가 HTML 생성
 * ───────────────────────────────────────────────────────── */

function getPriceInfoHTML(stockId) {
  const data = (typeof PRICE_DATA !== "undefined") ? PRICE_DATA[String(stockId)] : null;
  if (!data) return "";

  const chgUp = data.chgAmt >= 0;
  const color = chgUp ? "#cc2233" : "#1565c0";
  const arrow = chgUp ? "▲" : "▼";
  const sign  = chgUp ? "+" : "";

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
