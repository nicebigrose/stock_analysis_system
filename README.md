# 📈 Vietnam Stock Analysis System

Hệ thống phân tích cổ phiếu Việt Nam kết hợp **Phân tích Cơ bản** và **Phân tích Kỹ thuật** cho đầu tư trung-dài hạn.

## 🎯 Tính năng

### 1. **Data Pipeline**
- ✅ Crawl dữ liệu giá lịch sử từ vnstock3
- ✅ Crawl dữ liệu tài chính (BCTC, chỉ số tài chính)
- ✅ Cache thông minh để tăng tốc
- ✅ Cập nhật tự động theo lịch

### 2. **Fundamental Analysis**
- 📊 Tính toán chỉ số: ROE, ROA, P/E, P/B, D/E, margins
- 🎯 Chấm điểm cổ phiếu (0-100)
- 💡 Đề xuất mua/bán/giữ
- 📈 So sánh với trung bình ngành

### 3. **Technical Analysis**
- 📉 Các chỉ báo: MA, RSI, MACD, Bollinger Bands, Stochastic
- 🔍 Phát hiện patterns (Golden Cross, RSI extremes, v.v.)
- 📍 Xác định support/resistance
- 🎯 Tín hiệu mua/bán dựa trên kỹ thuật

### 4. **Stock Screener**
- 🔍 Sàng lọc cổ phiếu theo tiêu chí cơ bản + kỹ thuật
- ⭐ Kết hợp điểm fundamental (60%) + technical (40%)
- 📊 Ranking và đề xuất top picks
- ⚡ Xử lý song song nhiều mã

### 5. **Portfolio Manager**
- 💼 Quản lý danh mục cá nhân
- 📊 Theo dõi P&L (realized + unrealized)
- 📈 Tính toán risk metrics (Sharpe ratio, max drawdown)
- 💡 Đề xuất rebalance tự động

### 6. **Dashboard (Streamlit)**
- 🖥️ Giao diện trực quan, dễ sử dụng
- 📊 Biểu đồ tương tác (Plotly)
- 🔔 Alert và notifications
- 📱 Responsive, chạy trên mọi thiết bị

---

## 🚀 Cài đặt

### Yêu cầu
- Python 3.8+
- pip

### Bước 1: Clone/Download code

```bash
# Tạo thư mục dự án
mkdir stock_analysis_system
cd stock_analysis_system
```

### Bước 2: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
vnstock3>=0.1.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
ta>=0.11.0
plotly>=5.18.0
streamlit>=1.29.0
openpyxl>=3.1.0
sqlalchemy>=2.0.0
APScheduler>=3.10.0
python-dotenv>=1.0.0
```

### Bước 3: Tạo cấu trúc thư mục

```
stock_analysis_system/
├── config/
│   ├── __init__.py
│   └── settings.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── cache/
├── src/
│   ├── data_pipeline/
│   ├── analysis/
│   ├── screener/
│   ├── portfolio/
│   └── dashboard/
├── logs/
├── main.py
├── requirements.txt
└── README.md
```

---

## 📖 Hướng dẫn sử dụng

### 1. Chạy Stock Screener

```bash
# Sàng lọc toàn bộ watchlist
python main.py screen

# Sàng lọc các mã cụ thể
python main.py screen -s VNM VCB HPG FPT

# Kết quả sẽ hiển thị trên console và lưu vào file CSV
```

**Output:**
```
📊 SCREENING RESULTS:
Symbol  Rating       Score  F_Rating   T_Signal    Price    RSI  ROE   PE
VNM     STRONG BUY   4.6    EXCELLENT  BUY        75,000   35   25.5  14.5
VCB     BUY          4.2    GOOD       BUY        95,000   42   23.1  15.2
...
```

### 2. Phân tích chi tiết 1 mã

```bash
python main.py analyze --symbol VNM
```

**Output:**
```
📊 TECHNICAL ANALYSIS:
Close: 75,000
RSI: 35.2
Signal: BUY (Score: 3)
Reasons:
  • RSI oversold (<40)
  • Price above MA50 and MA200
  • MACD bullish

