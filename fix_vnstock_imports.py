"""
Script tự động sửa tất cả import vnstock -> vnstock
Chạy: python fix_vnstock_imports.py
"""
import os
from pathlib import Path

def fix_imports_in_file(filepath):
    """Sửa import trong 1 file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Thay thế
        original = content
        content = content.replace('from vnstock import', 'from vnstock import')
        content = content.replace('import vnstock', 'import vnstock')
        content = content.replace('vnstock', 'vnstock')
        
        # Chỉ ghi nếu có thay đổi
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[FIXED] {filepath}")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

def main():
    print("="*70)
    print("FIX VNSTOCK3 -> VNSTOCK")
    print("="*70)
    print()
    
    # Tìm tất cả file .py
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip __pycache__ và venv
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    print(f"Found {len(python_files)} Python files")
    print()
    
    fixed_count = 0
    for filepath in python_files:
        if fix_imports_in_file(filepath):
            fixed_count += 1
    
    print()
    print("="*70)
    print(f"DONE! Fixed {fixed_count} files")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Cài vnstock mới: pip uninstall vnstock -y && pip install vnstock --upgrade")
    print("2. Test: python quickstart.py VNM")

if __name__ == '__main__':
    main()