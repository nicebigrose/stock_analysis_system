"""
Main entry point cho Stock Analysis System
"""
import argparse
import logging
from datetime import datetime

from src.data_pipeline.price_data import PriceDataCrawler
from src.data_pipeline.fundamental_data import FundamentalDataCrawler
from src.screener.fundamental_screener import StockScreener
from src.portfolio.portfolio_manager import PortfolioManager
from config.settings import WATCHLIST, LOG_FILE

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_screener(symbols=None, save_results=True):
    """Chạy screener"""
    print("\n" + "="*80)
    print("RUNNING STOCK SCREENER")
    print("="*80)
    
    screener = StockScreener(watchlist=symbols or WATCHLIST)
    results = screener.screen_multiple_stocks(max_workers=5)
    
    if not results.empty:
        print("\n📊 SCREENING RESULTS:\n")
        print(results.to_string(index=False))
        
        # Top picks
        print("\n\n⭐ TOP PICKS (BUY trở lên):\n")
        top = results[results['Rating'].isin(['STRONG BUY', 'BUY'])]
        
        if not top.empty:
            for _, row in top.iterrows():
                print(f"\n✓ {row['Symbol']}: {row['Rating']}")
                print(f"   Score: {row['Score']:.2f}/5.0")
                print(f"   Fundamental: {row['F_Rating']} ({row['F_Score']:.0f}%)")
                print(f"   Technical: {row['T_Signal']} (Score: {row['T_Score']})")
                print(f"   Note: {row['Note']}")
        else:
            print("Không có mã nào đạt tiêu chí BUY")
        
        # Save to file
        if save_results:
            filename = f"screening_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            results.to_csv(filename, index=False)
            print(f"\n💾 Results saved to: {filename}")
    else:
        print("❌ No results found")


def update_data(symbols=None):
    """Cập nhật dữ liệu mới nhất"""
    print("\n" + "="*80)
    print("UPDATING DATA")
    print("="*80)
    
    symbols = symbols or WATCHLIST
    crawler = PriceDataCrawler()
    
    for symbol in symbols:
        print(f"Updating {symbol}...")
        df = crawler.update_data(symbol)
        if not df.empty:
            print(f"✓ {symbol}: {len(df)} new records")
        else:
            print(f"✗ {symbol}: No new data")


def show_portfolio():
    """Hiển thị portfolio"""
    print("\n" + "="*80)
    print("PORTFOLIO SUMMARY")
    print("="*80)
    
    pm = PortfolioManager()
    pm.print_summary()


def analyze_stock(symbol):
    """Phân tích chi tiết 1 mã"""
    print("\n" + "="*80)
    print(f"ANALYZING {symbol}")
    print("="*80)
    
    from src.analysis.technical import TechnicalAnalyzer
    from src.analysis.fundamental import FundamentalAnalyzer
    
    # Price data
    price_crawler = PriceDataCrawler()
    df = price_crawler.get_historical_data(symbol)
    
    if df.empty:
        print(f"❌ No price data for {symbol}")
        return
    
    # Technical analysis
    tech_analyzer = TechnicalAnalyzer()
    tech_result = tech_analyzer.analyze_stock(df, symbol)
    
    print("\n📊 TECHNICAL ANALYSIS:")
    print(f"Close: {tech_result['close']:,.0f}")
    print(f"RSI: {tech_result['rsi']:.1f}")
    print(f"Trend: {tech_result['trend']}")
    print(f"Signal: {tech_result['signals']['signal']} (Score: {tech_result['signals']['score']})")
    print("\nReasons:")
    for reason in tech_result['signals']['reasons']:
        print(f"  • {reason}")
    
    if tech_result['patterns']:
        print("\nPatterns:")
        for pattern in tech_result['patterns']:
            print(f"  • {pattern}")
    
    # Fundamental analysis
    fund_crawler = FundamentalDataCrawler()
    ratios = fund_crawler.get_financial_ratios(symbol)
    
    if ratios:
        fund_analyzer = FundamentalAnalyzer()
        fund_result = fund_analyzer.analyze_stock(ratios)
        
        print("\n💼 FUNDAMENTAL ANALYSIS:")
        print(f"Rating: {fund_result['scoring']['rating']} ({fund_result['scoring']['percentage']:.1f}%)")
        print(f"Recommendation: {fund_result['recommendation']['action']}")
        print(f"Note: {fund_result['recommendation']['note']}")
        print("\nKey Ratios:")
        print(f"  ROE: {ratios.get('roe', 0):.1f}%")
        print(f"  P/E: {ratios.get('pe', 0):.1f}x")
        print(f"  P/B: {ratios.get('pb', 0):.2f}x")
        print(f"  D/E: {ratios.get('debt_to_equity', 0):.2f}x")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Vietnam Stock Analysis System')
    
    parser.add_argument('command', choices=['screen', 'update', 'portfolio', 'analyze', 'dashboard'],
                       help='Command to execute')
    parser.add_argument('-s', '--symbols', nargs='+', help='Stock symbols')
    parser.add_argument('--symbol', help='Single stock symbol for analysis')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'screen':
            run_screener(symbols=args.symbols)
        
        elif args.command == 'update':
            update_data(symbols=args.symbols)
        
        elif args.command == 'portfolio':
            show_portfolio()
        
        elif args.command == 'analyze':
            if not args.symbol:
                print("❌ Please specify --symbol")
                return
            analyze_stock(args.symbol.upper())
        
        elif args.command == 'dashboard':
            print("\n🚀 Starting Streamlit Dashboard...")
            print("Run: streamlit run src/dashboard/app.py")
            import subprocess
            subprocess.run(['streamlit', 'run', 'src/dashboard/app.py'])
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()