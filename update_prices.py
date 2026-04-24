import json
import datetime
import yfinance as yf

# ── 42개 전체 종목 ──────────────────────────────────────────
# KOSPI = 종목코드.KS / KOSDAQ = 종목코드.KQ
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
    13: {"ticker": "003490.KS", "name": "대한항공"},
    14: {"ticker": "005930.KS", "name": "삼성전자"},
    15: {"ticker": "000660.KS", "name": "SK하이닉스"},
    16: {"ticker": "023790.KQ", "name": "동일스틸렉스"},
    17: {"ticker": "329180.KS", "name": "HD현대중공업"},
    18: {"ticker": "097230.KS", "name": "HJ중공업"},
    19: {"ticker": "064820.KQ", "name": "케이프"},
    20: {"ticker": "082740.KQ", "name": "한화엔진"},
    21: {"ticker": "112610.KS", "name": "씨에스윈드"},
    22: {"ticker": "010060.KS", "name": "OCI"},
    23: {"ticker": "322000.KS", "name": "HD현대에너지솔루션"},
    24: {"ticker": "009830.KS", "name": "한화솔루션"},
    25: {"ticker": "006110.KS", "name": "삼아알미늄"},
    26: {"ticker": "001530.KS", "name": "DI동일"},
    27: {"ticker": "038160.KQ", "name": "조일알루미늄"},
    28: {"ticker": "006400.KS", "name": "삼성SDI"},
    29: {"ticker": "017860.KS", "name": "DS단석"},
    30: {"ticker": "065150.KQ", "name": "퍼스텍"},
    31: {"ticker": "214430.KQ", "name": "아이쓰리시스템"},
    32: {"ticker": "024720.KS", "name": "휴니드"},
    33: {"ticker": "064350.KS", "name": "현대로템"},
    34: {"ticker": "000240.KS", "name": "가온전선"},
    35: {"ticker": "006260.KS", "name": "LS"},
    36: {"ticker": "010120.KS", "name": "LS ELECTRIC"},
    37: {"ticker": "092220.KQ", "name": "KEC"},
    38: {"ticker": "007660.KS", "name": "이수페타시스"},
    39: {"ticker": "011070.KS", "name": "LG이노텍"},
    40: {"ticker": "131970.KQ", "name": "두산테스나"},
    41: {"ticker": "005290.KS", "name": "동진쎄미켐"},
    42: {"ticker": "002220.KS", "name": "미래에셋벤처투자"},
    43: {"ticker": "237690.KQ", "name": "에스티팜"},
    44: {"ticker": "010140.KS", "name": "삼성중공업"},
    45: {"ticker": "298040.KS", "name": "효성중공업"},
    46: {"ticker": "008770.KS", "name": "호텔신라"},
    47: {"ticker": "347700.KQ", "name": "스피어"},
    48: {"ticker": "295310.KQ", "name": "에이치브이엠"},
    49: {"ticker": "274090.KQ", "name": "켄코아에어로스페이스"},
    50: {"ticker": "001430.KS", "name": "세아베스틸지주"},
    51: {"ticker": "354320.KQ", "name": "알멕"},
    52: {"ticker": "012450.KS", "name": "한화에어로스페이스"},
    53: {"ticker": "462350.KQ", "name": "이노스페이스"},
    54: {"ticker": "488900.KQ", "name": "비츠로넥스텍"},
    55: {"ticker": "063170.KQ", "name": "쎄트렉아이"},
    56: {"ticker": "478340.KQ", "name": "나라스페이스테크놀로지"},
    57: {"ticker": "047810.KS", "name": "한국항공우주"},
    58: {"ticker": "079550.KS", "name": "LIG넥스원"},
    59: {"ticker": "211270.KQ", "name": "AP위성"},
    60: {"ticker": "474170.KQ", "name": "루미르"},
    61: {"ticker": "189300.KQ", "name": "인텔리안테크"},
    62: {"ticker": "451760.KQ", "name": "컨텍"},
    63: {"ticker": "361390.KQ", "name": "제노코"},
    64: {"ticker": "108490.KQ", "name": "로보티즈"},
    65: {"ticker": "012330.KS", "name": "현대모비스"},
    66: {"ticker": "204320.KS", "name": "HL만도"},
    67: {"ticker": "160190.KQ", "name": "하이젠알앤엠"},
    68: {"ticker": "406570.KQ", "name": "삼현"},
    69: {"ticker": "348340.KQ", "name": "뉴로메카"},
    70: {"ticker": "058610.KQ", "name": "에스피지"},
    71: {"ticker": "389500.KQ", "name": "에스비비테크"},
    72: {"ticker": "101170.KQ", "name": "우림피티에스"},
    73: {"ticker": "092200.KQ", "name": "디아이씨"},
    74: {"ticker": "264850.KQ", "name": "이랜시스"},
    75: {"ticker": "475160.KQ", "name": "한국피아이엠"},
    76: {"ticker": "212300.KS", "name": "현대오토에버"},
    77: {"ticker": "475400.KQ", "name": "씨메스"},
    78: {"ticker": "277810.KQ", "name": "레인보우로보틱스"},
    79: {"ticker": "454910.KS", "name": "두산로보틱스"},
    80: {"ticker": "090710.KQ", "name": "휴림로봇"},
    81: {"ticker": "388720.KQ", "name": "유일로보틱스"},
    82: {"ticker": "042250.KQ", "name": "현대무벡스"},
    83: {"ticker": "117370.KQ", "name": "티로보틱스"},
    84: {"ticker": "056080.KQ", "name": "유진로봇"},
    85: {"ticker": "484810.KQ", "name": "티엑스알로보틱스"},
    86: {"ticker": "030530.KQ", "name": "원익홀딩스"},
    87: {"ticker": "464080.KQ", "name": "에스오에스랩"},
    88: {"ticker": "098460.KQ", "name": "고영"},
    89: {"ticker": "060280.KQ", "name": "큐렉소"},
    90: {"ticker": "060370.KQ", "name": "미래컴퍼니"},
    91: {"ticker": "467390.KQ", "name": "엔젤로보틱스"},
    92: {"ticker": "009300.KS", "name": "한라캐스트"},
    93: {"ticker": "257990.KQ", "name": "링크솔루션"},
    94: {"ticker": "139480.KS", "name": "이마트"},
    95: {"ticker": "004370.KS", "name": "농심"},
    96: {"ticker": "090430.KS", "name": "아모레퍼시픽"},
    97: {"ticker": "071840.KS", "name": "롯데하이마트"},
    98: {"ticker": "237630.KQ", "name": "엘앤씨바이오"},
}

