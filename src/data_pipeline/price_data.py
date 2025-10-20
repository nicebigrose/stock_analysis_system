"""
Module lay du lieu gia tu vnstock - FIXED
THAY THE FILE price_data.py HIEN TAI
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

try:
    from vnstock import Vnstock
except ImportError:
    print("Chua cai vnstock. Cai dat: pip install vnstock --upgrade")
    
from config.settings import RAW_DATA_DIR, CACHE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceDataCrawler:
    """Lay va quan ly du lieu gia co phieu"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        
    def get_historical_data(self, symbol: str, start_date: str = None, 
                           end_date: str = None, use_cache: bool = True):
        """
        Lay du lieu lich su
        
        Args:
            symbol: Ma co phieu (VD: 'VNM', 'VCB')
            start_date: Ngay bat dau (YYYY-MM-DD)
            end_date: Ngay ket thuc (YYYY-MM-DD)
            use_cache: Su dung cache hay khong
            
        Returns:
            DataFrame voi cac cot: date, open, high, low, close, volume
        """
        # Thiet lap ngay mac dinh
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
            
        cache_file = self.cache_dir / f"{symbol}_{start_date}_{end_date}.parquet"
        
        # Kiem tra cache
        if use_cache and cache_file.exists():
            logger.info(f"Loading {symbol} from cache")
            return pd.read_parquet(cache_file)
        
        try:
            logger.info(f"Fetching {symbol} from {start_date} to {end_date}")
            
            # Khoi tao stock cho moi lan goi
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            
            # Lay du lieu lich su
            df = stock.quote.history(start=start_date, end=end_date)
            
            if df is not None and not df.empty:
                # Chuan hoa ten cot - API moi co ten khac
                column_mapping = {
                    'time': 'date',
                    'open': 'open',
                    'high': 'high', 
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume',
                    # Cac ten co the khac
                    'Time': 'date',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                }
                
                # Rename columns neu co
                for old_name, new_name in column_mapping.items():
                    if old_name in df.columns and old_name != new_name:
                        df = df.rename(columns={old_name: new_name})
                
                # Dam bao co cac cot can thiet
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in required_cols):
                    logger.error(f"Missing required columns. Available: {df.columns.tolist()}")
                    return pd.DataFrame()
                
                # Dam bao index la datetime
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                elif 'time' in df.columns:
                    df['time'] = pd.to_datetime(df['time'])
                    df = df.set_index('time')
                    df.index.name = 'date'
                
                # Sort theo ngay
                df = df.sort_index()
                
                # Chi lay cac cot can thiet
                df = df[required_cols]
                
                # Luu cache
                df.to_parquet(cache_file)
                logger.info(f"Successfully fetched {len(df)} records for {symbol}")
                
                return df
            else:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_latest_price(self, symbol: str):
        """Lay gia realtime/latest"""
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            
            # Lay du lieu 5 ngay gan nhat
            df = stock.quote.history(
                start=(datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                end=datetime.now().strftime('%Y-%m-%d')
            )
            
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                
                return {
                    'symbol': symbol,
                    'date': latest.get('time', latest.get('Time', datetime.now())),
                    'close': latest.get('close', latest.get('Close', 0)),
                    'volume': latest.get('volume', latest.get('Volume', 0)),
                    'change': latest.get('change', 0),
                    'change_percent': latest.get('changePc', latest.get('pctChange', 0))
                }
        except Exception as e:
            logger.error(f"Error getting latest price for {symbol}: {str(e)}")
            return None
    
    def get_multiple_stocks(self, symbols: list, start_date: str = None, 
                           end_date: str = None):
        """Lay du lieu nhieu ma co phieu"""
        results = {}
        
        for symbol in symbols:
            logger.info(f"Processing {symbol}...")
            df = self.get_historical_data(symbol, start_date, end_date)
            if not df.empty:
                results[symbol] = df
                
        logger.info(f"Successfully fetched {len(results)}/{len(symbols)} stocks")
        return results
    
    def update_data(self, symbol: str, last_date: str = None):
        """Cap nhat du lieu moi nhat (tu last_date den hom nay)"""
        if last_date is None:
            last_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        return self.get_historical_data(
            symbol, 
            start_date=last_date, 
            end_date=end_date,
            use_cache=False  # Khong dung cache khi update
        )


# Example usage
if __name__ == "__main__":
    crawler = PriceDataCrawler()
    
    # Test voi 1 ma
    print("Testing with VNM...")
    df = crawler.get_historical_data('VNM', start_date='2024-01-01')
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Test latest price
    print("\nLatest price:")
    latest = crawler.get_latest_price('VNM')
    print(latest)