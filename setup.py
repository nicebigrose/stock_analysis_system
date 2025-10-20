"""
Script setup tự động cho Stock Analysis System

Chạy: python setup.py
"""
import os
import sys
from pathlib import Path
import subprocess


def create_directory_structure():
    """Tạo cấu trúc thư mục"""
    print("📁 Creating directory structure...")
    
    directories = [
        'config',
        'data/raw',
        'data/processed',
        'data/cache',
        'src/data_pipeline',
        'src/analysis',
        'src/screener',
        'src/portfolio',
        'src/dashboard',
        'logs',
        'notebooks',
        'tests'
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print("✅ Directory structure created!\n")


def create_init_files():
    """Tạo __init__.py files"""
    print("📝 Creating __init__.py files...")
    
    init_configs = {
        'config/__init__.py': '"""Configuration package"""',
        'src/__init__.py': '"""Source package"""',
        'src/data_pipeline/__init__.py': '''"""Data pipeline package"""
from .price_data import PriceDataCrawler
from .fundamental_data import FundamentalDataCrawler

__all__ = ["PriceDataCrawler", "FundamentalDataCrawler"]
''',
        'src/analysis/__init__.py': '''"""Analysis package"""
from .technical import TechnicalAnalyzer
from .fundamental import FundamentalAnalyzer

__all__ = ["TechnicalAnalyzer", "FundamentalAnalyzer"]
''',
        'src/screener/__init__.py': '''"""Screener package"""
from .fundamental_screener import StockScreener

__all__ = ["StockScreener"]
''',
        'src/portfolio/__init__.py': '''"""Portfolio package"""
from .portfolio_manager import PortfolioManager

__all__ = ["PortfolioManager"]
''',
        'src/dashboard/__init__.py': '"""Dashboard package"""',
        'tests/__init__.py': '"""Tests package"""'
    }
    
    for filepath, content in init_configs.items():
        path = Path(filepath)
        if not path.exists():
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {filepath}")
    
    print("✅ __init__.py files created!\n")


def create_requirements_file():
    """Tạo requirements.txt"""
    print("📦 Creating requirements.txt...")
    
    requirements = """# Core data & analysis
vnstock>=0.1.0
pandas>=2.0.0
numpy>=1.24.0

# Web scraping
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Technical analysis
ta>=0.11.0

# Visualization
plotly>=5.18.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Dashboard
streamlit>=1.29.0

# Data storage
openpyxl>=3.1.0
sqlalchemy>=2.0.0

# Scheduling
APScheduler>=3.10.0

# Utilities
python-dotenv>=1.0.0
pytz>=2023.3

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("  ✓ requirements.txt")
    print("✅ Requirements file created!\n")


def install_requirements():
    """Cài đặt requirements"""
    print("📥 Installing requirements...")
    print("This may take a few minutes...\n")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("\n✅ Requirements installed successfully!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing requirements: {e}")
        print("Please install manually: pip install -r requirements.txt\n")
        return False


def create_env_file():
    """Tạo .env file mẫu"""
    print("⚙️  Creating .env.example...")
    
    env_content = """# Stock Analysis System Configuration

# Data sources
DATA_SOURCE=vnstock

# Portfolio settings
INITIAL_CASH=100000000

# Risk settings
RISK_FREE_RATE=0.05
MAX_POSITION_SIZE=0.20

# Update schedule
AUTO_UPDATE=true
UPDATE_TIME=15:30

# Alerts (optional)
# TELEGRAM_BOT_TOKEN=your_token_here
# TELEGRAM_CHAT_ID=your_chat_id
# EMAIL_ALERTS=false
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("  ✓ .env.example")
    print("  📝 Copy to .env and customize if needed")
    print("✅ Environment file created!\n")


def create_gitignore():
    """Tạo .gitignore"""
    print("🔒 Creating .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Data files
data/raw/*
data/processed/*
data/cache/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/cache/.gitkeep

# Logs
logs/*
*.log
!logs/.gitkeep

# Portfolio (SENSITIVE!)
portfolio.json
portfolio_backup.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Jupyter
.ipynb_checkpoints/
notebooks/.ipynb_checkpoints/

# Test coverage
.coverage
htmlcov/

# Build
build/
dist/
*.egg-info/
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    # Tạo .gitkeep files
    for dir_path in ['data/raw', 'data/processed', 'data/cache', 'logs']:
        gitkeep = Path(dir_path) / '.gitkeep'
        gitkeep.touch()
    
    print("  ✓ .gitignore")
    print("✅ Git configuration created!\n")


def run_tests():
    """Chạy tests để verify installation"""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ All tests passed!\n")
        else:
            print("⚠️  Some tests failed. Check output above.\n")
    except Exception as e:
        print(f"ℹ️  Could not run tests: {e}")
        print("You can run tests manually with: pytest tests/\n")


def print_next_steps():
    """In hướng dẫn tiếp theo"""
    print("\n" + "="*70)
    print("🎉 SETUP COMPLETE!")
    print("="*70)
    
    print("""
📚 NEXT STEPS:

1. Test the system:
   python main.py screen -s VNM VCB HPG

2. Analyze a specific stock:
   python main.py analyze --symbol VNM

3. Start the dashboard:
   streamlit run src/dashboard/app.py
   # Or: python main.py dashboard

4. Setup your portfolio:
   python
   >>> from src.portfolio.portfolio_manager import PortfolioManager
   >>> pm = PortfolioManager()
   >>> pm.add_cash(100_000_000)  # Add 100 million VND

5. Run tests:
   pytest tests/ -v

6. Schedule auto-updates:
   python
   >>> from src.data_pipeline.data_updater import DataUpdater
   >>> updater = DataUpdater()
   >>> updater.start()

📖 DOCUMENTATION:
   - Read README.md for detailed guide
   - Check config/settings.py for customization
   - Explore notebooks/ for examples

⚠️  IMPORTANT:
   - This is for EDUCATIONAL purposes only
   - NOT financial advice
   - Test with small amounts first
   - Always do your own research (DYOR)

🐛 Issues? Check:
   - GitHub Issues (if available)
   - Logs in logs/system.log
   - Run: python -m pytest tests/ -v

🚀 Happy Investing!
""")
    print("="*70 + "\n")


def main():
    """Main setup function"""
    print("\n" + "="*70)
    print("📈 VIETNAM STOCK ANALYSIS SYSTEM - SETUP")
    print("="*70 + "\n")
    
    # Step 1: Create directories
    create_directory_structure()
    
    # Step 2: Create __init__ files
    create_init_files()
    
    # Step 3: Create requirements
    create_requirements_file()
    
    # Step 4: Create env file
    create_env_file()
    
    # Step 5: Create gitignore
    create_gitignore()
    
    # Step 6: Install requirements
    print("Would you like to install requirements now? (y/n): ", end='')
    install_now = input().lower().strip()
    
    if install_now == 'y':
        install_success = install_requirements()
        
        if install_success:
            # Step 7: Run tests
            print("Would you like to run tests? (y/n): ", end='')
            run_tests_now = input().lower().strip()
            
            if run_tests_now == 'y':
                run_tests()
    else:
        print("\n⚠️  Remember to install requirements:")
        print("   pip install -r requirements.txt\n")
    
    # Step 8: Print next steps
    print_next_steps()
    
    # Create a quick start script
    create_quickstart_script()


def create_quickstart_script():
    """Tạo script quick start"""
    print("📝 Creating quick start script...")
    
    quickstart = """#!/usr/bin/env python
\"\"\"
Quick start script - Chạy ví dụ nhanh
\"\"\"
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data_pipeline.price_data import PriceDataCrawler
from src.analysis.technical import TechnicalAnalyzer
from src.analysis.fundamental import FundamentalAnalyzer
from src.data_pipeline.fundamental_data import FundamentalDataCrawler


def quick_analysis(symbol='VNM'):
    \"\"\"Phân tích nhanh 1 mã\"\"\"
    print(f"\\n{'='*60}")
    print(f"QUICK ANALYSIS: {symbol}")
    print(f"{'='*60}\\n")
    
    # 1. Get price data
    print("1. Fetching price data...")
    price_crawler = PriceDataCrawler()
    df = price_crawler.get_historical_data(symbol, start_date='2024-01-01')
    
    if df.empty:
        print(f"❌ No data for {symbol}")
        return
    
    print(f"✓ Got {len(df)} days of data\\n")
    
    # 2. Technical analysis
    print("2. Running technical analysis...")
    tech = TechnicalAnalyzer()
    tech_result = tech.analyze_stock(df, symbol)
    
    print(f"   Close: {tech_result['close']:,.0f} VND")
    print(f"   RSI: {tech_result['rsi']:.1f}")
    print(f"   Signal: {tech_result['signals']['signal']}")
    print(f"   Trend: {tech_result['trend']['medium_term']}\\n")
    
    # 3. Fundamental analysis
    print("3. Running fundamental analysis...")
    fund_crawler = FundamentalDataCrawler()
    ratios = fund_crawler.get_financial_ratios(symbol)
    
    if ratios:
        fund = FundamentalAnalyzer()
        fund_result = fund.analyze_stock(ratios)
        
        print(f"   Rating: {fund_result['scoring']['rating']}")
        print(f"   ROE: {ratios.get('roe', 0):.1f}%")
        print(f"   P/E: {ratios.get('pe', 0):.1f}x")
        print(f"   Recommendation: {fund_result['recommendation']['action']}\\n")
    
    print(f"{'='*60}\\n")
    print(f"💡 For detailed analysis, use:")
    print(f"   python main.py analyze --symbol {symbol}")
    print(f"\\n📊 Or start dashboard:")
    print(f"   streamlit run src/dashboard/app.py")


if __name__ == '__main__':
    # Get symbol from command line or use default
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'VNM'
    
    try:
        quick_analysis(symbol)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\\nMake sure you have installed requirements:")
        print("   pip install -r requirements.txt")
"""
    
    with open('quickstart.py', 'w', encoding='utf-8') as f:
        f.write(quickstart)
    
    # Make executable on Unix
    if sys.platform != 'win32':
        os.chmod('quickstart.py', 0o755)
    
    print("  ✓ quickstart.py")
    print("  📝 Run: python quickstart.py [SYMBOL]")
    print("✅ Quick start script created!\n")


if __name__ == '__main__':
    main()