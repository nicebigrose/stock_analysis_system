"""
Module phân tích kỹ thuật
"""
import pandas as pd
import numpy as np
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
import logging

from config.settings import TECHNICAL_PARAMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Phân tích kỹ thuật cổ phiếu"""
    
    def __init__(self, params=None):
        self.params = params or TECHNICAL_PARAMS
    
    def add_all_indicators(self, df: pd.DataFrame):
        """
        Thêm tất cả chỉ báo kỹ thuật vào DataFrame
        
        Args:
            df: DataFrame với cột close, high, low, volume
            
        Returns:
            DataFrame với các chỉ báo đã được thêm
        """
        df = df.copy()
        
        # Moving Averages
        for period in self.params['ma_periods']:
            df[f'SMA_{period}'] = SMAIndicator(
                close=df['close'], window=period
            ).sma_indicator()
            
            df[f'EMA_{period}'] = EMAIndicator(
                close=df['close'], window=period
            ).ema_indicator()
        
        # RSI
        rsi = RSIIndicator(
            close=df['close'], 
            window=self.params['rsi_period']
        )
        df['RSI'] = rsi.rsi()
        
        # MACD
        macd = MACD(
            close=df['close'],
            window_fast=self.params['macd_fast'],
            window_slow=self.params['macd_slow'],
            window_sign=self.params['macd_signal']
        )
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = BollingerBands(
            close=df['close'],
            window=self.params['bb_period'],
            window_dev=self.params['bb_std']
        )
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_middle'] = bb.bollinger_mavg()
        df['BB_lower'] = bb.bollinger_lband()
        df['BB_width'] = bb.bollinger_wband()
        
        # Stochastic
        stoch = StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14,
            smooth_window=3
        )
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        
        # ATR (Average True Range)
        atr = AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14
        )
        df['ATR'] = atr.average_true_range()
        
        # Volume indicators
        df['OBV'] = OnBalanceVolumeIndicator(
            close=df['close'],
            volume=df['volume']
        ).on_balance_volume()
        
        # Price changes
        df['Daily_Return'] = df['close'].pct_change()
        df['Volume_Change'] = df['volume'].pct_change()
        
        return df
    
    def identify_support_resistance(self, df: pd.DataFrame, window=20):
        """Xác định vùng hỗ trợ/kháng cự"""
        df = df.copy()
        
        # Local minima (support)
        df['Local_Min'] = df['low'].rolling(window=window, center=True).min()
        df['Support'] = (df['low'] == df['Local_Min'])
        
        # Local maxima (resistance)  
        df['Local_Max'] = df['high'].rolling(window=window, center=True).max()
        df['Resistance'] = (df['high'] == df['Local_Max'])
        
        # Tìm các mức support/resistance gần nhất
        supports = df[df['Support']]['low'].tail(3).values
        resistances = df[df['Resistance']]['high'].tail(3).values
        
        return {
            'supports': supports.tolist() if len(supports) > 0 else [],
            'resistances': resistances.tolist() if len(resistances) > 0 else []
        }
    
    def detect_patterns(self, df: pd.DataFrame):
        """Phát hiện các pattern cơ bản"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        patterns = []
        
        # Golden Cross (MA ngắn cắt lên MA dài)
        if latest['SMA_50'] > latest['SMA_200'] and prev['SMA_50'] <= prev['SMA_200']:
            patterns.append('Golden Cross (Bullish)')
        
        # Death Cross (MA ngắn cắt xuống MA dài)
        if latest['SMA_50'] < latest['SMA_200'] and prev['SMA_50'] >= prev['SMA_200']:
            patterns.append('Death Cross (Bearish)')
        
        # RSI Oversold
        if latest['RSI'] < self.params['rsi_oversold']:
            patterns.append('RSI Oversold (Potential Buy)')
        
        # RSI Overbought
        if latest['RSI'] > self.params['rsi_overbought']:
            patterns.append('RSI Overbought (Potential Sell)')
        
        # MACD Crossover
        if latest['MACD'] > latest['MACD_signal'] and prev['MACD'] <= prev['MACD_signal']:
            patterns.append('MACD Bullish Crossover')
        
        if latest['MACD'] < latest['MACD_signal'] and prev['MACD'] >= prev['MACD_signal']:
            patterns.append('MACD Bearish Crossover')
        
        # Bollinger Bands breakout
        if latest['close'] > latest['BB_upper']:
            patterns.append('BB Upper Breakout (Overbought)')
        
        if latest['close'] < latest['BB_lower']:
            patterns.append('BB Lower Breakout (Oversold)')
        
        return patterns
    
    def calculate_trend(self, df: pd.DataFrame):
        """Xác định xu hướng tổng thể"""
        latest = df.iloc[-1]
        
        # Dựa vào MA
        if latest['close'] > latest['SMA_200']:
            long_trend = 'Uptrend'
        elif latest['close'] < latest['SMA_200']:
            long_trend = 'Downtrend'
        else:
            long_trend = 'Sideways'
        
        if latest['close'] > latest['SMA_50']:
            medium_trend = 'Uptrend'
        elif latest['close'] < latest['SMA_50']:
            medium_trend = 'Downtrend'
        else:
            medium_trend = 'Sideways'
        
        # Trend strength
        ma_slope = (latest['SMA_50'] - df.iloc[-20]['SMA_50']) / 20
        
        return {
            'long_term': long_trend,
            'medium_term': medium_trend,
            'strength': 'Strong' if abs(ma_slope) > 0.5 else 'Weak'
        }
    
    def generate_signals(self, df: pd.DataFrame):
        """
        Tạo tín hiệu mua/bán/giữ
        
        Returns:
            dict với signal, score, reasons
        """
        latest = df.iloc[-1]
        score = 0
        reasons = []
        
        # RSI signal
        if latest['RSI'] < 30:
            score += 2
            reasons.append('RSI oversold (<30)')
        elif latest['RSI'] < 40:
            score += 1
            reasons.append('RSI attractive (<40)')
        elif latest['RSI'] > 70:
            score -= 2
            reasons.append('RSI overbought (>70)')
        elif latest['RSI'] > 60:
            score -= 1
            reasons.append('RSI high (>60)')
        
        # MACD signal
        if latest['MACD'] > latest['MACD_signal'] and latest['MACD_diff'] > 0:
            score += 1
            reasons.append('MACD bullish')
        elif latest['MACD'] < latest['MACD_signal']:
            score -= 1
            reasons.append('MACD bearish')
        
        # Price vs MA
        if latest['close'] > latest['SMA_50'] > latest['SMA_200']:
            score += 2
            reasons.append('Price above MA50 and MA200')
        elif latest['close'] < latest['SMA_50'] < latest['SMA_200']:
            score -= 2
            reasons.append('Price below MA50 and MA200')
        
        # Bollinger Bands
        if latest['close'] < latest['BB_lower']:
            score += 1
            reasons.append('Price near lower BB')
        elif latest['close'] > latest['BB_upper']:
            score -= 1
            reasons.append('Price near upper BB')
        
        # Volume confirmation
        avg_volume = df['volume'].tail(20).mean()
        if latest['volume'] > avg_volume * 1.5:
            reasons.append('High volume confirmation')
        
        # Generate final signal
        if score >= 3:
            signal = 'STRONG BUY'
        elif score >= 1:
            signal = 'BUY'
        elif score <= -3:
            signal = 'STRONG SELL'
        elif score <= -1:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        return {
            'signal': signal,
            'score': score,
            'reasons': reasons,
            'rsi': latest['RSI'],
            'macd': latest['MACD'],
            'price_vs_ma50': ((latest['close'] - latest['SMA_50']) / latest['SMA_50'] * 100),
            'price_vs_ma200': ((latest['close'] - latest['SMA_200']) / latest['SMA_200'] * 100)
        }
    
    def analyze_stock(self, df: pd.DataFrame, symbol: str = None):
        """
        Phân tích tổng hợp một cổ phiếu
        
        Returns:
            dict với đầy đủ thông tin phân tích
        """
        # Thêm indicators
        df_with_indicators = self.add_all_indicators(df)
        
        # Các phân tích
        trend = self.calculate_trend(df_with_indicators)
        patterns = self.detect_patterns(df_with_indicators)
        signals = self.generate_signals(df_with_indicators)
        support_resistance = self.identify_support_resistance(df_with_indicators)
        
        latest = df_with_indicators.iloc[-1]
        
        result = {
            'symbol': symbol,
            'date': latest.name,
            'close': latest['close'],
            'volume': latest['volume'],
            
            # Technical indicators
            'rsi': latest['RSI'],
            'macd': latest['MACD'],
            'macd_signal': latest['MACD_signal'],
            'sma_50': latest['SMA_50'],
            'sma_200': latest['SMA_200'],
            'bb_upper': latest['BB_upper'],
            'bb_lower': latest['BB_lower'],
            
            # Analysis
            'trend': trend,
            'patterns': patterns,
            'signals': signals,
            'support_resistance': support_resistance,
            
            # Full dataframe for further use
            'dataframe': df_with_indicators
        }
        
        return result


# Example usage
if __name__ == "__main__":
    # Test với dữ liệu mẫu
    from src.data_pipeline.price_data import PriceDataCrawler
    
    crawler = PriceDataCrawler()
    df = crawler.get_historical_data('VNM', start_date='2024-01-01')
    
    if not df.empty:
        analyzer = TechnicalAnalyzer()
        result = analyzer.analyze_stock(df, symbol='VNM')
        
        print(f"\n{'='*60}")
        print(f"Technical Analysis for {result['symbol']}")
        print(f"{'='*60}")
        print(f"Date: {result['date']}")
        print(f"Close: {result['close']:,.0f}")
        print(f"\nTrend: {result['trend']}")
        print(f"\nSignal: {result['signals']['signal']} (Score: {result['signals']['score']})")
        print(f"Reasons:")
        for reason in result['signals']['reasons']:
            print(f"  - {reason}")
        
        if result['patterns']:
            print(f"\nPatterns detected:")
            for pattern in result['patterns']:
                print(f"  - {pattern}")
        
        print(f"\nSupport levels: {result['support_resistance']['supports']}")
        print(f"Resistance levels: {result['support_resistance']['resistances']}")