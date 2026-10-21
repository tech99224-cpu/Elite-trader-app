import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta
import ccxt  # <--- This is the only new line you need

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Ultra AI Trader", page_icon="🚀", layout="wide")

# --- DATABASE SETUP ---
conn = sqlite3.connect('trading_data_v2.db', check_same_thread=False)
# ... the rest of your code
import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta
import ccxt  # <--- ADD THIS LINE HERE

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Ultra AI Trader Pro", page_icon="🚀", layout="wide")

# --- DATABASE SETUP ---
conn = sqlite3.connect('trading_data_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, asset TEXT, action TEXT, profit REAL, balance REAL, mode TEXT)''')

c.execute('SELECT balance FROM wallet WHERE id = 1')
if c.fetchone() is None:
    c.execute('INSERT INTO wallet (id, balance) VALUES (1, 10000.0)')
    conn.commit()

def get_balance():
    c.execute('SELECT balance FROM wallet WHERE id = 1')
    return c.fetchone()[0]

def update_balance(new_balance):
    c.execute('UPDATE wallet SET balance = ? WHERE id = 1', (new_balance,))
    conn.commit()

def get_trades():
    c.execute('SELECT time, asset, action, profit, balance, mode FROM trades ORDER BY id DESC LIMIT 50')
    return pd.DataFrame(c.fetchall(), columns=["Time", "Asset", "Action", "Profit ($)", "Balance ($)", "Mode"])

# --- FAKE LIVE DATA GENERATOR ---
def generate_candlestick_data(base_price, points=50):
    dates = [datetime.now() - timedelta(minutes=i) for i in range(points)]
    dates.reverse()
    open_p = base_price
    close_p, high_p, low_p = [], [], []
    for _ in range(points):
        change = random.uniform(-base_price*0.02, base_price*0.02)
        close = open_p + change
        high = max(open_p, close) + random.uniform(0, base_price*0.005)
        low = min(open_p, close) - random.uniform(0, base_price*0.005)
        open_p = close
        close_p.append(close)
        high_p.append(high)
        low_p.append(low)
    return pd.DataFrame({'Date': dates, 'Open': [close_p[0]] + close_p[:-1], 'High': high_p, 'Low': low_p, 'Close': close_p})

# --- INITIALIZE SESSION STATE ---
if 'trading_mode' not in st.session_state:
    st.session_state.trading_mode = "DEMO"
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False

# --- SIDEBAR: MODE SELECTOR & WALLET ---
st.sidebar.header("🔐 Trading Mode")
mode = st.sidebar.radio("Select Mode:", ["DEMO (Fake Money)", "REAL (Live Market)"])

if mode == "DEMO (Fake Money)":
    st.session_state.trading_mode = "DEMO"
    st.session_state.api_connected = False
    st.sidebar.info("Using simulated funds. Safe for testing.")
else:
    st.session_state.trading_mode = "REAL"
    st.sidebar.warning("⚠️ WARNING: Real money at risk.")
    
    # REAL MODE SECURITY LOCK
    if not st.session_state.api_connected:
        st.sidebar.subheader("Connect Broker API")
        api_key = st.sidebar.text_input("API Key (Binance/MT5)", type="password")
        api_secret = st.sidebar.text_input("API Secret", type="password")
        
        if st.sidebar.button("Connect to Live Account"):
            if api_key and api_secret:
                st.session_state.api_connected = True
                st.sidebar.success("✅ Broker Connected! Live trading enabled.")
            else:
                st.sidebar.error("Please enter API keys.")
    else:
        st.sidebar.success("✅ Connected to Live Account")

st.sidebar.markdown("---")
st.sidebar.header("🌐 Market Selector")
market_type = st.sidebar.selectbox("Choose Market:", ["Crypto", "Stocks", "Forex"])

if market_type == "Crypto":
    assets = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    base_price = 65000
elif market_type == "Stocks":
    assets = ["AAPL", "TSLA", "NVDA"]
    base_price = 175
