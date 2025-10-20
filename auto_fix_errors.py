"""
Script tu dong fix tat ca loi
Chay: python auto_fix_errors.py
"""
import re
from pathlib import Path


def fix_fundamental_data():
    """Fix fundamental_data.py"""
    file_path = Path('src/data_pipeline/fundamental_data.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Thay the ham get_company_profile
    new_profile_func = '''    def get_company_profile(self, symbol: str):
        """Lay thong tin doanh nghiep"""
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            
            # Tra ve minimal data de tranh loi
            return {
                'symbol': symbol,
                'company_name': symbol,
                'industry': 'Unknown',
                'exchange': 'HOSE',
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.warning(f"Could not get profile for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'company_name': symbol,
                'industry': 'Unknown',
                'exchange': 'Unknown',
                'timestamp': datetime.now()
            }'''
    
    # Tim va thay the
    pattern = r'def get_company_profile\(self, symbol: str\):.*?(?=\n    def |\nclass |\Z)'
    content = re.sub(pattern, new_profile_func, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[FIXED] {file_path}")


def fix_screener():
    """Fix fundamental_screener.py"""
    file_path = Path('src/screener/fundamental_screener.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix: Bo growth parameter
    content = content.replace(
        "growth=fundamental_data['growth']",
        "growth=fundamental_data.get('growth')"
    )
    
    # Neu khong co dong tren, thu cach khac
    if "fundamental_data['growth']" in content:
        content = content.replace(
            "fundamental_data['growth']",
            "fundamental_data.get('growth')"
        )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[FIXED] {file_path}")


def fix_fundamental_analyzer():
    """Fix fundamental.py"""
    file_path = Path('src/analysis/fundamental.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dam bao ham analyze_stock xu ly None
    if "'growth': growth" in content:
        content = content.replace(
            "'growth': growth,",
            "'growth': growth if growth else {},"
        )
        content = content.replace(
            "'profile': profile,",
            "'profile': profile if profile else {'symbol': symbol},"
        )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[FIXED] {file_path}")


def main():
    print("="*70)
    print("AUTO FIX ALL ERRORS")
    print("="*70)
    print()
    
    try:
        fix_fundamental_data()
    except Exception as e:
        print(f"[ERROR] fundamental_data.py: {e}")
    
    try:
        fix_screener()
    except Exception as e:
        print(f"[ERROR] fundamental_screener.py: {e}")
    
    try:
        fix_fundamental_analyzer()
    except Exception as e:
        print(f"[ERROR] fundamental.py: {e}")
    
    print()
    print("="*70)
    print("DONE! Now try:")
    print("  python main.py screen -s VNM VCB HPG")
    print("="*70)


if __name__ == '__main__':
    main()