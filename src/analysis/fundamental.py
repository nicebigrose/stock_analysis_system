"""
Module phân tích cơ bản
"""
import pandas as pd
import numpy as np
import logging
from config.settings import FUNDAMENTAL_CRITERIA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """Phân tích cơ bản cổ phiếu"""
    
    def __init__(self, criteria=None):
        self.criteria = criteria or FUNDAMENTAL_CRITERIA
    
    def score_stock(self, ratios: dict):
        """
        Chấm điểm cổ phiếu dựa trên các chỉ số cơ bản
        
        Args:
            ratios: dict chứa các chỉ số tài chính
            
        Returns:
            dict với score và lý do
        """
        score = 0
        max_score = 0
        reasons = []
        
        # ROE (Return on Equity)
        max_score += 10
        if ratios.get('roe'):
            roe = ratios['roe']
            if roe >= 20:
                score += 10
                reasons.append(f'ROE xuất sắc: {roe:.1f}%')
            elif roe >= 15:
                score += 7
                reasons.append(f'ROE tốt: {roe:.1f}%')
            elif roe >= 10:
                score += 4
                reasons.append(f'ROE trung bình: {roe:.1f}%')
            else:
                reasons.append(f'ROE thấp: {roe:.1f}%')
        
        # P/E Ratio
        max_score += 10
        if ratios.get('pe'):
            pe = ratios['pe']
            if 8 <= pe <= 15:
                score += 10
                reasons.append(f'P/E hấp dẫn: {pe:.1f}x')
            elif 15 < pe <= 20:
                score += 6
                reasons.append(f'P/E hợp lý: {pe:.1f}x')
            elif 5 <= pe < 8:
                score += 5
                reasons.append(f'P/E thấp (value trap?): {pe:.1f}x')
            elif pe > 25:
                reasons.append(f'P/E cao: {pe:.1f}x')
            else:
                score += 3
        
        # P/B Ratio
        max_score += 8
        if ratios.get('pb'):
            pb = ratios['pb']
            if pb < 1.5:
                score += 8
                reasons.append(f'P/B rất tốt: {pb:.2f}x')
            elif pb < 2.5:
                score += 5
                reasons.append(f'P/B hợp lý: {pb:.2f}x')
            elif pb < 4:
                score += 2
                reasons.append(f'P/B cao: {pb:.2f}x')
            else:
                reasons.append(f'P/B rất cao: {pb:.2f}x')
        
        # Debt to Equity
        max_score += 10
        if ratios.get('debt_to_equity') is not None:
            de = ratios['debt_to_equity']
            if de < 0.5:
                score += 10
                reasons.append(f'Nợ rất thấp: {de:.2f}x')
            elif de < 1:
                score += 7
                reasons.append(f'Nợ thấp: {de:.2f}x')
            elif de < 2:
                score += 4
                reasons.append(f'Nợ trung bình: {de:.2f}x')
            else:
                score += 1
                reasons.append(f'Nợ cao: {de:.2f}x')
        
        # ROA (Return on Assets)
        max_score += 7
        if ratios.get('roa'):
            roa = ratios['roa']
            if roa >= 10:
                score += 7
                reasons.append(f'ROA tốt: {roa:.1f}%')
            elif roa >= 5:
                score += 4
                reasons.append(f'ROA trung bình: {roa:.1f}%')
            else:
                score += 1
                reasons.append(f'ROA thấp: {roa:.1f}%')
        
        # Net Margin
        max_score += 8
        if ratios.get('net_margin'):
            margin = ratios['net_margin']
            if margin >= 15:
                score += 8
                reasons.append(f'Biên lợi nhuận cao: {margin:.1f}%')
            elif margin >= 10:
                score += 5
                reasons.append(f'Biên lợi nhuận tốt: {margin:.1f}%')
            elif margin >= 5:
                score += 2
                reasons.append(f'Biên lợi nhuận thấp: {margin:.1f}%')
        
        # Current Ratio (thanh khoản)
        max_score += 7
        if ratios.get('current_ratio'):
            cr = ratios['current_ratio']
            if 1.5 <= cr <= 3:
                score += 7
                reasons.append(f'Thanh khoản tốt: {cr:.2f}')
            elif 1 <= cr < 1.5:
                score += 4
                reasons.append(f'Thanh khoản ổn: {cr:.2f}')
            elif cr < 1:
                reasons.append(f'Thanh khoản yếu: {cr:.2f}')
            else:
                score += 3
                reasons.append(f'Thanh khoản dư thừa: {cr:.2f}')
        
        # Tính điểm phần trăm
        score_percentage = (score / max_score * 100) if max_score > 0 else 0
        
        # Phân loại
        if score_percentage >= 80:
            rating = 'EXCELLENT'
        elif score_percentage >= 65:
            rating = 'GOOD'
        elif score_percentage >= 50:
            rating = 'AVERAGE'
        elif score_percentage >= 35:
            rating = 'BELOW AVERAGE'
        else:
            rating = 'POOR'
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': score_percentage,
            'rating': rating,
            'reasons': reasons
        }
    
    def check_criteria(self, ratios: dict):
        """Kiểm tra xem cổ phiếu có đáp ứng tiêu chí sàng lọc không"""
        passed = []
        failed = []
        
        # ROE
        if ratios.get('roe'):
            if ratios['roe'] >= self.criteria['min_roe']:
                passed.append(f"ROE {ratios['roe']:.1f}% >= {self.criteria['min_roe']}%")
            else:
                failed.append(f"ROE {ratios['roe']:.1f}% < {self.criteria['min_roe']}%")
        
        # P/E
        if ratios.get('pe'):
            if ratios['pe'] <= self.criteria['max_pe'] and ratios['pe'] > 0:
                passed.append(f"P/E {ratios['pe']:.1f} <= {self.criteria['max_pe']}")
            else:
                failed.append(f"P/E {ratios['pe']:.1f} > {self.criteria['max_pe']}")
        
        # Debt/Equity
        if ratios.get('debt_to_equity') is not None:
            if ratios['debt_to_equity'] <= self.criteria['max_debt_to_equity']:
                passed.append(f"D/E {ratios['debt_to_equity']:.2f} <= {self.criteria['max_debt_to_equity']}")
            else:
                failed.append(f"D/E {ratios['debt_to_equity']:.2f} > {self.criteria['max_debt_to_equity']}")
        
        meets_criteria = len(failed) == 0 and len(passed) >= 2
        
        return {
            'meets_criteria': meets_criteria,
            'passed': passed,
            'failed': failed
        }
    
    def calculate_intrinsic_value_simple(self, ratios: dict, growth_rate: float = 0.1):
        """
        Tính giá trị nội tại đơn giản (PE-based)
        
        Args:
            ratios: Chỉ số tài chính
            growth_rate: Tốc độ tăng trưởng kỳ vọng (10% mặc định)
        """
        if not ratios.get('eps') or not ratios.get('pe'):
            return None
        
        eps = ratios['eps']
        industry_pe = ratios.get('pe', 15)  # Dùng PE hiện tại hoặc 15x
        
        # PEG ratio approach
        fair_pe = growth_rate * 100  # Ví dụ: 10% growth = PE 10x
        intrinsic_value = eps * fair_pe
        
        return {
            'intrinsic_value': intrinsic_value,
            'current_eps': eps,
            'fair_pe': fair_pe,
            'current_pe': industry_pe
        }
    
    def analyze_stock(self, ratios: dict, profile: dict = None, growth: dict = None):
        """
        Phan tich tong hop co ban mot co phieu
        
        Returns:
            dict voi day du phan tich
        """
        symbol = ratios.get('symbol', 'N/A')
        
        # Cham diem
        scoring = self.score_stock(ratios)
        
        # Kiem tra tieu chi
        criteria_check = self.check_criteria(ratios)
        
        # Dinh gia (optional)
        valuation = None
        try:
            valuation = self.calculate_intrinsic_value_simple(ratios)
        except:
            pass
        
        result = {
            'symbol': symbol,
            'ratios': ratios,
            'profile': profile if profile else {'symbol': symbol, 'company_name': symbol},
            'growth': growth if growth else {},
            'scoring': scoring,
            'criteria': criteria_check,
            'valuation': valuation,
            'recommendation': self._generate_recommendation(scoring, criteria_check, ratios)
        }
        
        return result
    
    def _generate_recommendation(self, scoring: dict, criteria: dict, ratios: dict):
        """Tạo khuyến nghị đầu tư"""
        rating = scoring['rating']
        meets_criteria = criteria['meets_criteria']
        
        if rating == 'EXCELLENT' and meets_criteria:
            action = 'STRONG BUY'
            note = 'Cổ phiếu có cơ bản xuất sắc, đáp ứng tất cả tiêu chí'
        elif rating in ['EXCELLENT', 'GOOD'] and meets_criteria:
            action = 'BUY'
            note = 'Cổ phiếu có cơ bản tốt, đáng để mua'
        elif rating == 'AVERAGE':
            action = 'HOLD'
            note = 'Cổ phiếu có cơ bản trung bình, theo dõi thêm'
        elif rating == 'BELOW AVERAGE':
            action = 'AVOID'
            note = 'Cổ phiếu có cơ bản yếu, nên tránh'
        else:
            action = 'SELL'
            note = 'Cổ phiếu có cơ bản kém, nên bán nếu đang nắm giữ'
        
        return {
            'action': action,
            'note': note,
            'confidence': scoring['percentage']
        }


# Example usage
if __name__ == "__main__":
    # Test với dữ liệu giả định
    test_ratios = {
        'symbol': 'VNM',
        'roe': 25.5,
        'roa': 12.3,
        'pe': 14.5,
        'pb': 3.2,
        'debt_to_equity': 0.45,
        'net_margin': 18.5,
        'current_ratio': 2.1,
        'eps': 5200
    }
    
    analyzer = FundamentalAnalyzer()
    result = analyzer.analyze_stock(test_ratios)
    
    print(f"\n{'='*60}")
    print(f"Fundamental Analysis for {result['symbol']}")
    print(f"{'='*60}")
    print(f"\nRating: {result['scoring']['rating']}")
    print(f"Score: {result['scoring']['percentage']:.1f}%")
    print(f"\nRecommendation: {result['recommendation']['action']}")
    print(f"Note: {result['recommendation']['note']}")
    print(f"\nReasons:")
    for reason in result['scoring']['reasons']:
        print(f"  - {reason}")