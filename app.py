import streamlit as st
from streamlit_js_eval import streamlit_js_eval

# ==========================================
# 1. ULTIMATE CSS (TradingView Dark Theme)
# ==========================================
st.set_page_config(page_title="Pro Terminal", layout="wide")

st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #131722; color: #d1d4dc; }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] { background-color: #1e222d; border-right: 1px solid #2a2e39; }
    
    /* Top Header */
    header { background-color: #131722 !important; }
    
    /* Custom Buy Button */
    div.stButton > button:first-child {
        background-color: #089981; color: white; border: none; border-radius: 4px; font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #067a68;
    }
    
    /* Custom Sell Button (using a trick to target the second button) */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:first-child {
        background-color: #F23645; color: white; border: none; border-radius: 4px; font-weight: bold;
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:first-child:hover {
        background-color: #c92c39;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (Watchlist)
# ==========================================
st.sidebar.title("📊 Watchlist")
st.sidebar.markdown("---")

market = st.sidebar.selectbox("Market", ["Stocks", "Crypto", "Forex"])

if market == "Stocks":
    assets = ["NASDAQ:AAPL", "NASDAQ:TSLA", "NASDAQ:NVDA", "NASDAQ:MSFT"]
elif market == "Crypto":
    assets = ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT"]
else:
    assets = ["FX:EURUSD", "FX:GBPUSD", "FX:USDJPY"]

selected_asset = st.sidebar.radio("Symbols", assets)

st.sidebar.markdown("---")
st.sidebar.subheader("Paper Account")
st.sidebar.metric("Equity", "$100,000.00")
st.sidebar.metric("Buying Power", "$400,000.00")

# ==========================================
# 3. MAIN HEADER
# ==========================================
col_title, col_price = st.columns([2, 1])

with col_title:
    st.markdown(f"### {selected_asset.split(':')[1]}")
    st.markdown(f"<span style='color: #787b86; font-size: 14px;'>{selected_asset.split(':')[0]} • 15m • Paper Trading</span>", unsafe_allow_html=True)

with col_price:
    # Simulated live price metric
    st.markdown("""
    <div style='text-align: right;'>
        <h2 style='color: #089981; margin-bottom: 0;'>78,450.20</h2>
        <span style='color: #089981;'>+1,245.50 (+1.62%)</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 4. TRADINGVIEW OFFICIAL WIDGET (JavaScript)
# ==========================================
# This JavaScript code loads the actual TradingView Advanced Chart
tv_js = f"""
    <div id="tvchart_container" style="height: 600px; width: 100%;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
      "autosize": true,
      "symbol": "{selected_asset}",
      "interval": "15",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "hide_side_toolbar": false,
      "allow_symbol_change": true,
      "container_id": "tvchart_container"
    }});
    </script>
"""

# Use Streamlit JS Eval to render the HTML/JS
streamlit_js_eval(js_expressions=tv_js, key='TV_CHART')

st.markdown("---")

# ==========================================
# 5. TRADE PANEL (Bottom)
# ==========================================
st.subheader("Trade")
col_buy, col_sell = st.columns(2)

with col_buy:
    st.number_input("Quantity (Buy)", min_value=1, value=100, key="buy_qty")
    if st.button("BUY / LONG", use_container_width=True):
        st.success("Order Executed: BUY")

with col_sell:
    st.number_input("Quantity (Sell)", min_value=1, value=100, key="sell_qty")
    if st.button("SELL / SHORT", use_container_width=True):
        st.error("Order Executed: SELL")
