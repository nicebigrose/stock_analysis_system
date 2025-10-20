# 🚀 Quick Installation Guide

## Cài đặt trong 5 phút

### Bước 1: Download code

```bash
# Tạo thư mục dự án
mkdir stock_analysis_system
cd stock_analysis_system

# Copy tất cả các file từ artifacts vào thư mục này
```

### Bước 2: Chạy setup tự động

```bash
python setup.py
```

Script sẽ tự động:
- ✅ Tạo cấu trúc thư mục
- ✅ Tạo __init__.py files
- ✅ Tạo requirements.txt
- ✅ Cài đặt dependencies (nếu chọn y)
- ✅ Chạy tests (nếu chọn y)

### Bước 3: Test hệ thống

```bash
# Quick test với 1 mã
python quickstart.py VNM

# Hoặc chạy screener
python main.py screen -s VNM VCB HPG
```

### Bước 4: Khởi động dashboard

```bash
streamlit run src/dashboard/app.py
```

Truy cập: http://localhost:8501

---

## Cài đặt thủ công (nếu setup.py lỗi)

### 1. Cài requirements

```bash
pip install vnstock3 pandas numpy ta plotly streamlit requests beautifulsoup4 lxml openpyxl sqlalchemy APScheduler python-dotenv
```

### 2. Tạo thư mục

```bash
mkdir -p config data/raw data/processed data/cache logs notebooks tests
mkdir -p src/data_pipeline src/analysis src/screener src/portfolio src/dashboard
```

### 3. Tạo __init__.py

```bash
# Tạo file trống trong mỗi thư mục Python
touch config/__init__.py
touch src/__init__.py
touch src/data_pipeline/__init__.py
touch src/analysis/__init__.py
touch src/screener/__init__.py
touch src/portfolio/__init__.py
touch src/dashboard/__init__.py
touch tests/__init__.py
```

### 4. Copy các file code

Copy tất cả các file từ artifacts:
- `config/settings.py`
- `src/data_pipeline/price_data.py`
- `src/data_pipeline/fundamental_data.py`
- `src/data_pipeline/data_updater.py`
- `src/analysis/technical.py`
- `src/analysis/fundamental.py`
- `src/analysis/valuation.py`
- `src/screener/fundamental_screener.py`
- `src/screener/technical_scanner.py`
- `src/portfolio/portfolio_manager.py`
- `src/portfolio/risk_metrics.py`
- `src/dashboard/app.py`
- `main.py`
- `README.md`

---

## Troubleshooting

### Lỗi: Module not found

```bash
# Đảm bảo đang ở thư mục gốc
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Windows
set PYTHONPATH=%PYTHONPATH%;%CD%
```

### Lỗi: vnstock3 không cài được

```bash
pip install --upgrade pip
pip install vnstock3 --no-cache-dir
```

### Lỗi: Streamlit không chạy

```bash
pip install --upgrade streamlit
streamlit run src/dashboard/app.py --server.port 8502
```

### Lỗi: Không lấy được dữ liệu

- Kiểm tra internet
- Thử lại sau vài phút (rate limit)
- Xóa cache: `rm -rf data/cache/*`

---

## Kiểm tra cài đặt thành công

### Test 1: Import modules

```python
python -c "from src.data_pipeline.price_data import PriceDataCrawler; print('✓ OK')"
python -c "from src.analysis.technical import TechnicalAnalyzer; print('✓ OK')"
python -c "from src.screener.fundamental_screener import StockScreener; print('✓ OK')"
```

### Test 2: Lấy dữ liệu

```python
python -c "
from src.data_pipeline.price_data import PriceDataCrawler
crawler = PriceDataCrawler()
df = crawler.get_historical_data('VNM', start_date='2024-01-01')
print(f'✓ OK: Got {len(df)} records')
"
```

### Test 3: Chạy analysis

```bash
python quickstart.py VNM
```

Nếu tất cả đều OK → Cài đặt thành công! 🎉

---

## Cấu trúc file cuối cùng

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
│   ├── __init__.py
│   ├── data_pipeline/
│   │   ├── __init__.py
│   │   ├── price_data.py
│   │   ├── fundamental_data.py
│   │   └── data_updater.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── technical.py
│   │   ├── fundamental.py
│   │   └── valuation.py
│   ├── screener/
│   │   ├── __init__.py
│   │   ├── fundamental_screener.py
│   │   └── technical_scanner.py
│   ├── portfolio/
│   │   ├── __init__.py
│   │   ├── portfolio_manager.py
│   │   └── risk_metrics.py
│   └── dashboard/
│       ├── __init__.py
│       └── app.py
├── logs/
├── notebooks/
├── tests/
│   ├── __init__.py
│   └── test_analysis.py
├── main.py
├── quickstart.py
├── setup.py
├── requirements.txt
├── README.md
├── INSTALL.md
└── .gitignore
```

---

## Next Steps

Sau khi cài đặt xong:

1. **Đọc README.md** - Hướng dẫn chi tiết
2. **Chạy quickstart.py** - Test nhanh
3. **Explore dashboard** - Giao diện trực quan
4. **Customize settings.py** - Điều chỉnh theo nhu cầu
5. **Start investing!** - Nhưng nhớ DYOR! 

---

🎯 **Mục tiêu:** Hệ thống chạy được trong 10 phút!

📚 **Support:** Check README.md hoặc logs/system.log nếu có lỗi

⚠️ **Disclaimer:** Educational purposes only. Not financial advice!