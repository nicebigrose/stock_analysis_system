"""
Cấu hình hệ thống
Copy file này vào: config/settings.py
"""
import os
from pathlib import Path

# Thư mục gốc
BASE_DIR = Path(__file__).resolve().parent.parent

# Thư mục dữ liệu
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
CACHE_DIR = DATA_DIR / 'cache'

# Tạo thư mục nếu chưa có
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Danh sách cổ phiếu theo dõi (VN30 + một số mã khác)
WATCHLIST = [
    'VNM', 'VCB', 'VHM', 'VIC', 'GAS', 'HPG', 'TCB', 'MSN', 
    'BID', 'VPB', 'CTG', 'MWG', 'PLX', 'VRE', 'HDB',
    'SSI', 'MBB', 'FPT', 'STB', 'POW', 'ACB', 'VJC',
    'GVR', 'PDR', 'SAB', 'VCI', 'TPB', 'REE'
]

# Tiêu chí sàng lọc cơ bản
FUNDAMENTAL_CRITERIA = {
    'min_market_cap': 5000,  # Tỷ đồng
    'min_roe': 15,           # %
    'max_pe': 20,            # Lần
    'max_debt_to_equity': 2, # Lần
    'min_revenue_growth': 10 # %
}

# Tham số kỹ thuật
TECHNICAL_PARAMS = {
    'ma_periods': [20, 50, 200],
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'bb_period': 20,
    'bb_std': 2
}

# Cấu hình portfolio
PORTFOLIO_CONFIG = {
    'max_positions': 8,
    'max_position_size': 0.20,  # 20% mỗi mã
    'min_cash_reserve': 0.10,   # 10% tiền mặt
    'rebalance_threshold': 0.05  # 5% chênh lệch
}

# Cấu hình cập nhật dữ liệu
UPDATE_SCHEDULE = {
    'price_data': '15:30',      # Sau giờ đóng cửa
    'fundamental_data': 'weekly',
    'portfolio_review': 'daily'
}

# Alert thresholds
ALERT_THRESHOLDS = {
    'price_change': 0.05,       # 5%
    'volume_spike': 2.0,        # Gấp 2 lần TB
    'rsi_extreme': (25, 75),
    'support_resistance': 0.02  # 2% từ vùng quan trọng
}

# Database (SQLite)
DB_PATH = DATA_DIR / 'stock_data.db'

# Logging
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'system.log'

print(f"Configuration loaded. Base directory: {BASE_DIR}")