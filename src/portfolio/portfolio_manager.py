"""
Module quản lý danh mục đầu tư
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

from src.data_pipeline.price_data import PriceDataCrawler
from config.settings import PORTFOLIO_CONFIG, DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioManager:
    """Quản lý danh mục đầu tư cá nhân"""
    
    def __init__(self, portfolio_file='portfolio.json'):
        self.portfolio_file = DATA_DIR / portfolio_file
        self.price_crawler = PriceDataCrawler()
        self.portfolio = self._load_portfolio()
    
    def _load_portfolio(self):
        """Load danh mục từ file"""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'cash': 0,
                'positions': [],
                'history': []
            }
    
    def _save_portfolio(self):
        """Lưu danh mục vào file"""
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, indent=2, ensure_ascii=False)
        logger.info(f"Portfolio saved to {self.portfolio_file}")
    
    def add_cash(self, amount: float):
        """Nạp tiền vào tài khoản"""
        self.portfolio['cash'] += amount
        self.portfolio['history'].append({
            'date': datetime.now().isoformat(),
            'type': 'deposit',
            'amount': amount
        })
        self._save_portfolio()
        logger.info(f"Added {amount:,.0f} VND to portfolio")
    
    def buy_stock(self, symbol: str, shares: int, price: float, date=None):
        """
        Mua cổ phiếu
        
        Args:
            symbol: Mã cổ phiếu
            shares: Số lượng cổ phiếu
            price: Giá mua
            date: Ngày mua (mặc định là hôm nay)
        """
        if date is None:
            date = datetime.now().isoformat()
        
        total_cost = shares * price * 1.0015  # Phí 0.15%
        
        if total_cost > self.portfolio['cash']:
            logger.error(f"Insufficient cash. Need {total_cost:,.0f}, have {self.portfolio['cash']:,.0f}")
            return False
        
        # Trừ tiền
        self.portfolio['cash'] -= total_cost
        
        # Tìm position hiện có
        existing_position = None
        for pos in self.portfolio['positions']:
            if pos['symbol'] == symbol:
                existing_position = pos
                break
        
        if existing_position:
            # Cập nhật position hiện có
            total_shares = existing_position['shares'] + shares
            total_value = existing_position['shares'] * existing_position['avg_price'] + shares * price
            existing_position['avg_price'] = total_value / total_shares
            existing_position['shares'] = total_shares
        else:
            # Thêm position mới
            self.portfolio['positions'].append({
                'symbol': symbol,
                'shares': shares,
                'avg_price': price,
                'buy_date': date
            })
        
        # Lưu lịch sử
        self.portfolio['history'].append({
            'date': date,
            'type': 'buy',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': total_cost
        })
        
        self._save_portfolio()
        logger.info(f"Bought {shares} shares of {symbol} at {price:,.0f}")
        return True
    
    def sell_stock(self, symbol: str, shares: int, price: float, date=None):
        """
        Bán cổ phiếu
        
        Returns:
            dict với thông tin P&L hoặc False nếu lỗi
        """
        if date is None:
            date = datetime.now().isoformat()
        
        # Tìm position
        position = None
        for pos in self.portfolio['positions']:
            if pos['symbol'] == symbol:
                position = pos
                break
        
        if not position:
            logger.error(f"No position found for {symbol}")
            return False
        
        if shares > position['shares']:
            logger.error(f"Cannot sell {shares} shares. Only have {position['shares']}")
            return False
        
        # Tính toán P&L
        buy_value = shares * position['avg_price']
        sell_value = shares * price * 0.999  # Phí + thuế 0.1%
        pnl = sell_value - buy_value
        pnl_percent = (pnl / buy_value) * 100
        
        # Cập nhật position
        position['shares'] -= shares
        
        # Xóa position nếu bán hết
        if position['shares'] == 0:
            self.portfolio['positions'].remove(position)
        
        # Cộng tiền
        self.portfolio['cash'] += sell_value
        
        # Lưu lịch sử
        self.portfolio['history'].append({
            'date': date,
            'type': 'sell',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': sell_value,
            'pnl': pnl,
            'pnl_percent': pnl_percent
        })
        
        self._save_portfolio()
        logger.info(f"Sold {shares} shares of {symbol} at {price:,.0f}. P&L: {pnl:,.0f} ({pnl_percent:.2f}%)")
        
        return {
            'symbol': symbol,
            'shares': shares,
            'sell_price': price,
            'avg_cost': position['avg_price'],
            'pnl': pnl,
            'pnl_percent': pnl_percent
        }
    
    def get_current_value(self):
        """Tính giá trị danh mục hiện tại"""
        total_value = self.portfolio['cash']
        positions_value = 0
        position_details = []
        
        for pos in self.portfolio['positions']:
            # Lấy giá hiện tại
            latest = self.price_crawler.get_latest_price(pos['symbol'])
            
            if latest:
                current_price = latest['close']
                pos_value = pos['shares'] * current_price
                pnl = (current_price - pos['avg_price']) * pos['shares']
                pnl_percent = ((current_price - pos['avg_price']) / pos['avg_price']) * 100
                
                positions_value += pos_value
                
                position_details.append({
                    'symbol': pos['symbol'],
                    'shares': pos['shares'],
                    'avg_price': pos['avg_price'],
                    'current_price': current_price,
                    'value': pos_value,
                    'cost': pos['shares'] * pos['avg_price'],
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'weight': 0  # Will calculate later
                })
        
        total_value += positions_value
        
        # Tính weight
        for pos in position_details:
            pos['weight'] = (pos['value'] / total_value) * 100 if total_value > 0 else 0
        
        return {
            'total_value': total_value,
            'cash': self.portfolio['cash'],
            'positions_value': positions_value,
            'cash_percent': (self.portfolio['cash'] / total_value * 100) if total_value > 0 else 0,
            'positions': position_details
        }
    
    def get_performance(self):
        """Tính toán hiệu suất đầu tư"""
        # Tính tổng tiền nạp vào
        total_deposits = sum(
            h['amount'] for h in self.portfolio['history'] 
            if h['type'] == 'deposit'
        )
        
        # Giá trị hiện tại
        current = self.get_current_value()
        current_value = current['total_value']
        
        # P&L tổng
        total_pnl = current_value - total_deposits
        total_pnl_percent = (total_pnl / total_deposits * 100) if total_deposits > 0 else 0
        
        # Tính realized P&L từ lịch sử bán
        realized_pnl = sum(
            h.get('pnl', 0) for h in self.portfolio['history']
            if h['type'] == 'sell'
        )
        
        # Unrealized P&L
        unrealized_pnl = sum(pos['pnl'] for pos in current['positions'])
        
        return {
            'total_deposits': total_deposits,
            'current_value': current_value,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl
        }
    
    def get_risk_metrics(self):
        """Tính các chỉ số rủi ro"""
        if not self.portfolio['positions']:
            return {}
        
        returns = []
        
        for pos in self.portfolio['positions']:
            # Lấy lịch sử giá
            df = self.price_crawler.get_historical_data(
                pos['symbol'],
                start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            )
            
            if not df.empty:
                daily_returns = df['close'].pct_change().dropna()
                returns.extend(daily_returns.values)
        
        if not returns:
            return {}
        
        returns = np.array(returns)
        
        # Tính toán metrics
        volatility = np.std(returns) * np.sqrt(252) * 100  # Annualized
        
        # Sharpe Ratio (giả sử risk-free rate = 5%)
        risk_free_rate = 0.05
        perf = self.get_performance()
        annual_return = perf['total_pnl_percent'] / 100
        sharpe_ratio = (annual_return - risk_free_rate) / (volatility / 100) if volatility > 0 else 0
        
        # Max Drawdown (simplified)
        max_drawdown = np.min(returns) * 100
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }
    
    def suggest_rebalance(self):
        """Đề xuất tái cân bằng danh mục"""
        current = self.get_current_value()
        suggestions = []
        
        max_weight = PORTFOLIO_CONFIG['max_position_size'] * 100
        min_cash = PORTFOLIO_CONFIG['min_cash_reserve'] * 100
        
        # Kiểm tra cash
        if current['cash_percent'] < min_cash:
            suggestions.append({
                'type': 'INCREASE_CASH',
                'message': f"Tiền mặt chỉ {current['cash_percent']:.1f}%, nên giữ tối thiểu {min_cash:.0f}%",
                'action': 'Bán bớt một số vị thế'
            })
        
        # Kiểm tra positions
        for pos in current['positions']:
            if pos['weight'] > max_weight:
                over = pos['weight'] - max_weight
                suggestions.append({
                    'type': 'REDUCE_POSITION',
                    'symbol': pos['symbol'],
                    'message': f"{pos['symbol']} chiếm {pos['weight']:.1f}%, vượt ngưỡng {max_weight:.0f}%",
                    'action': f"Giảm khoảng {over:.1f}% ({over/100 * current['total_value']:,.0f} VND)"
                })
            
            # P&L quá lớn (take profit)
            if pos['pnl_percent'] > 30:
                suggestions.append({
                    'type': 'TAKE_PROFIT',
                    'symbol': pos['symbol'],
                    'message': f"{pos['symbol']} đã lãi {pos['pnl_percent']:.1f}%",
                    'action': 'Cân nhắc chốt lợi nhuận một phần'
                })
            
            # Stop loss
            elif pos['pnl_percent'] < -15:
                suggestions.append({
                    'type': 'STOP_LOSS',
                    'symbol': pos['symbol'],
                    'message': f"{pos['symbol']} đang lỗ {pos['pnl_percent']:.1f}%",
                    'action': 'Cân nhắc cắt lỗ nếu cơ bản xấu đi'
                })
        
        return suggestions
    
    def print_summary(self):
        """In báo cáo tóm tắt"""
        current = self.get_current_value()
        perf = self.get_performance()
        
        print("\n" + "="*80)
        print("PORTFOLIO SUMMARY")
        print("="*80)
        
        print(f"\n💰 Tổng giá trị: {current['total_value']:,.0f} VND")
        print(f"   - Tiền mặt: {current['cash']:,.0f} VND ({current['cash_percent']:.1f}%)")
        print(f"   - Cổ phiếu: {current['positions_value']:,.0f} VND ({100-current['cash_percent']:.1f}%)")
        
        print(f"\n📈 Hiệu suất:")
        print(f"   - Tổng nạp: {perf['total_deposits']:,.0f} VND")
        print(f"   - P&L: {perf['total_pnl']:,.0f} VND ({perf['total_pnl_percent']:+.2f}%)")
        print(f"   - Realized: {perf['realized_pnl']:,.0f} VND")
        print(f"   - Unrealized: {perf['unrealized_pnl']:,.0f} VND")
        
        if current['positions']:
            print(f"\n📊 Positions:")
            for pos in current['positions']:
                pnl_symbol = "📈" if pos['pnl'] > 0 else "📉"
                print(f"   {pnl_symbol} {pos['symbol']}: {pos['shares']} cp × {pos['current_price']:,.0f} "
                      f"= {pos['value']:,.0f} ({pos['weight']:.1f}%) | "
                      f"P&L: {pos['pnl']:,.0f} ({pos['pnl_percent']:+.2f}%)")
        
        # Suggestions
        suggestions = self.suggest_rebalance()
        if suggestions:
            print(f"\n💡 Đề xuất:")
            for sug in suggestions:
                print(f"   - {sug['message']}")
                print(f"     → {sug['action']}")


# Example usage
if __name__ == "__main__":
    pm = PortfolioManager()
    
    # Ví dụ: Tạo portfolio mới
    # pm.add_cash(100_000_000)  # 100 triệu
    # pm.buy_stock('VNM', 1000, 75000)
    # pm.buy_stock('VCB', 500, 95000)
    
    pm.print_summary()