def fetch_price_data(ticker, period="1y"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None
        closes = [round(float(v), 0) for v in hist["Close"].tolist()]
        current = closes[-1] if closes else None
        prev = closes[-2] if len(closes) > 1 else current
        change_pct = round((current - prev) / prev * 100, 2) if prev else 0
        return {
            "closes": closes,
            "current": current,
            "change_pct": change_pct,
            "updated": datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
        }
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None

def main():
    print(f"=== 주가 업데이트 시작: {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')} ===")
    result = {}
    for sid, info in STOCKS.items():
        print(f"  [{sid:2d}] {info['name']} ({info['ticker']}) ...", end=" ")
        data = fetch_price_data(info["ticker"])
        if data:
            result[str(sid)] = data
            print(f"✓ 현재가: {data['current']:,.0f}원 ({data['change_pct']:+.2f}%)")
        else:
            print("skip")

    js_content = f"""// 자동 생성 파일 - 수동 수정 금지
// 업데이트: {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')} KST
// 총 {len(result)}개 종목

const PRICE_DATA = {json.dumps(result, ensure_ascii=False, indent=2)};
"""
    with open("stocks_data.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"\n=== 완료: {len(result)}/{len(STOCKS)}개 종목 업데이트 ===")
    print("stocks_data.js 저장 완료")

if __name__ == "__main__":
    main()
