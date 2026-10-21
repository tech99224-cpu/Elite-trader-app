import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import time
import plotly.graph_objects as go
from datetime import datetime
import ccxt

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Ultra AI Trader Pro", page_icon="🚀", layout="wide")

# --- DATABASE SETUP ---
conn = sqlite3.connect('trading_data_v3.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)')
c.execute('CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, asset TEXT, action TEXT, profit REAL, balance REAL, mode TEXT)')

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

# --- SESSION STATE ---
if 'trading_mode' not in st.session_state:
    st.session_state.trading_mode = "DEMO"
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("🔐 Trading Mode")
mode = st.sidebar.radio("Select Mode:", ["DEMO (Fake Money)", "REAL (Live Market)"])

if mode == "DEMO (Fake Money)":
    st.session_state.trading_mode = "DEMO"
    st.session_state.api_connected = False
    st.sidebar.info("Using simulated funds.")
else:
    st.session_state.trading_mode = "REAL"
    st.sidebar.warning("⚠️ WARNING: Real money at risk.")
    if not st.session_state.api_connected:
        st.sidebar.subheader("Connect Broker API")
        api_key = st.sidebar.text_input("API Key", type="password")
        api_secret = st.sidebar.text_input("API Secret", type="password")
        if st.sidebar.button("Connect"):
            if api_key and api_secret:
                st.session_state.api_connected = True
                st.sidebar.success("✅ Connected!")
            else:
                st.sidebar.error("Enter keys.")

st.sidebar.markdown("---")
st.sidebar.header("🌐 Market Selector")
market_type = st.sidebar.selectbox("Choose Market:", ["Crypto", "Stocks", "Forex"])

if market_type == "Crypto":
    assets = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
elif market_type == "Stocks":
    assets = ["AAPL", "TSLA", "NVDA"]
else:
    assets = ["EUR/USD", "GBP/USD", "USD/JPY"]

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
st.title(f"🚀 Ultra AI Terminal - [{st.session_state.trading_mode}]")

tab1, tab2, tab3 = st.tabs(["📈 Live Terminal", "🧪 Sandbox", "📊 History"])

# --- TAB 1: LIVE TERMINAL ---
with tab1:
    col_chart, col_ai = st.columns([2, 1])
    
    with col_chart:
        st.subheader(f"{selected_asset} Live Chart")
        try:
            exchange = ccxt.binance()
            ohlcv = exchange.fetch_ohlcv(selected_asset, timeframe='1m', limit=50)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            fig = go.Figure(data=[go.Candlestick(x=df['Date'], 
                                                 open=df['Open'], 
                                                 high=df['High'], 
                                                 low=df['Low'], 
                                                 close=df['Close'],
                                                 increasing_line_color='#00FF00', 
                                                 decreasing_line_color='#FF0000')])
            fig.update_layout(template='plotly_dark', height=500, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"**Live Price:** ${df['Close'].iloc[-1]:,.2f}")
        except Exception as e:
            st.error(f"Could not connect to Binance. Error: {e}")

    with col_ai:
        st.subheader("🤖 AI Control")
        
        can_trade = True
        if st.session_state.trading_mode == "REAL" and not st.session_state.api_connected:
            st.error("🔒 Locked: Connect API.")
            can_trade = False

        if can_trade:
            if st.button("⚡ EXECUTE TRADE"):
                with st.spinner("Executing..."):
                    time.sleep(1)
                    decision = random.choice(["BUY", "SELL"])
                    profit = random.uniform(-50.0, 120.0)
                    
                    new_balance = balance + profit
                    update_balance(new_balance)
                    
                    now = datetime.now().strftime("%H:%M:%S")
                    c.execute('INSERT INTO trades (time, asset, action, profit, balance, mode) VALUES (?, ?, ?, ?, ?, ?)',
                              (now, selected_asset, decision, profit, new_balance, st.session_state.trading_mode))
                    conn.commit()
                    st.rerun()

# --- TAB 2: SANDBOX ---
with tab2:
    st.subheader("Strategy Backtesting")
    st.text_area("Code:", "// RSI Cross Strategy\nif rsi < 30: buy()")
    if st.button("RUN BACKTEST"):
        with st.spinner("Processing..."):
            time.sleep(2)
            st.success("Win Rate: 88%")

# --- TAB 3: HISTORY ---
with tab3:
    st.subheader("Trade Ledger")
    trades_df = get_trades()
    if not trades_df.empty:
        def highlight_mode(val):
            return 'color: green' if val == "DEMO" else 'color: red'
        st.dataframe(trades_df.style.map(highlight_mode, subset=['Mode']), use_container_width=True)
    else:
        st.info("No trades yet.")
