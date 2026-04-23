"""
update_prices.py
================
GitHub Actions에서 매일 실행 → stocks_data.js 자동 갱신
로컬 테스트: python update_prices.py

의존성: pip install yfinance pandas
"""

import yfinance as yf
import json
import os
from datetime import datetime, timedelta
import pandas as pd

# ─────────────────────────────────────────────────────────────
# 종목 정의 (추가 시 여기에만 추가)
# ─────────────────────────────────────────────────────────────
STOCKS = {
    1:  {"ticker": "082920.KQ", "name": "비츠로셀"},
    2:  {"ticker": "272210.KS", "name": "한화시스템"},
    3:  {"ticker": "034020.KS", "name": "두산에너빌리티"},
    4:  {"ticker": "003030.KS", "name": "세아제강지주"},
    5:  {"ticker": "475960.KQ", "name": "토모큐브"},
    6:  {"ticker": "468530.KQ", "name": "프로티나"},
    7:  {"ticker": "494120.KQ", "name": "큐리오시스"},
    8:  {"ticker": "445680.KQ", "name": "큐리옥스바이오"},
    9:  {"ticker": "491000.KQ", "name": "리브스메드"},
    10: {"ticker": "466100.KQ", "name": "클로봇"},
    11: {"ticker": "124500.KQ", "name": "아이티센글로벌"},
    12: {"ticker": "127120.KQ", "name": "제이에스링크"},
}

def fetch_stock_data(ticker: str, name: str) -> dict:
    """Yahoo Finance에서 12개월 일봉 데이터 수집"""
    try:
        tk = yf.Ticker(ticker)
        # 12개월 + 여유분 (공휴일 대비 270 거래일)
        df = tk.history(period="12mo", interval="1d", auto_adjust=True)

        if df.empty:
            print(f"  ⚠️  {name}: 데이터 없음")
            return None

        df = df.dropna(subset=["Close"])
        df.index = df.index.tz_localize(None) if df.index.tzinfo else df.index

        closes = [round(float(c), 0) for c in df["Close"].tolist()]
        volumes = [int(v) for v in df["Volume"].tolist()]
        dates   = [d.strftime("%Y-%m-%d") for d in df.index.tolist()]

        current  = closes[-1] if closes else 0
        prev_day = closes[-2] if len(closes) >= 2 else current
        chg_amt  = round(current - prev_day, 0)
        chg_pct  = round((chg_amt / prev_day * 100), 2) if prev_day else 0

        # 52주 고·저
        h52 = max(closes[-252:]) if len(closes) >= 252 else max(closes)
        l52 = min(closes[-252:]) if len(closes) >= 252 else min(closes)

        print(f"  ✓  {name}: {int(current):,}원  {chg_pct:+.2f}%  ({len(closes)}일치)")

        return {
            "closes":  closes,
            "volumes": volumes,
            "dates":   dates,
            "current": int(current),
            "prev":    int(prev_day),
            "chgAmt":  int(chg_amt),
            "chgPct":  chg_pct,
            "h52":     int(h52),
            "l52":     int(l52),
            "updatedAt": datetime.now().strftime("%Y.%m.%d %H:%M"),
        }

    except Exception as e:
        print(f"  ✗  {name}: 오류 - {e}")
        return None


def main():
    print(f"\n{'='*50}")
    print(f" 주가 데이터 업데이트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    result = {}
    failed = []

    for sid, info in STOCKS.items():
        data = fetch_stock_data(info["ticker"], info["name"])
        if data:
            result[str(sid)] = data
        else:
            failed.append(info["name"])

    # stocks_data.js 파일 생성
    output = f"""// AUTO-GENERATED — DO NOT EDIT MANUALLY
// Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")}
// Source: Yahoo Finance via yfinance

const PRICE_DATA = {json.dumps(result, ensure_ascii=False, indent=2)};
"""

    out_path = os.path.join(os.path.dirname(__file__), "stocks_data.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"\n{'='*50}")
    print(f" ✓ stocks_data.js 저장 완료 ({len(result)}종목)")
    if failed:
        print(f" ⚠ 실패: {', '.join(failed)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
