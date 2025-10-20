# ✅ Deployment Checklist

## Danh sách các file cần tạo

### 📁 Cấu trúc thư mục
- [ ] `config/`
- [ ] `data/raw/`
- [ ] `data/processed/`
- [ ] `data/cache/`
- [ ] `src/data_pipeline/`
- [ ] `src/analysis/`
- [ ] `src/screener/`
- [ ] `src/portfolio/`
- [ ] `src/dashboard/`
- [ ] `logs/`
- [ ] `notebooks/`
- [ ] `tests/`

### 📄 File __init__.py (8 files)
- [ ] `config/__init__.py`
- [ ] `src/__init__.py`
- [ ] `src/data_pipeline/__init__.py`
- [ ] `src/analysis/__init__.py`
- [ ] `src/screener/__init__.py`
- [ ] `src/portfolio/__init__.py`
- [ ] `src/dashboard/__init__.py`
- [ ] `tests/__init__.py`

### 🔧 Config files (1 file)
- [ ] `config/settings.py`

### 📊 Data Pipeline (3 files)
- [ ] `src/data_pipeline/price_data.py`
- [ ] `src/data_pipeline/fundamental_data.py`
- [ ] `src/data_pipeline/data_updater.py`

### 📈 Analysis (3 files)
- [ ] `src/analysis/technical.py`
- [ ] `src/analysis/fundamental.py`
- [ ] `src/analysis/valuation.py`

### 🔍 Screener (2 files)
- [ ] `src/screener/fundamental_screener.py`
- [ ] `src/screener/technical_scanner.py`

### 💼 Portfolio (2 files)
- [ ] `src/portfolio/portfolio_manager.py`
- [ ] `src/portfolio/risk_metrics.py`

### 🖥️ Dashboard (1 file)
- [ ] `src/dashboard/app.py`

### 🧪 Tests (1 file)
- [ ] `tests/test_analysis.py`

### 📚 Documentation (3 files)
- [ ] `README.md`
- [ ] `INSTALL.md`
- [ ] `CHECKLIST.md` (this file)

### 🚀 Main scripts (3 files)
- [ ] `main.py`
- [ ] `quickstart.py`
- [ ] `setup.py`

### ⚙️ Configuration files (3 files)
- [ ] `requirements.txt`
- [ ] `.gitignore`
- [ ] `.env.example`

---

## 🎯 Quick Setup Steps

### Option 1: Tự động (Khuyến nghị)

```bash
# 1. Tạo thư mục
mkdir stock_analysis_system
cd stock_analysis_system

# 2. Copy tất cả files từ artifacts vào đây

# 3. Chạy setup
python setup.py

# 4. Test
python quickstart.py VNM
```

### Option 2: Thủ công

```bash
# 1. Tạo thư mục
mkdir stock_analysis_system
cd stock_analysis_system

# 2. Tạo cấu trúc
mkdir -p config data/{raw,processed,cache} logs notebooks tests
mkdir -p src/{data_pipeline,analysis,screener,portfolio,dashboard}

# 3. Tạo __init__.py
find . -type d -name "src" -o -name "config" -o -name "tests" | xargs -I {} touch {}/__init__.py
find src -type d | xargs -I {} touch {}/__init__.py

# 4. Copy từng file từ artifacts
# (Copy thủ công hoặc dùng script)

# 5. Cài requirements
pip install -r requirements.txt

# 6. Test
python -m pytest tests/
```

---

## 📋 Verification Checklist

### Cài đặt cơ bản
- [ ] Python 3.8+ đã cài
- [ ] pip đã cài và update
- [ ] Virtual environment (khuyến nghị)

### Dependencies
- [ ] vnstock3 cài thành công
- [ ] pandas, numpy cài thành công
- [ ] ta (technical analysis) cài thành công
- [ ] plotly cài thành công
- [ ] streamlit cài thành công

### Import test
```python
- [ ] from src.data_pipeline.price_data import PriceDataCrawler
- [ ] from src.analysis.technical import TechnicalAnalyzer
- [ ] from src.screener.fundamental_screener import StockScreener
- [ ] from src.portfolio.portfolio_manager import PortfolioManager
```

### Functional test
- [ ] Lấy được dữ liệu giá từ vnstock3
- [ ] Technical analysis chạy được
- [ ] Fundamental analysis chạy được
- [ ] Screener chạy được
- [ ] Portfolio manager hoạt động
- [ ] Dashboard khởi động được

### Commands test
- [ ] `python main.py screen -s VNM` chạy OK
- [ ] `python main.py analyze --symbol VNM` chạy OK
- [ ] `streamlit run src/dashboard/app.py` chạy OK
- [ ] `python quickstart.py VNM` chạy OK
- [ ] `pytest tests/` pass (hoặc ít nhất import OK)

---

## 🐛 Common Issues

### Issue: Module not found
**Solution:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Hoặc add vào ~/.bashrc
```

### Issue: vnstock3 lỗi
**Solution:**
```bash
pip install --upgrade pip setuptools
pip install vnstock3 --no-cache-dir
```

### Issue: Streamlit không chạy
**Solution:**
```bash
pip install --upgrade streamlit
streamlit run src/dashboard/app.py --server.port 8502
```

### Issue: Không lấy được dữ liệu
**Solution:**
- Check internet
- Wait và retry (rate limit)
- Clear cache: `rm -rf data/cache/*`

---

## 📊 File Count Summary

- **Total directories:** 12
- **__init__.py files:** 8
- **Python modules:** 17
- **Main scripts:** 3
- **Config files:** 3
- **Documentation:** 3
- **Tests:** 1

**Total files to create:** ~35 files

---

## ✅ Final Verification

Sau khi setup xong, chạy:

```bash
# 1. Structure check
ls -la config/ src/ data/ tests/

# 2. Import check
python -c "import src; print('✓ src package OK')"

# 3. Quick analysis
python quickstart.py VNM

# 4. Full test
python main.py screen -s VNM VCB HPG FPT

# 5. Dashboard
streamlit run src/dashboard/app.py
```

Nếu tất cả chạy OK → **🎉 DEPLOYMENT SUCCESSFUL!**

---

## 📞 Support

- Đọc `README.md` cho hướng dẫn chi tiết
- Đọc `INSTALL.md` cho troubleshooting
- Check `logs/system.log` cho errors
- Review code trong từng module

---

**Last updated:** 2025-10-03  
**Version:** 1.0.0