"""
Module tinh toan cac chi so rui ro cua portfolio
Copy vao: src/portfolio/risk_metrics.py
"""
import numpy as np
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskMetrics:
    """Tinh toan cac chi so rui ro"""
    
    def __init__(self, risk_free_rate=0.05):
        """
        Args:
            risk_free_rate: Lai suat phi rui ro (5% cho VN)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_returns(self, prices):
        """Tinh daily returns tu gia"""
        if isinstance(prices, pd.Series):
            returns = prices.pct_change().dropna()
        else:
            returns = pd.Series(prices).pct_change().dropna()
        return returns
    
    def volatility(self, returns, annualize=True):
        """
        Tinh volatility (do bien dong)
        
        Args:
            returns: Daily returns
            annualize: Annualize ket qua (√252)
        """
        vol = np.std(returns)
        
        if annualize:
            vol = vol * np.sqrt(252)  # 252 trading days
        
        return vol
    
    def sharpe_ratio(self, returns, risk_free_rate=None):
        """
        Sharpe Ratio = (Return - Risk Free Rate) / Volatility
        
        Do luong loi nhuan dieu chinh theo rui ro
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily RF rate
        
        if len(excess_returns) == 0 or np.std(excess_returns) == 0:
            return 0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns)
        sharpe_annualized = sharpe * np.sqrt(252)
        
        return sharpe_annualized
    
    def sortino_ratio(self, returns, risk_free_rate=None):
        """
        Sortino Ratio - Giong Sharpe nhung chi tinh downside volatility
        
        Tot hon Sharpe vi chi phat bien dong am
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        excess_returns = returns - (risk_free_rate / 252)
        
        # Chi lay negative returns
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return np.inf
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0
        
        sortino = np.mean(excess_returns) / downside_std
        sortino_annualized = sortino * np.sqrt(252)
        
        return sortino_annualized
    
    def max_drawdown(self, prices):
        """
        Max Drawdown - Sut giam lon nhat tu dinh
        
        Returns:
            dict voi max_drawdown (%), peak, trough
        """
        if isinstance(prices, list):
            prices = pd.Series(prices)
        
        # Tinh cumulative returns
        cumulative = (1 + self.calculate_returns(prices)).cumprod()
        
        # Running maximum
        running_max = cumulative.expanding().max()
        
        # Drawdown
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()
        
        # Tim peak truoc do
        peak_date = running_max[:max_dd_date].idxmax()
        
        return {
            'max_drawdown': max_dd * 100,  # %
            'peak_date': peak_date,
            'trough_date': max_dd_date,
            'drawdown_series': drawdown
        }
    
    def value_at_risk(self, returns, confidence_level=0.95):
        """
        VaR (Value at Risk) - Thua lo toi da o muc tin cay nhat dinh
        
        Args:
            confidence_level: 0.95 = 95% (5% worst case)
        """
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return var * 100  # Convert to %
    
    def conditional_var(self, returns, confidence_level=0.95):
        """
        CVaR (Conditional VaR) / Expected Shortfall
        
        Trung binh cua cac losses vuot qua VaR
        """
        var = np.percentile(returns, (1 - confidence_level) * 100)
        cvar = returns[returns <= var].mean()
        return cvar * 100  # Convert to %
    
    def beta(self, stock_returns, market_returns):
        """
        Beta - Do luong do nhay cam voi thi truong
        
        Beta > 1: Bien dong manh hon thi truong
        Beta < 1: Bien dong it hon thi truong
        Beta = 1: Bien dong nhu thi truong
        """
        if len(stock_returns) != len(market_returns):
            min_len = min(len(stock_returns), len(market_returns))
            stock_returns = stock_returns[:min_len]
            market_returns = market_returns[:min_len]
        
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 0
        
        beta = covariance / market_variance
        return beta
    
    def alpha(self, stock_returns, market_returns, risk_free_rate=None):
        """
        Alpha - Loi nhuan vuot troi so voi thi truong
        
        Alpha > 0: Outperform
        Alpha < 0: Underperform
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        beta_value = self.beta(stock_returns, market_returns)
        
        stock_return = np.mean(stock_returns) * 252
        market_return = np.mean(market_returns) * 252
        
        alpha = stock_return - (risk_free_rate + beta_value * (market_return - risk_free_rate))
        
        return alpha
    
    def calmar_ratio(self, returns, prices):
        """
        Calmar Ratio = Annualized Return / Max Drawdown
        
        Do luong return/risk, cao hon thi tot hon
        """
        annual_return = np.mean(returns) * 252
        max_dd = abs(self.max_drawdown(prices)['max_drawdown'])
        
        if max_dd == 0:
            return np.inf
        
        calmar = (annual_return * 100) / max_dd
        return calmar
    
    def portfolio_metrics(self, returns, prices, market_returns=None):
        """
        Tinh tat ca metrics cho portfolio
        
        Returns:
            dict voi tat ca chi so
        """
        metrics = {
            'total_return': ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100,
            'annualized_return': (np.mean(returns) * 252) * 100,
            'volatility': self.volatility(returns) * 100,
            'sharpe_ratio': self.sharpe_ratio(returns),
            'sortino_ratio': self.sortino_ratio(returns),
            'max_drawdown': self.max_drawdown(prices)['max_drawdown'],
            'var_95': self.value_at_risk(returns, 0.95),
            'cvar_95': self.conditional_var(returns, 0.95),
            'calmar_ratio': self.calmar_ratio(returns, prices)
        }
        
        # Neu co market returns, tinh beta va alpha
        if market_returns is not None and len(market_returns) > 0:
            metrics['beta'] = self.beta(returns, market_returns)
            metrics['alpha'] = self.alpha(returns, market_returns)
        
        return metrics
    
    def risk_adjusted_performance(self, metrics):
        """
        Danh gia hieu suat dieu chinh rui ro
        
        Returns:
            rating (A, B, C, D, F)
        """
        score = 0
        max_score = 0
        
        # Sharpe Ratio (0-30 points)
        max_score += 30
        if metrics['sharpe_ratio'] >= 2:
            score += 30
        elif metrics['sharpe_ratio'] >= 1:
            score += 20
        elif metrics['sharpe_ratio'] >= 0.5:
            score += 10
        
        # Return (0-30 points)
        max_score += 30
        if metrics['annualized_return'] >= 25:
            score += 30
        elif metrics['annualized_return'] >= 15:
            score += 20
        elif metrics['annualized_return'] >= 10:
            score += 10
        elif metrics['annualized_return'] >= 5:
            score += 5
        
        # Max Drawdown (0-20 points)
        max_score += 20
        if abs(metrics['max_drawdown']) <= 10:
            score += 20
        elif abs(metrics['max_drawdown']) <= 15:
            score += 15
        elif abs(metrics['max_drawdown']) <= 20:
            score += 10
        elif abs(metrics['max_drawdown']) <= 30:
            score += 5
        
        # Volatility (0-20 points)
        max_score += 20
        if metrics['volatility'] <= 15:
            score += 20
        elif metrics['volatility'] <= 20:
            score += 15
        elif metrics['volatility'] <= 25:
            score += 10
        elif metrics['volatility'] <= 30:
            score += 5
        
        percentage = (score / max_score) * 100
        
        if percentage >= 85:
            rating = 'A'
        elif percentage >= 70:
            rating = 'B'
        elif percentage >= 55:
            rating = 'C'
        elif percentage >= 40:
            rating = 'D'
        else:
            rating = 'F'
        
        return {
            'rating': rating,
            'score': score,
            'max_score': max_score,
            'percentage': percentage
        }


