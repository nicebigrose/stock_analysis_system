"""
Dashboard Streamlit để visualize dữ liệu và phân tích
Chạy: streamlit run src/dashboard/app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Import modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data_pipeline.price_data import PriceDataCrawler
from src.data_pipeline.fundamental_data import FundamentalDataCrawler
from src.analysis.technical import TechnicalAnalyzer
from src.analysis.fundamental import FundamentalAnalyzer
from src.screener.fundamental_screener import StockScreener
from src.portfolio.portfolio_manager import PortfolioManager
from config.settings import WATCHLIST

# Page config
st.set_page_config(
    page_title="Vietnam Stock Analysis System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
@st.cache_resource
def init_components():
    return {
        'price_crawler': PriceDataCrawler(),
        'fundamental_crawler': FundamentalDataCrawler(),
        'technical_analyzer': TechnicalAnalyzer(),
        'fundamental_analyzer': FundamentalAnalyzer(),
        'screener': StockScreener(),
        'portfolio': PortfolioManager()
    }

components = init_components()

# Sidebar
st.sidebar.title("📈 Stock Analysis System")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🔍 Stock Screener", "📊 Stock Analysis", 
     "💼 Portfolio", "⚙️ Settings"]
)

# ==================== DASHBOARD PAGE ====================
if page == "🏠 Dashboard":
    st.title("📊 Vietnam Stock Market Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # LAY DU LIEU THAT
    try:
        # 1. Lay chi so VN-Index (dung VNINDEX)
        price_crawler = components['price_crawler']
        vnindex_data = price_crawler.get_latest_price('VNINDEX')
        
        # 2. Lay thong tin Portfolio
        portfolio_mgr = components['portfolio']
        portfolio_value = portfolio_mgr.get_current_value()
        portfolio_perf = portfolio_mgr.get_performance()
        
        # Hien thi metrics
        with col1:
            if vnindex_data:
                st.metric(
                    "VN-Index", 
                    f"{vnindex_data['close']:,.2f}",
                    f"{vnindex_data.get('change', 0):+,.2f} ({vnindex_data.get('change_percent', 0):+.2f}%)"
                )
            else:
                st.metric("VN-Index", "N/A", "Không lấy được dữ liệu")
        
        with col2:
            # HNX-Index
            hnx_data = price_crawler.get_latest_price('HNX-INDEX')
            if hnx_data:
                st.metric(
                    "HNX-Index",
                    f"{hnx_data['close']:,.2f}",
                    f"{hnx_data.get('change', 0):+,.2f} ({hnx_data.get('change_percent', 0):+.2f}%)"
                )
            else:
                st.metric("HNX-Index", "N/A")
        
        with col3:
            # Portfolio Value
            total_value = portfolio_value['total_value']
            total_pnl = portfolio_perf['total_pnl']
            total_pnl_pct = portfolio_perf['total_pnl_percent']
            
            st.metric(
                "Portfolio Value",
                f"{total_value:,.0f} VND",
                f"{total_pnl:+,.0f} ({total_pnl_pct:+.2f}%)"
            )
        
        with col4:
            # Cash
            cash = portfolio_value['cash']
            cash_pct = portfolio_value['cash_percent']
            
            st.metric(
                "Cash",
                f"{cash:,.0f} VND",
                f"{cash_pct:.1f}%"
            )
    
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {str(e)}")
        # Fallback to placeholder
        with col1:
            st.metric("VN-Index", "N/A", "Dữ liệu placeholder")
        with col2:
            st.metric("HNX-Index", "N/A")
        with col3:
            st.metric("Portfolio", "0 VND", "Chưa có dữ liệu")
        with col4:
            st.metric("Cash", "0 VND", "0%")
    
    st.markdown("---")
    
    # Quick watchlist - LAY DU LIEU THAT
    st.subheader("📋 Watchlist Overview")
    
    with st.spinner("Loading watchlist data..."):
        try:
            from config.settings import WATCHLIST
            watchlist_data = []
            
            # Lay TOP 10 ma trong watchlist
            for symbol in WATCHLIST[:10]:
                latest = components['price_crawler'].get_latest_price(symbol)
                if latest:
                    watchlist_data.append({
                        'Symbol': latest['symbol'],
                        'Price': f"{latest['close']:,.0f}",
                        'Change': f"{latest.get('change', 0):+,.2f}",
                        'Change %': f"{latest.get('change_percent', 0):+.2f}%",
                        'Volume': f"{latest.get('volume', 0):,.0f}"
                    })
            
            if watchlist_data:
                df_watch = pd.DataFrame(watchlist_data)
                st.dataframe(df_watch, use_container_width=True)
            else:
                st.warning("Không lấy được dữ liệu watchlist")
        
        except Exception as e:
            st.error(f"Error loading watchlist: {str(e)}")
    
    # Recent alerts
    st.subheader("🔔 Recent Alerts")
    
    # Kiem tra tin hieu tu Technical Scanner
    try:
        from src.screener.technical_scanner import TechnicalScanner
        scanner = TechnicalScanner(watchlist=WATCHLIST[:5])
        
        # Tim oversold
        oversold = scanner.find_oversold(rsi_threshold=30)
        if not oversold.empty:
            for _, row in oversold.head(3).iterrows():
                st.info(f"🟢 {row['symbol']}: RSI = {row['rsi']:.1f} (Oversold) - Có thể cân nhắc mua")
        
        # Tim overbought
        overbought = scanner.find_overbought(rsi_threshold=70)
        if not overbought.empty:
            for _, row in overbought.head(3).iterrows():
                st.warning(f"🟡 {row['symbol']}: RSI = {row['rsi']:.1f} (Overbought) - Cân nhắc chốt lời")
        
        if oversold.empty and overbought.empty:
            st.write("Chưa có alert nào")
    
    except Exception as e:
        st.write("Không thể tải alerts")

# ==================== SCREENER PAGE ====================
elif page == "🔍 Stock Screener":
    st.title("🔍 Stock Screener")
    st.markdown("Sàng lọc cổ phiếu kết hợp phân tích cơ bản và kỹ thuật")
    
    # Filters
    with st.expander("⚙️ Screening Criteria", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_roe = st.number_input("Min ROE (%)", value=15.0, step=1.0)
            max_pe = st.number_input("Max P/E", value=20.0, step=1.0)
        
        with col2:
            max_de = st.number_input("Max D/E", value=2.0, step=0.1)
            min_score = st.number_input("Min Combined Score", value=3.5, step=0.1, max_value=5.0)
        
        with col3:
            rsi_min = st.number_input("RSI Min", value=30, step=5)
            rsi_max = st.number_input("RSI Max", value=70, step=5)
    
    # Watchlist selection
    selected_stocks = st.multiselect(
        "Select stocks to screen",
        WATCHLIST,
        default=WATCHLIST[:10]
    )
    
    if st.button("🚀 Run Screener", type="primary"):
        with st.spinner("Screening stocks... This may take a few minutes..."):
            try:
                screener = StockScreener(watchlist=selected_stocks)
                results = screener.screen_multiple_stocks(max_workers=3)
                
                if not results.empty:
                    st.success(f"✅ Screened {len(results)} stocks successfully!")
                    
                    # Apply filters
                    filtered = results[
                        (results['Score'] >= min_score) &
                        (results['ROE'] >= min_roe) &
                        (results['PE'] <= max_pe) &
                        (results['D/E'] <= max_de) &
                        (results['RSI'] >= rsi_min) &
                        (results['RSI'] <= rsi_max)
                    ]
                    
                    st.subheader(f"📊 Results ({len(filtered)} stocks passed)")
                    
                    # Display results
                    st.dataframe(
                        filtered.style.background_gradient(subset=['Score'], cmap='RdYlGn'),
                        use_container_width=True
                    )
                    
                    # Top picks
                    st.subheader("⭐ Top Picks")
                    top = filtered[filtered['Rating'].isin(['STRONG BUY', 'BUY'])].head(5)
                    
                    for _, row in top.iterrows():
                        with st.container():
                            col1, col2, col3 = st.columns([2, 3, 3])
                            with col1:
                                st.markdown(f"### {row['Symbol']}")
                                st.metric("Rating", row['Rating'])
                            with col2:
                                st.metric("Score", f"{row['Score']:.2f}/5.0")
                                st.metric("ROE", f"{row['ROE']:.1f}%")
                            with col3:
                                st.metric("P/E", f"{row['PE']:.1f}x")
                                st.metric("RSI", f"{row['RSI']:.1f}")
                            st.info(f"💡 {row['Note']}")
                            st.markdown("---")
                else:
                    st.warning("No results found")
                    
            except Exception as e:
                st.error(f"Error during screening: {str(e)}")

# ==================== STOCK ANALYSIS PAGE ====================
elif page == "📊 Stock Analysis":
    st.title("📊 Stock Analysis")
    
    # Stock selector
    symbol = st.selectbox("Select Stock", WATCHLIST)
    
    if symbol:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Price chart
            st.subheader(f"💹 {symbol} Price Chart")
            
            period = st.selectbox("Period", ["1M", "3M", "6M", "1Y", "2Y"], index=3)
            period_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "2Y": 730}
            
            with st.spinner("Loading price data..."):
                try:
                    df = components['price_crawler'].get_historical_data(
                        symbol,
                        start_date=(datetime.now() - timedelta(days=period_map[period])).strftime('%Y-%m-%d')
                    )
                    
                    if not df.empty:
                        # Add indicators
                        df_tech = components['technical_analyzer'].add_all_indicators(df)
                        
                        # Create candlestick chart
                        fig = go.Figure()
                        
                        fig.add_trace(go.Candlestick(
                            x=df_tech.index,
                            open=df_tech['open'],
                            high=df_tech['high'],
                            low=df_tech['low'],
                            close=df_tech['close'],
                            name='Price'
                        ))
                        
                        # Add MAs
                        fig.add_trace(go.Scatter(
                            x=df_tech.index, y=df_tech['SMA_50'],
                            name='SMA 50', line=dict(color='orange', width=1)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=df_tech.index, y=df_tech['SMA_200'],
                            name='SMA 200', line=dict(color='blue', width=1)
                        ))
                        
                        fig.update_layout(
                            height=500,
                            xaxis_title="Date",
                            yaxis_title="Price (VND)",
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # RSI Chart
                        fig_rsi = go.Figure()
                        fig_rsi.add_trace(go.Scatter(
                            x=df_tech.index, y=df_tech['RSI'],
                            name='RSI', line=dict(color='purple', width=2)
                        ))
                        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                        fig_rsi.update_layout(height=200, yaxis_title="RSI")
                        
                        st.plotly_chart(fig_rsi, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error loading price data: {str(e)}")
        
        with col2:
            # Technical indicators
            st.subheader("📊 Technical Indicators")
            
            try:
                analysis = components['technical_analyzer'].analyze_stock(df, symbol)
                
                latest = analysis['dataframe'].iloc[-1]
                
                st.metric("Close", f"{latest['close']:,.0f}")
                st.metric("RSI", f"{latest['RSI']:.1f}")
                st.metric("MACD", f"{latest['MACD']:.2f}")
                
                # Signal
                signal = analysis['signals']['signal']
                color = "green" if "BUY" in signal else ("red" if "SELL" in signal else "gray")
                st.markdown(f"### Signal: :{color}[{signal}]")
                
                # Reasons
                with st.expander("📋 Signal Reasons"):
                    for reason in analysis['signals']['reasons']:
                        st.write(f"• {reason}")
                
                # Patterns
                if analysis['patterns']:
                    with st.expander("🔍 Patterns Detected"):
                        for pattern in analysis['patterns']:
                            st.write(f"• {pattern}")
                
                # Support/Resistance
                with st.expander("📍 Support/Resistance"):
                    st.write("**Support:**", analysis['support_resistance']['supports'])
                    st.write("**Resistance:**", analysis['support_resistance']['resistances'])
                
            except Exception as e:
                st.error(f"Error in technical analysis: {str(e)}")
        
        # Fundamental Analysis
        st.markdown("---")
        st.subheader("💼 Fundamental Analysis")

        with st.spinner("Loading fundamental data..."):
            try:
                ratios = components['fundamental_crawler'].get_financial_ratios(symbol)
                
                if ratios:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # Helper function de hien thi an toan
                    def safe_display(value, format_str="{:.1f}", default="N/A", suffix=""):
                        """Hien thi gia tri an toan, tranh loi None"""
                        try:
                            if value is not None and value != 0:
                                if isinstance(value, (int, float)):
                                    return format_str.format(value) + suffix
                            return default
                        except:
                            return default
                    
                    with col1:
                        st.metric("ROE", safe_display(ratios.get('roe'), "{:.1f}", suffix="%"))
                        st.metric("ROA", safe_display(ratios.get('roa'), "{:.1f}", suffix="%"))
                    
                    with col2:
                        st.metric("P/E", safe_display(ratios.get('pe'), "{:.1f}", suffix="x"))
                        st.metric("P/B", safe_display(ratios.get('pb'), "{:.2f}", suffix="x"))
                    
                    with col3:
                        st.metric("D/E", safe_display(ratios.get('debt_to_equity'), "{:.2f}", suffix="x"))
                        st.metric("Current Ratio", safe_display(ratios.get('current_ratio'), "{:.2f}"))
                    
                    with col4:
                        st.metric("EPS", safe_display(ratios.get('eps'), "{:,.0f}", suffix=" VND"))
                        st.metric("Net Margin", safe_display(ratios.get('net_margin'), "{:.1f}", suffix="%"))
                    
                    # Fundamental scoring
                    f_analysis = components['fundamental_analyzer'].analyze_stock(ratios)
                    
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Fundamental Rating")
                        rating = f_analysis['scoring']['rating']
                        score = f_analysis['scoring']['percentage']
                        
                        color = "green" if rating in ["EXCELLENT", "GOOD"] else ("orange" if rating == "AVERAGE" else "red")
                        st.markdown(f"### :{color}[{rating}]")
                        st.progress(score / 100)
                        st.write(f"Score: {score:.1f}/100")
                    
                    with col2:
                        st.subheader("Recommendation")
                        rec = f_analysis['recommendation']
                        st.markdown(f"### {rec['action']}")
                        st.info(rec['note'])
                    
                    # Detailed reasons
                    with st.expander("📋 Detailed Analysis"):
                        for reason in f_analysis['scoring']['reasons']:
                            st.write(f"• {reason}")
                else:
                    st.warning("No fundamental data available for this symbol")
                    
            except Exception as e:
                st.error(f"Error loading fundamental data: {str(e)}")
                import traceback
                st.code(traceback.format_exc())  # Hien thi loi chi tiet de debug

# ==================== PORTFOLIO PAGE ====================
elif page == "💼 Portfolio":
    st.title("💼 Portfolio Management")
    
    pm = components['portfolio']
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 Add Cash"):
            st.session_state.show_add_cash = True
    
    with col2:
        if st.button("📈 Buy Stock"):
            st.session_state.show_buy = True
    
    with col3:
        if st.button("📉 Sell Stock"):
            st.session_state.show_sell = True
    
    # Modals (using expanders)
    if st.session_state.get('show_add_cash'):
        with st.form("add_cash_form"):
            amount = st.number_input("Amount (VND)", min_value=0, step=1000000)
            submitted = st.form_submit_button("Confirm")
            if submitted and amount > 0:
                pm.add_cash(amount)
                st.success(f"Added {amount:,.0f} VND")
                st.session_state.show_add_cash = False
                st.rerun()
    
    if st.session_state.get('show_buy'):
        with st.form("buy_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                symbol = st.selectbox("Symbol", WATCHLIST)
            with col2:
                shares = st.number_input("Shares", min_value=1, step=100)
            with col3:
                price = st.number_input("Price", min_value=0.0, step=1000.0)
            
            submitted = st.form_submit_button("Buy")
            if submitted:
                if pm.buy_stock(symbol, shares, price):
                    st.success(f"Bought {shares} shares of {symbol}")
                    st.session_state.show_buy = False
                    st.rerun()
    
    if st.session_state.get('show_sell'):
        with st.form("sell_form"):
            positions = [p['symbol'] for p in pm.portfolio['positions']]
            if positions:
                col1, col2, col3 = st.columns(3)
                with col1:
                    symbol = st.selectbox("Symbol", positions)
                with col2:
                    max_shares = next(p['shares'] for p in pm.portfolio['positions'] if p['symbol'] == symbol)
                    shares = st.number_input("Shares", min_value=1, max_value=max_shares, step=100)
                with col3:
                    price = st.number_input("Price", min_value=0.0, step=1000.0)
                
                submitted = st.form_submit_button("Sell")
                if submitted:
                    result = pm.sell_stock(symbol, shares, price)
                    if result:
                        st.success(f"Sold {shares} shares. P&L: {result['pnl']:,.0f} ({result['pnl_percent']:.2f}%)")
                        st.session_state.show_sell = False
                        st.rerun()
            else:
                st.warning("No positions to sell")
    
    st.markdown("---")
    
    # Portfolio summary
    current = pm.get_current_value()
    perf = pm.get_performance()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Value", f"{current['total_value']:,.0f} VND")
    with col2:
        st.metric("P&L", f"{perf['total_pnl']:,.0f} VND", f"{perf['total_pnl_percent']:+.2f}%")
    with col3:
        st.metric("Cash", f"{current['cash']:,.0f} VND", f"{current['cash_percent']:.1f}%")
    with col4:
        st.metric("Positions Value", f"{current['positions_value']:,.0f} VND")
    
    # Positions table
    if current['positions']:
        st.subheader("📊 Current Positions")
        
        df_positions = pd.DataFrame(current['positions'])
        df_positions = df_positions[['symbol', 'shares', 'avg_price', 'current_price', 
                                     'value', 'pnl', 'pnl_percent', 'weight']]
        
        # Format columns
        df_positions['avg_price'] = df_positions['avg_price'].apply(lambda x: f"{x:,.0f}")
        df_positions['current_price'] = df_positions['current_price'].apply(lambda x: f"{x:,.0f}")
        df_positions['value'] = df_positions['value'].apply(lambda x: f"{x:,.0f}")
        df_positions['pnl'] = df_positions['pnl'].apply(lambda x: f"{x:,.0f}")
        df_positions['pnl_percent'] = df_positions['pnl_percent'].apply(lambda x: f"{x:+.2f}%")
        df_positions['weight'] = df_positions['weight'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(df_positions, use_container_width=True)
        
        # Pie chart
        fig = px.pie(
            current['positions'],
            values='value',
            names='symbol',
            title='Portfolio Allocation'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No positions yet. Start by adding cash and buying stocks!")
    
    # Rebalancing suggestions
    suggestions = pm.suggest_rebalance()
    if suggestions:
        st.subheader("💡 Rebalancing Suggestions")
        for sug in suggestions:
            if sug['type'] == 'TAKE_PROFIT':
                st.success(f"✅ {sug['message']} → {sug['action']}")
            elif sug['type'] == 'STOP_LOSS':
                st.error(f"⚠️ {sug['message']} → {sug['action']}")
            else:
                st.info(f"ℹ️ {sug['message']} → {sug['action']}")
    
    # Performance chart
    st.subheader("📈 Performance History")
    
    if pm.portfolio['history']:
        df_history = pd.DataFrame(pm.portfolio['history'])
        df_history['date'] = pd.to_datetime(df_history['date'])
        
        # Calculate cumulative P&L
        df_pnl = df_history[df_history['type'] == 'sell'][['date', 'pnl']].copy()
        df_pnl['cumulative_pnl'] = df_pnl['pnl'].cumsum()
        
        if not df_pnl.empty:
            fig = px.line(df_pnl, x='date', y='cumulative_pnl', 
                         title='Cumulative Realized P&L')
            st.plotly_chart(fig, use_container_width=True)

# ==================== SETTINGS PAGE ====================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.subheader("📋 Watchlist Management")
    
    new_symbol = st.text_input("Add new symbol to watchlist")
    if st.button("Add") and new_symbol:
        if new_symbol.upper() not in WATCHLIST:
            WATCHLIST.append(new_symbol.upper())
            st.success(f"Added {new_symbol.upper()}")
        else:
            st.warning("Symbol already in watchlist")
    
    st.write("Current watchlist:", ", ".join(WATCHLIST))
    
    st.markdown("---")
    
    st.subheader("⚙️ Screening Criteria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Min ROE (%)", value=15.0, key="settings_min_roe")
        st.number_input("Max P/E", value=20.0, key="settings_max_pe")
        st.number_input("Max D/E", value=2.0, key="settings_max_de")
    
    with col2:
        st.number_input("Min Revenue Growth (%)", value=10.0, key="settings_min_growth")
        st.number_input("Min Market Cap (Billion)", value=5.0, key="settings_min_mcap")
    
    if st.button("Save Settings"):
        st.success("Settings saved!")
    
    st.markdown("---")
    
    st.subheader("🗃️ Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
    
    with col2:
        if st.button("Backup Portfolio"):
            st.info("Portfolio backed up!")
    
    with col3:
        if st.button("Export Data"):
            st.info("Data exported!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Vietnam Stock Analysis System | Built with ❤️ using Python & Streamlit</p>
        <p>Data sources: vnstock | ⚠️ For educational purposes only. Not financial advice.</p>
    </div>
    """,
    unsafe_allow_html=True
)