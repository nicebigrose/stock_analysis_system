"""
Module dinh gia co phieu (DCF, DDM, comparable)
Copy vao: src/analysis/valuation.py
"""
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockValuation:
    """Dinh gia co phieu bang nhieu phuong phap"""
    
    def __init__(self, risk_free_rate=0.05, market_return=0.12):
        """
        Args:
            risk_free_rate: Lai suat phi rui ro (trai phieu chinh phu VN ~5%)
            market_return: Loi nhuan ky vong thi truong (~12%)
        """
        self.risk_free_rate = risk_free_rate
        self.market_return = market_return
    
    def dcf_valuation(self, free_cash_flows, discount_rate, 
                      terminal_growth_rate=0.03):
        """
        DCF (Discounted Cash Flow) Valuation
        
        Args:
            free_cash_flows: List FCF du kien trong 5-10 nam
            discount_rate: Ty le chiet khau (WACC)
            terminal_growth_rate: Toc do tang truong vinh vien
            
        Returns:
            Enterprise Value
        """
        if not free_cash_flows:
            return None
        
        # PV cua FCF trong giai doan du bao
        pv_fcf = 0
        for i, fcf in enumerate(free_cash_flows, start=1):
            pv = fcf / ((1 + discount_rate) ** i)
            pv_fcf += pv
        
        # Terminal Value
        last_fcf = free_cash_flows[-1]
        terminal_value = (last_fcf * (1 + terminal_growth_rate)) / \
                        (discount_rate - terminal_growth_rate)
        
        # PV cua Terminal Value
        n = len(free_cash_flows)
        pv_terminal = terminal_value / ((1 + discount_rate) ** n)
        
        # Enterprise Value
        enterprise_value = pv_fcf + pv_terminal
        
        return {
            'enterprise_value': enterprise_value,
            'pv_fcf': pv_fcf,
            'terminal_value': terminal_value,
            'pv_terminal': pv_terminal
        }
    
    def pe_valuation(self, eps, industry_pe=None, growth_rate=None):
        """
        P/E Valuation
        
        Fair Value = EPS × Fair P/E
        """
        if industry_pe is None:
            # Dung PEG neu co growth rate
            if growth_rate:
                fair_pe = growth_rate * 100  # PEG = 1
            else:
                fair_pe = 15  # Default P/E
        else:
            fair_pe = industry_pe
        
        fair_value = eps * fair_pe
        
        return {
            'fair_value': fair_value,
            'fair_pe': fair_pe,
            'eps': eps
        }
    
    def pb_valuation(self, book_value_per_share, roe, required_return):
        """
        P/B Valuation
        
        Fair P/B = ROE / Required Return
        """
        fair_pb = roe / required_return
        fair_value = book_value_per_share * fair_pb
        
        return {
            'fair_value': fair_value,
            'fair_pb': fair_pb,
            'bvps': book_value_per_share
        }
    
    def ddm_valuation(self, dividend_per_share, growth_rate, required_return):
        """
        DDM (Dividend Discount Model) - Gordon Growth Model
        
        P0 = D1 / (r - g)
        """
        if required_return <= growth_rate:
            logger.warning("Required return must be > growth rate")
            return None
        
        next_dividend = dividend_per_share * (1 + growth_rate)
        intrinsic_value = next_dividend / (required_return - growth_rate)
        
        return intrinsic_value
    
    def comprehensive_valuation(self, ratios, growth_rate=0.10):
        """
        Dinh gia tong hop bang nhieu phuong phap
        
        Args:
            ratios: Dict chua cac chi so tai chinh
            growth_rate: Toc do tang truong ky vong
        """
        valuations = {}
        
        # P/E Valuation
        if ratios.get('eps'):
            pe_val = self.pe_valuation(
                ratios['eps'],
                growth_rate=growth_rate
            )
            valuations['pe_method'] = pe_val
        
        # P/B Valuation
        if ratios.get('bvps') and ratios.get('roe'):
            pb_val = self.pb_valuation(
                ratios['bvps'],
                ratios['roe'] / 100,
                self.market_return
            )
            valuations['pb_method'] = pb_val
        
        # Tinh gia tri trung binh
        fair_values = [v['fair_value'] for v in valuations.values() if v]
        
        if fair_values:
            avg_fair_value = np.mean(fair_values)
            median_fair_value = np.median(fair_values)
            
            return {
                'methods': valuations,
                'average_fair_value': avg_fair_value,
                'median_fair_value': median_fair_value,
                'current_price': ratios.get('current_price', 0),
                'upside_downside': ((avg_fair_value - ratios.get('current_price', 0)) / 
                                   ratios.get('current_price', 1) * 100) if ratios.get('current_price') else None
            }
        
        return None


# Example usage
if __name__ == "__main__":
    valuator = StockValuation()
    
    # DCF Example
    print("=== DCF Valuation ===")
    fcf_projections = [1000, 1100, 1210, 1331, 1464]  # Ty VND
    dcf_result = valuator.dcf_valuation(fcf_projections, discount_rate=0.10)
    print(f"Enterprise Value: {dcf_result['enterprise_value']:,.0f} VND")
    
    # P/E Example
    print("\n=== P/E Valuation ===")
    pe_result = valuator.pe_valuation(eps=5000, growth_rate=0.15)
    print(f"Fair Value: {pe_result['fair_value']:,.0f} VND")
    print(f"Fair P/E: {pe_result['fair_pe']:.1f}x")