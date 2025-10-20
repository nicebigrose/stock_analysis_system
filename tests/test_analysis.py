"""
Unit tests cho các module phân tích
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.analysis.technical import TechnicalAnalyzer
from src.analysis.fundamental import FundamentalAnalyzer
from src.portfolio.risk_metrics import RiskMetrics


class TestTechnicalAnalyzer(unittest.TestCase):
    """Test technical analysis"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.analyzer = TechnicalAnalyzer()
        
        # Tạo fake price data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)
        
        self.df = pd.DataFrame({
            'open': np.random.uniform(70000, 80000, len(dates)),
            'high': np.random.uniform(75000, 85000, len(dates)),
            'low': np.random.uniform(65000, 75000, len(dates)),
            'close': np.random.uniform(70000, 80000, len(dates)),
            'volume': np.random.uniform(1000000, 5000000, len(dates))
        }, index=dates)
    
    def test_add_indicators(self):
        """Test thêm indicators"""
        df_with_indicators = self.analyzer.add_all_indicators(self.df)
        
        # Kiểm tra các cột mới
        self.assertIn('RSI', df_with_indicators.columns)
        self.assertIn('MACD', df_with_indicators.columns)
        self.assertIn('SMA_50', df_with_indicators.columns)
        self.assertIn('SMA_200', df_with_indicators.columns)
        
        # Kiểm tra RSI trong range 0-100
        self.assertTrue(df_with_indicators['RSI'].dropna().between(0, 100).all())
    
    def test_generate_signals(self):
        """Test tạo tín hiệu"""
        df_with_indicators = self.analyzer.add_all_indicators(self.df)
        signals = self.analyzer.generate_signals(df_with_indicators)
        
        self.assertIn('signal', signals)
        self.assertIn('score', signals)
        self.assertIn(signals['signal'], ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL'])
    
    def test_calculate_trend(self):
        """Test xác định trend"""
        df_with_indicators = self.analyzer.add_all_indicators(self.df)
        trend = self.analyzer.calculate_trend(df_with_indicators)
        
        self.assertIn('long_term', trend)
        self.assertIn('medium_term', trend)
        self.assertIn(trend['long_term'], ['Uptrend', 'Downtrend', 'Sideways'])


class TestFundamentalAnalyzer(unittest.TestCase):
    """Test fundamental analysis"""
    
    def setUp(self):
        """Setup test data"""
        self.analyzer = FundamentalAnalyzer()
        
        self.test_ratios = {
            'symbol': 'TEST',
            'roe': 20.0,
            'roa': 10.0,
            'pe': 15.0,
            'pb': 2.5,
            'debt_to_equity': 0.8,
            'net_margin': 12.0,
            'current_ratio': 2.0,
            'eps': 5000
        }
    
    def test_score_stock(self):
        """Test chấm điểm cổ phiếu"""
        result = self.analyzer.score_stock(self.test_ratios)
        
        self.assertIn('score', result)
        self.assertIn('rating', result)
        self.assertIn('percentage', result)
        
        # Score phải từ 0-100
        self.assertGreaterEqual(result['percentage'], 0)
        self.assertLessEqual(result['percentage'], 100)
    
    def test_check_criteria(self):
        """Test kiểm tra tiêu chí"""
        result = self.analyzer.check_criteria(self.test_ratios)
        
        self.assertIn('meets_criteria', result)
        self.assertIn('passed', result)
        self.assertIn('failed', result)
        
        self.assertIsInstance(result['meets_criteria'], bool)
    
    def test_analyze_stock(self):
        """Test phân tích tổng hợp"""
        result = self.analyzer.analyze_stock(self.test_ratios)
        
        self.assertIn('scoring', result)
        self.assertIn('criteria', result)
        self.assertIn('recommendation', result)
        
        # Recommendation phải có action
        self.assertIn('action', result['recommendation'])


class TestRiskMetrics(unittest.TestCase):
    """Test risk metrics"""
    
    def setUp(self):
        """Setup test data"""
        self.risk_calc = RiskMetrics()
        
        # Tạo fake returns
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 252))
        
        # Tạo fake prices
        initial_price = 100000
        prices = [initial_price]
        for r in self.returns:
            prices.append(prices[-1] * (1 + r))
        self.prices = pd.Series(prices)
    
    def test_volatility(self):
        """Test tính volatility"""
        vol = self.risk_calc.volatility(self.returns)
        
        self.assertIsInstance(vol, float)
        self.assertGreater(vol, 0)
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio"""
        sharpe = self.risk_calc.sharpe_ratio(self.returns)
        
        self.assertIsInstance(sharpe, float)
    
    def test_max_drawdown(self):
        """Test max drawdown"""
        dd = self.risk_calc.max_drawdown(self.prices)
        
        self.assertIn('max_drawdown', dd)
        self.assertIn('peak_date', dd)
        self.assertIn('trough_date', dd)
        
        # Max drawdown phải âm
        self.assertLessEqual(dd['max_drawdown'], 0)
    
    def test_portfolio_metrics(self):
        """Test tính tất cả metrics"""
        metrics = self.risk_calc.portfolio_metrics(self.returns, self.prices)
        
        required_keys = ['total_return', 'annualized_return', 'volatility', 
                        'sharpe_ratio', 'max_drawdown']
        
        for key in required_keys:
            self.assertIn(key, metrics)


class TestDataIntegration(unittest.TestCase):
    """Test integration giữa các modules"""
    
    def test_full_analysis_flow(self):
        """Test flow hoàn chỉnh từ data đến signal"""
        # Tạo data
        dates = pd.date_range(start='2024-01-01', periods=300, freq='D')
        np.random.seed(42)
        
        df = pd.DataFrame({
            'open': np.random.uniform(70000, 80000, len(dates)),
            'high': np.random.uniform(75000, 85000, len(dates)),
            'low': np.random.uniform(65000, 75000, len(dates)),
            'close': np.random.uniform(70000, 80000, len(dates)),
            'volume': np.random.uniform(1000000, 5000000, len(dates))
        }, index=dates)
        
        # Technical analysis
        tech_analyzer = TechnicalAnalyzer()
        tech_result = tech_analyzer.analyze_stock(df, 'TEST')
        
        self.assertIsNotNone(tech_result)
        self.assertIn('signals', tech_result)
        
        # Fundamental analysis
        fund_analyzer = FundamentalAnalyzer()
        ratios = {
            'symbol': 'TEST',
            'roe': 20.0,
            'pe': 15.0,
            'debt_to_equity': 0.8,
            'eps': 5000
        }
        
        fund_result = fund_analyzer.analyze_stock(ratios)
        
        self.assertIsNotNone(fund_result)
        self.assertIn('recommendation', fund_result)


def run_tests():
    """Chạy tất cả tests"""
    # Tạo test suite
    suite = unittest.TestSuite()
    
    # Thêm tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTechnicalAnalyzer))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFundamentalAnalyzer))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRiskMetrics))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDataIntegration))
    
    # Chạy tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)