💼 FUNDAMENTAL ANALYSIS:
Rating: EXCELLENT (85.5%)
Recommendation: STRONG BUY
Key Ratios:
  ROE: 25.5%
  P/E: 14.5x
  D/E: 0.45x
```

### 3. Quản lý Portfolio

```python
# Trong Python script hoặc notebook
from src.portfolio.portfolio_manager import PortfolioManager

pm = PortfolioManager()

# Nạp tiền
pm.add_cash(100_000_000)  # 100 triệu

# Mua cổ phiếu
pm.buy_stock('VNM', 1000, 75000)  # 1000 cp VNM @ 75k
pm.buy_stock('VCB', 500, 95000)   # 500 cp VCB @ 95k

# Xem portfolio
pm.print_summary()

# Bán cổ phiếu
pm.sell_stock('VNM', 500, 80000)  # Bán 500 cp @ 80k
```

**Hoặc dùng command line:**

```bash
python main.py portfolio
```

### 4. Chạy Dashboard

```bash
# Khởi động Streamlit dashboard
python main.py dashboard

# Hoặc trực tiếp
streamlit run src/dashboard/app.py
```

Mở browser tại: `http://localhost:8501`

**Dashboard có 5 trang:**
- 🏠 Dashboard: Tổng quan thị trường
- 🔍 Stock Screener: Sàng lọc cổ phiếu
- 📊 Stock Analysis: Phân tích chi tiết
- 💼 Portfolio: Quản lý danh mục
- ⚙️ Settings: Cài đặt

### 5. Cập nhật dữ liệu

```bash
# Cập nhật tất cả mã trong watchlist
python main.py update

# Cập nhật các mã cụ thể
python main.py update -s VNM VCB HPG
```

---

## 📊 Ví dụ sử dụng trong code

### Example 1: Tìm cổ phiếu tốt

```python
from src.screener.fundamental_screener import StockScreener

screener = StockScreener()

# Lấy top 10 cổ phiếu tốt nhất
top_picks = screener.get_top_picks(n=10)
print(top_picks)

# Lọc theo tiêu chí tùy chỉnh
results = screener.screen_multiple_stocks()
filtered = screener.filter_by_criteria(
    results,
    min_score=4.0,
    min_roe=20,
    max_pe=15,
    rsi_range=(30, 60)
)
print(filtered)
```

### Example 2: Backtest chiến lược

```python
from src.data_pipeline.price_data import PriceDataCrawler
from src.analysis.technical import TechnicalAnalyzer

crawler = PriceDataCrawler()
analyzer = TechnicalAnalyzer()

# Lấy dữ liệu 2 năm
df = crawler.get_historical_data('VNM', start_date='2023-01-01')

# Thêm indicators
df_with_indicators = analyzer.add_all_indicators(df)

# Simulate trading signals
buy_signals = []
sell_signals = []

for i in range(50, len(df_with_indicators)):
    row = df_with_indicators.iloc[i]
    
    # Buy signal: RSI < 30 và giá trên MA200
    if row['RSI'] < 30 and row['close'] > row['SMA_200']:
        buy_signals.append({
            'date': row.name,
            'price': row['close'],
            'signal': 'BUY'
        })
    
    # Sell signal: RSI > 70 hoặc giá dưới MA50
    elif row['RSI'] > 70 or row['close'] < row['SMA_50']:
        sell_signals.append({
            'date': row.name,
            'price': row['close'],
            'signal': 'SELL'
        })

print(f"Buy signals: {len(buy_signals)}")
print(f"Sell signals: {len(sell_signals)}")
```

### Example 3: Tự động hóa với scheduler

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from src.screener.fundamental_screener import StockScreener