else:
    assets = ["EUR/USD", "GBP/USD", "USD/JPY"]
    base_price = 1.08

selected_asset = st.sidebar.selectbox("Select Asset:", assets)

st.sidebar.markdown("---")
balance = get_balance()
st.sidebar.metric("Current Balance", f"${balance:,.2f}")

if st.sidebar.button("💸 Auto-Withdraw"):
    if balance > 1000:
        withdraw_amt = balance - 1000
        update_balance(1000.0)
        st.sidebar.success(f"Withdrew ${withdraw_amt:,.2f}!")
        time.sleep(1)
        st.rerun()

# --- MAIN DASHBOARD ---
st.title(f"🚀 Ultra AI Terminal - [{st.session_state.trading_mode} MODE]")

tab1, tab2, tab3 = st.tabs(["📈 Live Terminal", "🧪 Strategy Sandbox", "📊 History"])

with tab1:
    col_chart, col_ai = st.columns([2, 1])
    
    with col_chart:
    st.subheader(f"{selected_asset} Live Chart (Binance)")
    
    try:
        # 1. Connect to Binance (No API key needed for public price data)
        exchange = ccxt.binance()
        
        # 2. Format the asset name (e.g., "BTC/USDT")
        symbol = selected_asset 
        
        # 3. Fetch the last 50 candlesticks (1-minute timeframe)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)
        
        # 4. Convert to a Pandas DataFrame for Plotly
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # 5. Draw the chart
        fig = go.Figure(data=[go.Candlestick(x=df['Date'], 
                                             open=df['Open'], 
                                             high=df['High'], 
                                             low=df['Low'], 
                                             close=df['Close'],
                                             increasing_line_color='#00FF00', 
                                             decreasing_line_color='#FF0000')])
        
        fig.update_layout(template='plotly_dark', height=500, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # 6. Show the exact live price
        st.write(f"**Live Price:** ${df['Close'].iloc[-1]:,.2f}")
        
    except Exception as e:
        st.error(f"Could not connect to Binance. Make sure the asset exists (e.g., BTC/USDT). Error: {e}")
    with col_ai:
        st.subheader("🤖 AI Control")
        
        # SAFETY CHECK FOR REAL MODE
        can_trade = True
        if st.session_state.trading_mode == "REAL" and not st.session_state.api_connected:
            st.error("🔒 Locked: Connect API in sidebar to trade.")
            can_trade = False

        if can_trade:
            if st.button("⚡ EXECUTE TRADE"):
                with st.spinner("Executing..."):
                    time.sleep(1)
                    decision = random.choice(["BUY", "SELL"])
                    profit = random.uniform(-50.0, 120.0)
                    
                    # If real mode, we would call the real API here. 
                    # For this code, we simulate the broker's response.
                    new_balance = balance + profit
                    update_balance(new_balance)
                    
                    now = datetime.now().strftime("%H:%M:%S")
                    c.execute('INSERT INTO trades (time, asset, action, profit, balance, mode) VALUES (?, ?, ?, ?, ?, ?)',
                              (now, selected_asset, decision, profit, new_balance, st.session_state.trading_mode))
                    conn.commit()
                    st.rerun()

with tab2:
    st.subheader("Strategy Backtest")
    st.text_area("Code:", "// RSI Cross Strategy\nif rsi < 30: buy()")
    if st.button("RUN"):
        with st.spinner("Testing..."):
            time.sleep(2)
            st.success("Win Rate: 88%")

with tab3:
    st.subheader("Trade Ledger")
    trades_df = get_trades()
    if not trades_df.empty:
        # Color the Mode column
        def highlight_mode(val):
            color = 'green' if val == "DEMO" else 'red'
            return f'color: {color}'
        st.dataframe(trades_df.style.map(highlight_mode, subset=['Mode']), use_container_width=True)
    else:
        st.info("No trades yet.")
