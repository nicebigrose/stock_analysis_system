"""
COMPLETE - Fix lay data moi nhat
THAY THE fundamental_data.py
"""
import pandas as pd
import logging
from datetime import datetime

try:
    from vnstock import Vnstock
except ImportError:
    print("Chua cai vnstock")

from config.settings import RAW_DATA_DIR, CACHE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundamentalDataCrawler:
    """Lay du lieu tai chinh co ban"""
    
    def __init__(self):
        pass
        
    def get_financial_ratios(self, symbol: str):
        """Lay cac chi so tai chinh quan trong"""
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            ratios = stock.finance.ratio(lang='vi', dropna=True)
            
            if ratios is not None and not ratios.empty:
                # SORT theo nam va quy de lay du lieu MOI NHAT
                if ('Meta', 'Năm') in ratios.columns and ('Meta', 'Kỳ') in ratios.columns:
                    ratios = ratios.sort_values([('Meta', 'Năm'), ('Meta', 'Kỳ')], ascending=False)
                
                # Lay dong dau tien (moi nhat sau khi sort)
                latest = ratios.iloc[0]
                
                # Kiem tra nam hop ly
                year = latest.get(('Meta', 'Năm'), 0)
                quarter = latest.get(('Meta', 'Kỳ'), 0)
                current_year = datetime.now().year
                
                if year < current_year - 3:
                    logger.warning(f"{symbol}: Old data (year {year}Q{quarter}), may not be accurate")
                
                # Parse du lieu
                result = {
                    'symbol': symbol,
                    
                    # Valuation
                    'pe': latest.get(('Chỉ tiêu định giá', 'P/E'), None),
                    'pb': latest.get(('Chỉ tiêu định giá', 'P/B'), None),
                    'ps': latest.get(('Chỉ tiêu định giá', 'P/S'), None),
                    'eps': latest.get(('Chỉ tiêu định giá', 'EPS (VND)'), None),
                    'bvps': latest.get(('Chỉ tiêu định giá', 'BVPS (VND)'), None),
                    'evebitda': latest.get(('Chỉ tiêu định giá', 'EV/EBITDA'), None),
                    
                    # Profitability
                    'roe': latest.get(('Chỉ tiêu khả năng sinh lợi', 'ROE (%)'), None),
                    'roa': latest.get(('Chỉ tiêu khả năng sinh lợi', 'ROA (%)'), None),
                    'roic': latest.get(('Chỉ tiêu khả năng sinh lợi', 'ROIC (%)'), None),
                    'gross_margin': latest.get(('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận gộp (%)'), None),
                    'net_margin': latest.get(('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận ròng (%)'), None),
                    'ebit_margin': latest.get(('Chỉ tiêu khả năng sinh lợi', 'Biên EBIT (%)'), None),
                    
                    # Leverage
                    'debt_to_equity': latest.get(('Chỉ tiêu cơ cấu nguồn vốn', 'Nợ/VCSH'), None),
                    
                    # Liquidity
                    'current_ratio': latest.get(('Chỉ tiêu thanh khoản', 'Chỉ số thanh toán hiện thời'), None),
                    'quick_ratio': latest.get(('Chỉ tiêu thanh khoản', 'Chỉ số thanh toán nhanh'), None),
                    
                    # Meta
                    'year': year,
                    'quarter': quarter,
                    
                    'timestamp': datetime.now()
                }
                
                # Convert % sang decimal neu can
                if result['roe'] is not None and result['roe'] < 1:
                    result['roe'] = result['roe'] * 100
                if result['roa'] is not None and result['roa'] < 1:
                    result['roa'] = result['roa'] * 100
                if result['gross_margin'] is not None and result['gross_margin'] < 1:
                    result['gross_margin'] = result['gross_margin'] * 100
                if result['net_margin'] is not None and result['net_margin'] < 1:
                    result['net_margin'] = result['net_margin'] * 100
                
                logger.info(f"Got ratios for {symbol}: Year={year}Q{quarter}, ROE={result.get('roe')}, PE={result.get('pe')}")
                return result
            else:
                logger.warning(f"No financial ratios for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting ratios for {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_company_profile(self, symbol: str):
        """Lay thong tin doanh nghiep"""
        return {
            'symbol': symbol,
            'company_name': symbol,
            'industry': 'Unknown',
            'exchange': 'HOSE',
            'timestamp': datetime.now()
        }
    
    def get_complete_fundamentals(self, symbol: str):
        """Lay toan bo du lieu co ban"""
        logger.info(f"Fetching complete fundamentals for {symbol}")
        
        result = {
            'symbol': symbol,
            'ratios': self.get_financial_ratios(symbol),
            'profile': self.get_company_profile(symbol),
            'growth': None,
            'timestamp': datetime.now()
        }
        
        return result


# Test
if __name__ == "__main__":
    crawler = FundamentalDataCrawler()
    
    for sym in ['VNM', 'FPT', 'VCB']:
        print(f"\n{'='*60}")
        print(f"Testing {sym}...")
        d = crawler.get_financial_ratios(sym)
        if d:
            print(f"  Year: {d['year']}Q{d['quarter']}")
            print(f"  ROE: {d.get('roe')}%")
            print(f"  PE: {d.get('pe')}")
            print(f"  PB: {d.get('pb')}")