def daily_screening():
    """Chạy screening mỗi ngày sau giờ đóng cửa"""
    print("Running daily screening...")
    screener = StockScreener()
    results = screener.screen_multiple_stocks()
    
    # Lưu kết quả
    results.to_csv(f'daily_screen_{datetime.now().strftime("%Y%m%d")}.csv')
    
    # Gửi alert nếu có cổ phiếu tốt
    top = results[results['Rating'] == 'STRONG BUY']
    if not top.empty:
        print(f"🔔 Alert: {len(top)} stocks rated STRONG BUY!")
        # Có thể gửi email/telegram ở đây

scheduler = BlockingScheduler()
scheduler.add_job(daily_screening, 'cron', hour=15, minute=30)  # 3:30 PM
scheduler.start()
```

---

## ⚙️ Cấu hình

### Tùy chỉnh tiêu chí trong `config/settings.py`:

```python
# Danh sách theo dõi
WATCHLIST = [
    'VNM', 'VCB', 'VHM', 'VIC', 'GAS', 'HPG', 'TCB', 
    # Thêm mã của bạn...
]

# Tiêu chí sàng lọc cơ bản
FUNDAMENTAL_CRITERIA = {
    'min_market_cap': 5000,      # Tỷ đồng
    'min_roe': 15,               # %
    'max_pe': 20,                # Lần
    'max_debt_to_equity': 2,     # Lần
    'min_revenue_growth': 10     # %
}

# Tham số kỹ thuật
TECHNICAL_PARAMS = {
    'ma_periods': [20, 50, 200],
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    # Tùy chỉnh thêm...
}

# Portfolio
PORTFOLIO_CONFIG = {
    'max_positions': 8,           # Tối đa 8 mã
    'max_position_size': 0.20,    # 20%/mã
    'min_cash_reserve': 0.10,     # 10% tiền mặt
}
```

---

## 🎓 Chiến lược đầu tư được khuyến nghị

### 1. **Quy trình 4 bước**

```
Bước 1: SÀNG LỌC CƠ BẢN
└─> Chỉ chọn cổ phiếu có:
    • ROE > 15%
    • P/E < 20
    • D/E < 2
    • Vốn hóa > 5,000 tỷ

Bước 2: PHÂN TÍCH KỸ THUẬT
└─> Tìm điểm vào tốt:
    • RSI 30-40 (điều chỉnh)
    • Giá gần MA200
    • Volume xác nhận
    • MACD sắp crossover

Bước 3: MUA VÀ GIỮ
└─> Mục tiêu: 6-12 tháng
    • Target: +20-30%
    • Stop loss: -15%
    • Theo dõi quarterly

Bước 4: REBALANCE
└─> Mỗi 3-6 tháng:
    • Bán mã lỗ/xấu đi
    • Chốt lời mã đã đạt target
    • Thêm mã mới tốt hơn
```

### 2. **Quản lý rủi ro**

```python
# Rule 1: Đa dạng hóa
- Không quá 20% vào 1 mã
- Giữ 5-8 mã khác ngành
- Dự trữ 10-20% tiền mặt

# Rule 2: Stop loss nghiêm ngặt
- Cắt lỗ tại -15% hoặc khi cơ bản xấu đi
- Không "đu đỉnh" hay "bình quân giá"

# Rule 3: Take profit từng phần
- Chốt 50% khi lãi 25%
- Chốt 30% khi lãi 40%
- Để 20% chạy dài hạn