# Example usage
if __name__ == "__main__":
    # Tao du lieu mau
    np.random.seed(42)
    
    # Gia lap gia co phieu
    initial_price = 100000
    returns = np.random.normal(0.0005, 0.02, 252)  # 252 trading days
    prices = [initial_price]
    
    for r in returns:
        prices.append(prices[-1] * (1 + r))
    
    prices = pd.Series(prices)
    returns = pd.Series(returns)
    
    # Tinh metrics
    risk_calc = RiskMetrics()
    metrics = risk_calc.portfolio_metrics(returns, prices)
    
    print("=== PORTFOLIO RISK METRICS ===\n")
    print(f"Total Return: {metrics['total_return']:+.2f}%")
    print(f"Annualized Return: {metrics['annualized_return']:+.2f}%")
    print(f"Volatility: {metrics['volatility']:.2f}%")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
    print(f"Sortino Ratio: {metrics['sortino_ratio']:.3f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"VaR (95%): {metrics['var_95']:.2f}%")
    print(f"CVaR (95%): {metrics['cvar_95']:.2f}%")
    print(f"Calmar Ratio: {metrics['calmar_ratio']:.3f}")
    
    # Risk-adjusted performance
    performance = risk_calc.risk_adjusted_performance(metrics)
    print(f"\n[RATING] Risk-Adjusted: {performance['rating']}")
    print(f"Score: {performance['score']}/{performance['max_score']} ({performance['percentage']:.1f}%)")