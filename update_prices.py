#!/usr/bin/env python3
"""
update_prices.py
================
GitHub Actions에서 매일 실행 → stocks_data.js 자동 생성
수정 포인트:
  1. 모든 종목 처리 (기존 1개 → 전체)
  2. 250 거래일 히스토리 확보 (기존 20개 → 약 1.2년치)
  3. "code" 필드 추가 → TradingView 일봉차트 링크 지원

사용법:
  pip install yfinance
  python update_prices.py

출력:
  stocks_data.js  (같은 디렉터리에 생성)
"""

import json
import re
from datetime import datetime, timezone, timedelta
import yfinance as yf

# ── KST 기준 현재 시각 ───────────────────────────────────
KST = timezone(timedelta(hours=9))
NOW_KST = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")

# ══════════════════════════════════════════════════════════
#  종목 매핑 테이블
#  형식: { "HTML_STOCKS_배열_ID": ("종목코드", "Yahoo_티커") }
#
#  ※ HTML 장우천_포트폴리오.html 의 STOCKS 배열 id와 일치해야 함
#  ※ KS = KOSPI (.KS), KQ = KOSDAQ (.KQ)
# ══════════════════════════════════════════════════════════
STOCK_MAP = {
    # ── 바이오·AI신약 ──────────────────────────────────────
    "1":  ("475960", "475960.KQ"),  # 토모큐브
    "2":  ("950200", "950200.KQ"),  # 프로티나
    "3":  ("큐리오시스코드", "큐리오시스.KQ"),  # 큐리오시스 ← 코드 확인 필요
    "4":  ("큐리옥스코드",  "큐리옥스.KQ"),   # 큐리옥스바이오 ← 코드 확인 필요
    "5":  ("엘앤씨코드",   "엘앤씨.KQ"),    # 엘앤씨바이오 ← 코드 확인 필요

    # ── 방산·전지 ──────────────────────────────────────────
    "6":  ("032680", "032680.KQ"),  # 비츠로셀
    "7":  ("009450", "009450.KS"),  # 한화시스템
    "8":  ("010820", "010820.KS"),  # 퍼스텍
    "9":  ("214430", "214430.KQ"),  # 아이쓰리시스템
    "10": ("056190", "056190.KQ"),  # 휴니드
    "11": ("064350", "064350.KS"),  # 현대로템

    # ── 원전·SMR ───────────────────────────────────────────
    "12": ("034020", "034020.KS"),  # 두산에너빌리티

    # ── 에너지인프라 ────────────────────────────────────────
    "13": ("003030", "003030.KS"),  # 세아제강지주

    # ── 수술로봇 ───────────────────────────────────────────
    "14": ("리브스메드코드", "리브스메드.KQ"),  # 리브스메드 ← 코드 확인 필요

    # ── 로봇·AI ────────────────────────────────────────────
    "15": ("클로봇코드",       "클로봇.KQ"),        # 클로봇
    "16": ("277810", "277810.KQ"),  # 레인보우로보틱스
    "17": ("454910", "454910.KQ"),  # 두산로보틱스
    "18": ("뉴로메카코드",     "뉴로메카.KQ"),      # 뉴로메카
    "19": ("108490", "108490.KQ"),  # 로보티즈

    # ── IT·플랫폼 ──────────────────────────────────────────
    "20": ("아이티센코드", "아이티센.KQ"),  # 아이티센글로벌

    # ── 항공·물류 ──────────────────────────────────────────
    "21": ("003490", "003490.KS"),  # 대한항공

    # ── 반도체 ────────────────────────────────────────────
    "22": ("005930", "005930.KS"),  # 삼성전자
    "23": ("000660", "000660.KS"),  # SK하이닉스

    # ── 조선·기자재 ────────────────────────────────────────
    "24": ("동일스틸렉스코드", "동일스틸렉스.KS"),
    "25": ("329180", "329180.KS"),  # HD현대중공업
    "26": ("097230", "097230.KS"),  # HJ중공업
    "27": ("케이프코드",      "케이프.KQ"),
    "28": ("한화엔진코드",    "한화엔진.KS"),

    # ── 신재생에너지 ───────────────────────────────────────
    "29": ("112610", "112610.KQ"),  # 씨에스윈드
    "30": ("010060", "010060.KS"),  # OCI
    "31": ("HD현대에너지코드", "HD현대에너지.KQ"),
    "32": ("009830", "009830.KS"),  # 한화솔루션

    # ── 알루미늄·소재 ──────────────────────────────────────
    "33": ("삼아알미늄코드", "삼아알미늄.KS"),
    "34": ("DI동일코드",    "DI동일.KS"),
    "35": ("조일알루미늄코드","조일알루미늄.KS"),

    # ── 2차전지 ────────────────────────────────────────────
    "36": ("006400", "006400.KS"),  # 삼성SDI
    "37": ("DS단석코드",   "DS단석.KQ"),

    # ── 전력설비 ───────────────────────────────────────────
    "38": ("000800", "000800.KS"),  # 가온전선
    "39": ("006260", "006260.KS"),  # LS
    "40": ("010120", "010120.KS"),  # LS ELECTRIC

    # ── PCB·반도체소재 ─────────────────────────────────────
    "41": ("KEC코드",      "KEC.KS"),
    "42": ("이수페타시스코드","이수페타시스.KQ"),
    "43": ("011070", "011070.KS"),  # LG이노텍
    "44": ("두산테스나코드", "두산테스나.KQ"),
    "45": ("동진쎄미켐코드", "동진쎄미켐.KQ"),

    # ── 우주항공 ───────────────────────────────────────────
    "46": ("미래에셋벤처코드", "미래에셋벤처.KQ"),
    "47": ("스피어코드",      "스피어.KQ"),
    "48": ("에이치브이엠코드", "에이치브이엠.KQ"),
    "49": ("012450", "012450.KS"),  # 한화에어로스페이스
    "50": ("047810", "047810.KS"),  # 한국항공우주
    "51": ("079550", "079550.KS"),  # LIG넥스원

    # ── 소비·유통 ──────────────────────────────────────────
    "52": ("008770", "008770.KS"),  # 호텔신라
    "53": ("139480", "139480.KS"),  # 이마트
    "54": ("004370", "004370.KS"),  # 농심
    "55": ("090430", "090430.KS"),  # 아모레퍼시픽
    "56": ("롯데하이마트코드", "롯데하이마트.KS"),

    # ── 로봇 세부 섹터 (중복 종목 제외, 주요 종목만) ─────────
    # robot_part, robot_reductor, robot_sw, robot_cobot, robot_service,
    # robot_hand, robot_eye, robot_medical, robot_light 섹터들
    # 이미 위 ID로 등록된 종목들은 동일 ID 재사용
    # 아래는 위에 없는 추가 종목들
    "57": ("에스피지코드",     "에스피지.KQ"),
    "58": ("에스비비테크코드",  "에스비비테크.KQ"),
    "59": ("현대오토에버코드",  "현대오토에버.KS"),
    "60": ("씨메스코드",       "씨메스.KQ"),
    "61": ("휴림로봇코드",     "휴림로봇.KQ"),
    "62": ("유일로보틱스코드",  "유일로보틱스.KQ"),
    "63": ("현대무벡스코드",   "현대무벡스.KQ"),
    "64": ("티로보틱스코드",   "티로보틱스.KQ"),
    "65": ("유진로봇코드",     "유진로봇.KQ"),
    "66": ("티엑스알코드",     "티엑스알로보틱스.KQ"),
    "67": ("원익홀딩스코드",   "원익홀딩스.KQ"),
    "68": ("에스오에스랩코드", "에스오에스랩.KQ"),
    "69": ("고영코드",        "고영.KQ"),
    "70": ("큐렉소코드",      "큐렉소.KQ"),
    "71": ("미래컴퍼니코드",  "미래컴퍼니.KQ"),
    "72": ("엔젤로보틱스코드","엔젤로보틱스.KQ"),
    "73": ("한라캐스트코드",  "한라캐스트.KS"),
    "74": ("링크솔루션코드",  "링크솔루션.KQ"),
    "75": ("하이젠알앤엠코드","하이젠알앤엠.KQ"),
    "76": ("HL만도코드",     "HL만도.KS"),
    "77": ("현대모비스코드",  "현대모비스.KS"),
    "78": ("우림피티에스코드","우림피티에스.KQ"),
    "79": ("디아이씨코드",   "디아이씨.KQ"),
    "80": ("이랜시스코드",   "이랜시스.KQ"),
    "81": ("한국피아이엠코드","한국피아이엠.KQ"),
    "82": ("삼현코드",       "삼현.KQ"),
    "83": ("제이에스링크코드","제이에스링크.KQ"),  # 테마·투기
    "84": ("한화엔진코드2",  "한화엔진코드2.KS"),  # 중복 방지용 placeholder
}