# Rule 4: Review định kỳ
- Kiểm tra portfolio mỗi tuần
- Đọc BCTC mỗi quý
- Rebalance mỗi 6 tháng
```

---

## 📈 Kỳ vọng thực tế

### ✅ Điều có thể đạt được:
- Lợi nhuận: **15-25%/năm** (tốt hơn gửi tiết kiệm)
- Win rate: **60-70%** (không phải 100%)
- Drawdown: Chấp nhận **-15 đến -20%** tạm thời
- Thời gian: Cần **2-3 năm** để thấy kết quả rõ

### ❌ Điều KHÔNG nên kỳ vọng:
- ❌ Làm giàu nhanh, x2 x3 tài khoản
- ❌ Dự đoán chính xác 100%
- ❌ "Holy Grail" - chiến lược thắng mãi
- ❌ Không thua lỗ bao giờ

---

## 🔧 Troubleshooting

### Lỗi thường gặp:

**1. Không cài được vnstock3:**
```bash
pip install --upgrade pip
pip install vnstock3
```

**2. Lỗi import module:**
```bash
# Đảm bảo đang ở thư mục gốc
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Hoặc thêm vào đầu file
import sys
sys.path.append('/path/to/stock_analysis_system')
```

**3. Không lấy được dữ liệu:**
- Kiểm tra kết nối internet
- Thử lại sau vài phút (vnstock3 có thể bị rate limit)
- Xóa cache: `rm -rf data/cache/*`

**4. Dashboard không chạy:**
```bash
# Cài lại streamlit
pip install --upgrade streamlit

# Chạy với port khác
streamlit run src/dashboard/app.py --server.port 8502
```

---

## 🚨 Lưu ý quan trọng

### ⚠️ Disclaimer:

```
HỆ THỐNG NÀY CHỈ PHỤC VỤ MỤC ĐÍCH GIÁO DỤC VÀ NGHIÊN CỨU.

• KHÔNG phải lời khuyên đầu tư
• KHÔNG đảm bảo lợi nhuận
• Mọi quyết định đầu tư là TRÁCH NHIỆM của bạn
• Hãy tự nghiên cứu kỹ (DYOR - Do Your Own Research)
• Chỉ đầu tư số tiền bạn có thể chấp nhận mất
• Tham khảo ý kiến chuyên gia tài chính nếu cần
```

### 🔐 Bảo mật:

- Không share file `portfolio.json` (chứa thông tin tài khoản)
- Backup dữ liệu định kỳ
- Không commit API keys vào Git

---

## 📚 Tài liệu tham khảo

### Thư viện:
- [vnstock3](https://github.com/thinh-vu/vnstock) - Lấy dữ liệu chứng khoán VN
- [TA-Lib](https://github.com/mrjbq7/ta-lib) - Technical Analysis
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [Plotly](https://plotly.com/) - Interactive charts

### Sách về đầu tư:
- "The Intelligent Investor" - Benjamin Graham
- "One Up On Wall Street" - Peter Lynch
- "A Random Walk Down Wall Street" - Burton Malkiel

### Học thêm:
- Phân tích cơ bản: https://stockopedia.com/
- Phân tích kỹ thuật: https://www.investopedia.com/
- Thị trường VN: https://www.vietstock.vn/

---

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Bạn có thể:
- Báo lỗi (issues)
- Đề xuất tính năng mới
- Cải thiện code
- Viết thêm documentation

---

## 📞 Liên hệ & Hỗ trợ

Nếu gặp vấn đề hoặc cần hỗ trợ:
1. Đọc kỹ README này
2. Check phần Troubleshooting
3. Tìm kiếm trong Issues (nếu có GitHub repo)

---

## 📝 Changelog

### Version 1.0.0 (2025-10-03)
- ✅ Data pipeline với vnstock3
- ✅ Fundamental & Technical analysis
- ✅ Stock screener
- ✅ Portfolio manager
- ✅ Streamlit dashboard

### Roadmap (Coming soon)
- [ ] Telegram/Email alerts
- [ ] Advanced backtesting engine
- [ ] Machine Learning models
- [ ] Sentiment analysis từ tin tức
- [ ] Mobile app

---

## ⭐ Kết luận

Hệ thống này giúp bạn:
1. ✅ Sàng lọc cổ phiếu có cơ bản tốt
2. ✅ Tìm điểm vào/ra hợp lý bằng kỹ thuật
3. ✅ Quản lý danh mục chuyên nghiệp
4. ✅ Tiết kiệm thời gian phân tích

Nhưng nhớ rằng: **Không có hệ thống nào thay thế được tư duy và kỷ luật của chính bạn!**

> "The stock market is a device for transferring money from the impatient to the patient." - Warren Buffett

**Chúc bạn đầu tư thành công! 🚀📈**

---

**Made with ❤️ for Vietnam Stock Market Investors**