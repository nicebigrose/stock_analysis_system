"""
Module scan tin hieu ky thuat nhanh
Copy vao: src/screener/technical_scanner.py
"""
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.data_pipeline.price_data import PriceDataCrawler
from src.analysis.technical import TechnicalAnalyzer
from config.settings import WATCHLIST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalScanner:
    """Scan tin hieu ky thuat nhanh cho nhieu ma"""
    
    def __init__(self, watchlist=None):
        self.watchlist = watchlist or WATCHLIST
        self.price_crawler = PriceDataCrawler()
        self.technical_analyzer = TechnicalAnalyzer()
    
    def scan_single_stock(self, symbol: str):
        """Scan mot ma co phieu"""
        try:
            # Lay du lieu
            df = self.price_crawler.get_historical_data(symbol)
            
            if df.empty:
                return None
            
            # Phan tich
            result = self.technical_analyzer.analyze_stock(df, symbol)
            
            # Tom tat quan trong
            summary = {
                'symbol': symbol,
                'close': result['close'],
                'signal': result['signals']['signal'],
                'signal_score': result['signals']['score'],
                'rsi': result['rsi'],
                'macd': result['macd'],
                'trend': result['trend']['medium_term'],
                'patterns': result['patterns'],
                'support': result['support_resistance']['supports'][-1] if result['support_resistance']['supports'] else None,
                'resistance': result['support_resistance']['resistances'][-1] if result['support_resistance']['resistances'] else None
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {str(e)}")
            return None
    
    def scan_all(self, max_workers=5):
        """Scan tat ca ma trong watchlist"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.scan_single_stock, symbol): symbol
                for symbol in self.watchlist
            }
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        if results:
            df = pd.DataFrame(results)
            df = df.sort_values('signal_score', ascending=False)
            return df
        
        return pd.DataFrame()
    
    def find_buy_signals(self):
        """Tim cac ma co tin hieu mua"""
        df = self.scan_all()
        
        if df.empty:
            return pd.DataFrame()
        
        # Loc tin hieu BUY
        buy_signals = df[df['signal'].isin(['BUY', 'STRONG BUY'])]
        
        return buy_signals
    
    def find_oversold(self, rsi_threshold=30):
        """Tim cac ma oversold (RSI thap)"""
        df = self.scan_all()
        
        if df.empty:
            return pd.DataFrame()
        
        oversold = df[df['rsi'] < rsi_threshold]
        return oversold.sort_values('rsi')
    
    def find_overbought(self, rsi_threshold=70):
        """Tim cac ma overbought (RSI cao)"""
        df = self.scan_all()
        
        if df.empty:
            return pd.DataFrame()
        
        overbought = df[df['rsi'] > rsi_threshold]
        return overbought.sort_values('rsi', ascending=False)
    
    def find_near_support(self, threshold=0.02):
        """Tim cac ma gan vung ho tro"""
        df = self.scan_all()
        
        if df.empty:
            return pd.DataFrame()
        
        near_support = []
        
        for _, row in df.iterrows():
            if row['support'] and row['close']:
                distance = abs(row['close'] - row['support']) / row['close']
                if distance < threshold:
                    near_support.append(row)
        
        if near_support:
            return pd.DataFrame(near_support)
        
        return pd.DataFrame()
    
    def find_breakout(self):
        """Tim cac ma breakout khoi resistance"""
        df = self.scan_all()
        
        if df.empty:
            return pd.DataFrame()
        
        breakouts = []
        
        for _, row in df.iterrows():
            if row['resistance'] and row['close'] > row['resistance']:
                breakouts.append(row)
        
        if breakouts:
            return pd.DataFrame(breakouts)
        
        return pd.DataFrame()


# Example usage
if __name__ == "__main__":
    scanner = TechnicalScanner(watchlist=['VNM', 'VCB', 'HPG', 'FPT', 'MWG'])
    
    print("=== TECHNICAL SCANNER ===\n")
    
    # Scan tat ca
    print("1. Scanning all stocks...")
    all_results = scanner.scan_all()
    if not all_results.empty:
        print(all_results[['symbol', 'signal', 'rsi', 'trend']].to_string(index=False))
    
    # Tim buy signals
    print("\n2. Stocks with BUY signals:")
    buy_signals = scanner.find_buy_signals()
    if not buy_signals.empty:
        for _, row in buy_signals.iterrows():
            print(f"  [BUY] {row['symbol']}: {row['signal']} (RSI: {row['rsi']:.1f})")
    else:
        print("  No BUY signals found")
    
    # Tim oversold
    print("\n3. Oversold stocks (RSI < 30):")
    oversold = scanner.find_oversold()
    if not oversold.empty:
        for _, row in oversold.iterrows():
            print(f"  [OVERSOLD] {row['symbol']}: RSI {row['rsi']:.1f}")
    else:
        print("  No oversold stocks")