# ══════════════════════════════════════════════════════════
#  히스토리 수집 (최대 1.2년 = 약 300 거래일)
# ══════════════════════════════════════════════════════════
HISTORY_PERIOD = "15mo"   # yfinance period 파라미터 (15개월 → 약 300 거래일 확보)
MAX_CLOSES     = 300       # 저장할 최대 종가 수

def fetch_stock(stock_id: str, code: str, ticker: str) -> dict | None:
    """단일 종목 데이터 수집"""
    # 코드가 한글이거나 placeholder인 경우 스킵
    if any(c > "\u007F" for c in ticker) or "코드" in ticker:
        print(f"  [SKIP] ID={stock_id} ticker={ticker} (코드 미입력)")
        return None

    try:
        tk   = yf.Ticker(ticker)
        hist = tk.history(period=HISTORY_PERIOD, interval="1d", auto_adjust=True)

        if hist.empty or len(hist) < 5:
            print(f"  [WARN] ID={stock_id} {ticker}: 데이터 없음")
            return None

        closes  = [round(float(p)) for p in hist["Close"].tolist()]
        volumes = [int(v) for v in hist["Volume"].tolist()]
        dates   = [str(d.date()) for d in hist.index.tolist()]

        # 최근 MAX_CLOSES 개로 자름
        closes  = closes[-MAX_CLOSES:]
        volumes = volumes[-MAX_CLOSES:]
        dates   = dates[-MAX_CLOSES:]

        last  = closes[-1]
        prev  = closes[-2] if len(closes) >= 2 else last
        chg   = last - prev
        pct   = round(chg / prev * 100, 2) if prev else 0.0
        h52   = max(closes[-250:]) if len(closes) >= 250 else max(closes)
        l52   = min(closes[-250:]) if len(closes) >= 250 else min(closes)

        print(f"  [OK]   ID={stock_id} {ticker}: {len(closes)}일, 현재가={last:,}")
        return {
            "code":      code,
            "closes":    closes,
            "volumes":   volumes,
            "dates":     dates,
            "current":   last,
            "prev":      prev,
            "chgAmt":    chg,
            "chgPct":    pct,
            "h52":       h52,
            "l52":       l52,
            "updatedAt": datetime.now(KST).strftime("%Y.%m.%d %H:%M"),
        }

    except Exception as e:
        print(f"  [ERR]  ID={stock_id} {ticker}: {e}")
        return None


