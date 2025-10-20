"""
Quick start script - Chay vi du nhanh
COPY FILE NAY DE THAY THE quickstart.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data_pipeline.price_data import PriceDataCrawler
from src.analysis.technical import TechnicalAnalyzer
from src.analysis.fundamental import FundamentalAnalyzer
from src.data_pipeline.fundamental_data import FundamentalDataCrawler


def quick_analysis(symbol='VNM'):
    """Phan tich nhanh 1 ma"""
    print(f"\n{'='*60}")
    print(f"QUICK ANALYSIS: {symbol}")
    print(f"{'='*60}\n")
    
    # 1. Get price data
    print("1. Fetching price data...")
    price_crawler = PriceDataCrawler()
    df = price_crawler.get_historical_data(symbol, start_date='2024-01-01')
    
    if df.empty:
        print(f"[ERROR] No data for {symbol}")
        return
    
    print(f"[OK] Got {len(df)} days of data\n")
    
    # 2. Technical analysis
    print("2. Running technical analysis...")
    tech = TechnicalAnalyzer()
    tech_result = tech.analyze_stock(df, symbol)
    
    print(f"   Close: {tech_result['close']:,.0f} VND")
    print(f"   RSI: {tech_result['rsi']:.1f}")
    print(f"   Signal: {tech_result['signals']['signal']}")
    print(f"   Trend: {tech_result['trend']['medium_term']}\n")
    
    # 3. Fundamental analysis
    print("3. Running fundamental analysis...")
    fund_crawler = FundamentalDataCrawler()
    ratios = fund_crawler.get_financial_ratios(symbol)
    
    if ratios:
        fund = FundamentalAnalyzer()
        fund_result = fund.analyze_stock(ratios)
        
        print(f"   Rating: {fund_result['scoring']['rating']}")
        print(f"   ROE: {ratios.get('roe', 0):.1f}%")
        print(f"   P/E: {ratios.get('pe', 0):.1f}x")
        print(f"   Recommendation: {fund_result['recommendation']['action']}\n")
    else:
        print("   [SKIP] No fundamental data available\n")
    
    print(f"{'='*60}\n")
    print(f"[TIP] For detailed analysis:")
    print(f"   python main.py analyze --symbol {symbol}")
    print(f"\n[TIP] Or start dashboard:")
    print(f"   streamlit run src/dashboard/app.py")


if __name__ == '__main__':
    # Get symbol from command line or use default
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'VNM'
    
    try:
        quick_analysis(symbol)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nMake sure you have installed requirements:")
        print("   pip install vnstock --upgrade")
        print("   pip install pandas numpy ta")