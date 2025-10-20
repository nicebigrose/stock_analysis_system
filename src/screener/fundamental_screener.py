"""
Module sàng lọc cổ phiếu theo tiêu chí cơ bản và kỹ thuật
"""
import pandas as pd
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.data_pipeline.price_data import PriceDataCrawler
from src.data_pipeline.fundamental_data import FundamentalDataCrawler
from src.analysis.fundamental import FundamentalAnalyzer
from src.analysis.technical import TechnicalAnalyzer
from config.settings import WATCHLIST, FUNDAMENTAL_CRITERIA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockScreener:
    """Sàng lọc cổ phiếu kết hợp cơ bản và kỹ thuật"""
    
    def __init__(self, watchlist=None):
        self.watchlist = watchlist or WATCHLIST
        self.price_crawler = PriceDataCrawler()
        self.fundamental_crawler = FundamentalDataCrawler()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
    
    def screen_single_stock(self, symbol: str):
        """
        Phan tich mot ma co phieu
        
        Returns:
            dict voi phan tich day du hoac None neu loi
        """
        logger.info(f"Screening {symbol}...")
        
        try:
            # 1. Lay du lieu co ban
            fundamental_data = self.fundamental_crawler.get_complete_fundamentals(symbol)
            
            if not fundamental_data.get('ratios'):
                logger.warning(f"No fundamental data for {symbol}")
                return None
            
            # 2. Phan tich co ban
            fundamental_analysis = self.fundamental_analyzer.analyze_stock(
                ratios=fundamental_data['ratios'],
                profile=fundamental_data.get('profile'),
                growth=fundamental_data.get('growth')  # Use .get() de tranh loi
            )
            
            # 3. Lay du lieu gia
            price_df = self.price_crawler.get_historical_data(
                symbol, 
                start_date=(datetime.now().replace(year=datetime.now().year - 1)).strftime('%Y-%m-%d')
            )
            
            if price_df.empty:
                logger.warning(f"No price data for {symbol}")
                return None
            
            # 4. Phan tich ky thuat
            technical_analysis = self.technical_analyzer.analyze_stock(price_df, symbol)
            
            # 5. Ket hop danh gia
            combined_score = self._combine_analysis(fundamental_analysis, technical_analysis)
            
            result = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'fundamental': fundamental_analysis,
                'technical': technical_analysis,
                'combined': combined_score
            }
            
            logger.info(f"[OK] {symbol}: F={fundamental_analysis['scoring']['rating']}, "
                    f"T={technical_analysis['signals']['signal']}, "
                    f"Combined={combined_score['final_rating']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error screening {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()  # In chi tiet loi de debug
            return None
    
    def screen_multiple_stocks(self, symbols=None, max_workers=5):
        """
        Sàng lọc nhiều mã cổ phiếu song song
        
        Args:
            symbols: Danh sách mã (nếu None, dùng watchlist)
            max_workers: Số luồng xử lý song song
            
        Returns:
            DataFrame với kết quả sàng lọc
        """
        symbols = symbols or self.watchlist
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tất cả tasks
            future_to_symbol = {
                executor.submit(self.screen_single_stock, symbol): symbol 
                for symbol in symbols
            }
            
            # Lấy kết quả
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Exception for {symbol}: {str(e)}")
        
        # Chuyển thành DataFrame
        if results:
            df = self._create_summary_dataframe(results)
            return df
        else:
            return pd.DataFrame()
    
    def _combine_analysis(self, fundamental, technical):
        """
        Kết hợp đánh giá cơ bản và kỹ thuật
        
        Trọng số: Fundamental 60%, Technical 40%
        """
        # Chuyển rating thành điểm
        f_rating_map = {
            'EXCELLENT': 5,
            'GOOD': 4,
            'AVERAGE': 3,
            'BELOW AVERAGE': 2,
            'POOR': 1
        }
        
        t_signal_map = {
            'STRONG BUY': 5,
            'BUY': 4,
            'HOLD': 3,
            'SELL': 2,
            'STRONG SELL': 1
        }
        
        f_score = f_rating_map.get(fundamental['scoring']['rating'], 3)
        t_score = t_signal_map.get(technical['signals']['signal'], 3)
        
        # Điểm tổng hợp (60-40)
        combined_score = (f_score * 0.6 + t_score * 0.4)
        
        # Quyết định cuối cùng
        if combined_score >= 4.5:
            final_rating = 'STRONG BUY'
            final_action = 'Mua mạnh - Cả cơ bản và kỹ thuật đều tốt'
        elif combined_score >= 3.8:
            final_rating = 'BUY'
            final_action = 'Mua - Tổng thể khá tích cực'
        elif combined_score >= 3.2:
            final_rating = 'HOLD'
            final_action = 'Giữ/Theo dõi - Chờ tín hiệu rõ ràng hơn'
        elif combined_score >= 2.5:
            final_rating = 'AVOID'
            final_action = 'Tránh - Chưa hấp dẫn'
        else:
            final_rating = 'SELL'
            final_action = 'Bán - Cả cơ bản và kỹ thuật đều yếu'
        
        # Phân tích điểm mạnh/yếu
        strengths = []
        weaknesses = []
        
        if f_score >= 4:
            strengths.append('Cơ bản tốt')
        elif f_score <= 2:
            weaknesses.append('Cơ bản yếu')
        
        if t_score >= 4:
            strengths.append('Kỹ thuật tích cực')
        elif t_score <= 2:
            weaknesses.append('Kỹ thuật tiêu cực')
        
        # Kiểm tra xung đột
        conflict = abs(f_score - t_score) >= 2
        if conflict:
            if f_score > t_score:
                note = '⚠️  Cơ bản tốt nhưng kỹ thuật chưa đẹp - Chờ điểm vào tốt hơn'
            else:
                note = '⚠️  Kỹ thuật tốt nhưng cơ bản yếu - Cẩn thận bẫy giá'
        else:
            note = '✓ Cơ bản và kỹ thuật đồng thuận'
        
        return {
            'fundamental_score': f_score,
            'technical_score': t_score,
            'combined_score': combined_score,
            'final_rating': final_rating,
            'final_action': final_action,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'has_conflict': conflict,
            'note': note
        }
    
    def _create_summary_dataframe(self, results):
        """Tạo DataFrame tóm tắt kết quả"""
        data = []
        
        for result in results:
            symbol = result['symbol']
            f = result['fundamental']
            t = result['technical']
            c = result['combined']
            
            row = {
                'Symbol': symbol,
                'Rating': c['final_rating'],
                'Score': round(c['combined_score'], 2),
                'F_Rating': f['scoring']['rating'],
                'F_Score': f['scoring']['percentage'],
                'T_Signal': t['signals']['signal'],
                'T_Score': t['signals']['score'],
                'Price': t['close'],
                'RSI': round(t['rsi'], 1),
                'ROE': f['ratios'].get('roe'),
                'PE': f['ratios'].get('pe'),
                'D/E': f['ratios'].get('debt_to_equity'),
                'Trend': t['trend']['medium_term'],
                'Note': c['note']
            }
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Sort theo Score giảm dần
        df = df.sort_values('Score', ascending=False)
        
        return df
    
    def get_top_picks(self, n=10):
        """Lấy top N cổ phiếu tốt nhất"""
        df = self.screen_multiple_stocks()
        
        if df.empty:
            return pd.DataFrame()
        
        # Lọc các mã có rating BUY trở lên
        top = df[df['Rating'].isin(['STRONG BUY', 'BUY'])].head(n)
        
        return top
    
    def filter_by_criteria(self, df: pd.DataFrame, 
                          min_score=3.5, 
                          min_roe=15, 
                          max_pe=20,
                          rsi_range=(30, 70)):
        """Lọc cổ phiếu theo tiêu chí cụ thể"""
        filtered = df[
            (df['Score'] >= min_score) &
            (df['ROE'] >= min_roe) &
            (df['PE'] <= max_pe) &
            (df['RSI'] >= rsi_range[0]) &
            (df['RSI'] <= rsi_range[1])
        ]
        
        return filtered


# Example usage
if __name__ == "__main__":
    screener = StockScreener(watchlist=['VNM', 'VCB', 'HPG', 'FPT', 'MWG'])
    
    print("\n" + "="*80)
    print("STOCK SCREENER - Kết hợp Cơ bản & Kỹ thuật")
    print("="*80)
    
    # Screen tất cả
    results = screener.screen_multiple_stocks(max_workers=3)
    
    if not results.empty:
        print("\n📊 KẾT QUẢ SÀNG LỌC:\n")
        print(results.to_string(index=False))
        
        # Top picks
        print("\n\n⭐ TOP PICKS (BUY trở lên):\n")
        top = results[results['Rating'].isin(['STRONG BUY', 'BUY'])]
        if not top.empty:
            for _, row in top.iterrows():
                print(f"✓ {row['Symbol']}: {row['Rating']} - {row['Note']}")
        else:
            print("Không có mã nào đạt tiêu chí BUY")
    else:
        print("Không có kết quả")