def main():
    print(f"=== update_prices.py 시작 ({NOW_KST} KST) ===\n")

    price_data = {}
    success, skip, fail = 0, 0, 0

    for stock_id, (code, ticker) in STOCK_MAP.items():
        result = fetch_stock(stock_id, code, ticker)
        if result is None:
            if "코드" in ticker or any(c > "\u007F" for c in ticker):
                skip += 1
            else:
                fail += 1
        else:
            price_data[stock_id] = result
            success += 1

    print(f"\n처리 완료: 성공={success}, 스킵={skip}, 실패={fail}")

    # ── JS 파일 출력 ──────────────────────────────────────
    lines = [
        "// AUTO-GENERATED — DO NOT EDIT MANUALLY",
        f"// Updated: {NOW_KST} KST",
        "// Source: Yahoo Finance via yfinance",
        "// chart_module.js 에서 PRICE_DATA[stockId].code 로 TradingView 링크 생성",
        "",
        "const PRICE_DATA = {",
    ]

    items = list(price_data.items())
    for i, (sid, d) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        closes_str  = json.dumps(d["closes"],  ensure_ascii=False)
        volumes_str = json.dumps(d["volumes"], ensure_ascii=False)
        dates_str   = json.dumps(d["dates"],   ensure_ascii=False)
        lines += [
            f'  "{sid}": {{',
            f'    "code":      "{d["code"]}",',
            f'    "closes":    {closes_str},',
            f'    "volumes":   {volumes_str},',
            f'    "dates":     {dates_str},',
            f'    "current":   {d["current"]},',
            f'    "prev":      {d["prev"]},',
            f'    "chgAmt":    {d["chgAmt"]},',
            f'    "chgPct":    {d["chgPct"]},',
            f'    "h52":       {d["h52"]},',
            f'    "l52":       {d["l52"]},',
            f'    "updatedAt": "{d["updatedAt"]}"',
            f'  }}{comma}',
        ]

    lines.append("};")

    out_path = "stocks_data.js"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n✅ {out_path} 생성 완료 ({success}개 종목)")


if __name__ == "__main__":
    main()
