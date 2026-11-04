import streamlit as st
import yfinance as yf
import ccxt
import pandas as pd
from streamlit_js_eval import streamlit_js_eval
import sqlite3
import time
from datetime import datetime

# ==========================================
# 1. DATABASE SETUP (Real Paper Trading)
# ==========================================
conn = sqlite3.connect('pro_terminal.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)')
c.execute('CREATE TABLE IF NOT EXISTS positions (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, symbol TEXT, side TEXT, qty REAL, price REAL)')

# Initialize $100,000 Paper Account
c.execute('SELECT balance FROM wallet WHERE id = 1')
if c.fetchone() is None:
    c.execute('INSERT INTO wallet (id, balance) VALUES (1, 100000.0)')
    conn.commit()

def get_balance():
    c.execute('SELECT balance FROM wallet WHERE id = 1')
    return c.fetchone()[0]

def update_balance(new_bal):
    c.execute('UPDATE wallet SET balance = ? WHERE id = 1', (new_bal,))
    conn.commit()

def add_position(symbol, side, qty, price):
    now = datetime.now().strftime("%H:%M:%S")
    c.execute('INSERT INTO positions (time, symbol, side, qty, price) VALUES (?, ?, ?, ?, ?)', 
              (now, symbol, side, qty, price))
    conn.commit()

# ==========================================
# 2. PAGE CONFIG & ADVANCED CSS
# ==========================================
st.set_page_config(page_title="Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Global Dark Theme */
    .stApp { background-color: #131722; color: #d1d4dc; }
    [data-testid="stSidebar"] { background-color: #1e222d; border-right: 1px solid #2a2e39; }
    header { background-color: #131722 !important; }
    
    /* Buy Button */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #089981 !important; color: white !important; border: none !important; 
        border-radius: 4px !important; font-weight: 600 !important; width: 100% !important;
    }
    /* Sell Button */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #F23645 !important; color: white !important; border: none !important; 
        border-radius: 4px !important; font-weight: 600 !important; width: 100% !important;
    }
    
    /* Hide Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e222d; border-radius: 4px; color: #d1d4dc;}
    .stTabs [aria-selected="true"] { background-color: #2a2e39; color: white; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR (Watchlist & Account)
# ==========================================
with st.sidebar:
    st.markdown("<h4 style='margin-top:-20px;'>Watchlist</h4>", unsafe_allow_html=True)
    
    market = st.selectbox("Market", ["Stocks", "Crypto", "Forex"])
    
    if market == "Stocks":
        assets = ["NASDAQ:AAPL", "NASDAQ:TSLA", "NASDAQ:NVDA", "NASDAQ:MSFT"]
    elif market == "Crypto":
        assets = ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT"]
    else:
        assets = ["FX:EURUSD", "FX:GBPUSD", "FX:USDJPY"]

    selected_asset = st.radio("Symbols", assets)
    
    st.markdown("---")
    st.markdown("<h4>Paper Account</h4>", unsafe_allow_html=True)
    current_balance = get_balance()
    st.metric(label="Equity", value=f"${current_balance:,.2f}", delta="+1.2%")
    st.metric(label="Buying Power", value=f"${current_balance * 4:,.2f}")

# ==========================================
# 4. MAIN LAYOUT
# ==========================================
tab1, tab2 = st.tabs(["📈 Chart & Trade", "💼 Portfolio"])

with tab1:
    # Top Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h3 style='margin-bottom: 0;'>{selected_asset.split(':')[1]}</h3>", unsafe_allow_html=True)
        st.markdown(f"<span style='color: #787b86; font-size: 13px;'>{selected_asset.split(':')[0]} • Paper Trading</span>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='text-align: right;'>
            <h3 style='color: #089981; margin-bottom: 0;'>78,450.20</h3>
            <span style='color: #089981; font-size: 13px;'>+1.62% (+1,245.50)</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Real TradingView Chart Engine
    tv_js = f"""
        <div id="tvchart_pro" style="height: 550px; width: 100%;"></div>
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
          "toolbar_bg": "#131722",
          "enable_publishing": false,
          "withdateranges": true,
          "hide_side_toolbar": false,
          "allow_symbol_change": true,
          "details": true,
          "container_id": "tvchart_pro"
        }});
        </script>
    """
    # Load Chart
    streamlit_js_eval(js_expressions=tv_js, key='TV_CHART_PRO')

    st.markdown("---")

    # Trading Panel
    st.markdown("### Execute Trade")
    col_buy, col_sell = st.columns(2)
    
    with col_buy:
        qty_buy = st.number_input("Quantity", min_value=1, value=100, key="buy_qty")
        if st.button("BUY / LONG"):
            # Simulate order execution
            add_position(selected_asset, "LONG", qty_buy, 78450.20)
            st.success(f"Executed: Bought {qty_buy} of {selected_asset}")
            
    with col_sell:
        qty_sell = st.number_input("Limit Price", min_value=1, value=100, key="sell_qty", label_visibility="hidden")
        if st.button("SELL / SHORT"):
            # Simulate order execution
            add_position(selected_asset, "SHORT", qty_sell, 78450.20)
            st.error(f"Executed: Shorted {qty_sell} of {selected_asset}")

with tab2:
    st.markdown("### Open Positions & Order History")
    
    # Fetch positions from database
    c.execute('SELECT time, symbol, side, qty, price FROM positions ORDER BY id DESC')
    positions = c.fetchall()
    
    if positions:
        df = pd.DataFrame(positions, columns=["Time", "Symbol", "Side", "Quantity", "Price"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No open positions yet. Go to the Chart tab to place a trade.")
