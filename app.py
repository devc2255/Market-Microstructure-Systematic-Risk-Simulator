"""
app.py
Streamlit Dashboard for the Multi-Agent Systemic Risk Sandbox.
Features real-time Polygon.io API initialization, 4-tier telemetry visualization, and UI Frame Batching.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modularized components
from matching_engine import MatchingEngine
from simulation_agents import NLPSentimentAgent, QuantHedgingAgent, OptionsMarketMaker
from data_ingestion import PolygonMarketData

# Configure Streamlit Page
st.set_page_config(page_title="Systemic Risk Sandbox", layout="wide", initial_sidebar_state="expanded")
st.title("🏛️ Multi-Agent Systemic Risk Sandbox")
st.markdown("A quantitative microstructure simulation analyzing procyclical AI feedback loops and dynamic delta-hedging cascades.")

# ==========================================
# SIDEBAR: POLYGON.IO INTEGRATION
# ==========================================
with st.sidebar:
    st.header("1. Market Initialization")
    st.markdown("Seed the synthetic engine with real-world aggregated tick data via Polygon.io.")
    
    # Institutional Security: Check backend environment variables silently
    backend_key = os.getenv("POLYGON_KEY", "")
    
    if backend_key:
        polygon_key = backend_key
        st.markdown("🔒 **API Key:** Securely loaded from backend (`.env`)")
    else:
        # Fallback UI only if backend key is missing
        polygon_key = st.text_input("Polygon.io API Key", type="password")
        st.warning("⚠️ Backend key not found. Please enter manually.")
        
    # 1. User types any keyword or partial company name
    search_query = st.text_input("Search Company Name", value="Apple")
    
    ticker = "SPY" # Default baseline fallback
    
    # 2. Query backend automatically as the user types
    if search_query and polygon_key:
        polygon_client = PolygonMarketData(polygon_key)
        matches = polygon_client.search_ticker_by_name(search_query)
        
        if matches:
            # Map user-friendly strings ("AAPL - Apple Inc.") to raw tickers ("AAPL")
            ticker_map = {f"{t} - {n}": t for t, n in matches}
            selected_display = st.selectbox("Select Matching Company", options=list(ticker_map.keys()))
            ticker = ticker_map[selected_display]
        else:
            st.caption("No exact corporate match found. Defaulting to SPY index.")
    
    if st.button("Fetch Live State", use_container_width=True):
        if polygon_key:
            with st.spinner(f"Querying Polygon.io for {ticker}..."):
                polygon_client = PolygonMarketData(polygon_key)
                market_state = polygon_client.fetch_initial_state(ticker)
                
                if market_state:
                    spot, sigma = market_state
                    st.success(f"Success: {ticker} @ ${spot:,.2f} | Vol Proxy: {sigma:.4f}")
                    # Cache the fetched variables into the session state
                    st.session_state.init_spot = spot
                    st.session_state.init_sigma = sigma
                else:
                    st.error("API Call Failed. Check your key, internet connection, or ticker symbol.")
        else:
            st.warning("Please provide a Polygon.io API Key.")

    st.markdown("---")
    st.header("2. Microstructure Status")
    if 'init_spot' in st.session_state:
        st.metric(label="Seeded Spot Price", value=f"${st.session_state.init_spot:,.2f}")
        st.metric(label="Base Volatility (σ)", value=f"{st.session_state.init_sigma:.4f}")
    else:
        st.info("Awaiting initialization. Defaulting to $100.00 / 0.15 σ")

# ==========================================
# STORYTELLING: MEET THE AGENTS
# ==========================================
with st.expander("📖 How it Works: Meet the AI Agents (Click to read)", expanded=False):
    st.markdown("""
    This simulation runs three distinct AI algorithms that interact with each other to mimic a real stock market ecosystem:
    
    * 🕵️‍♂️ **1. The NLP Sentiment Agent (The Catalyst):** Scans the news. When you click 'Inject Macro Panic', this agent reads a disastrous headline and triggers the initial market sell-off.
    * 🏦 **2. The Quant Hedging Agent (The Big Bank):** Holds a massive portfolio. When it sees the market crashing and volatility spiking, it panics and buys 'Put Options' (insurance) to protect its money.
    * ⚖️ **3. The Options Market Maker (The Liquidity Provider):** The firm that sells the insurance to the Quant Agent. To balance their own risk, they are forced to aggressively short-sell the actual stock. This forced selling is the "domino effect" that turns a small dip into a Flash Crash.
    """)
# ==========================================
# STATE MANAGEMENT
# ==========================================
def initialize_simulation():
    """Initializes or resets the engine using Polygon data if cached, else defaults."""
    spot = st.session_state.get('init_spot', 100.0)
    sigma = st.session_state.get('init_sigma', 0.15)
    
    st.session_state.engine = MatchingEngine(initial_price=spot, sigma=sigma)
    st.session_state.nlp_agent = NLPSentimentAgent()
    st.session_state.quant_agent = QuantHedgingAgent()
    st.session_state.mm_agent = OptionsMarketMaker()
    st.session_state.sim_running = False

    # --- ADDED: Volume tracking history arrays ---
    st.session_state.vol_history = [0]
    st.session_state.vol_colors = ['#00FF99']

if 'engine' not in st.session_state:
    initialize_simulation()

# ==========================================
# UI LAYOUT & CONTROLS
# ==========================================
col1, col2 = st.columns([1, 4])

with col1:
    st.subheader("Control Panel")
    if st.button("▶️ Start Market Sim", use_container_width=True):
        st.session_state.sim_running = True
    
    st.markdown("---")
    st.markdown("**Exogenous Shock Trigger**")
    if st.button("🚨 Inject Macro Panic", type="primary", use_container_width=True):
        st.session_state.engine.trigger_exogenous_shock()
        st.session_state.sim_running = True # Keep simulation running when shocked
        
    st.markdown("---")
    if st.button("🔄 Hard Reset", use_container_width=True):
        initialize_simulation()
        st.rerun()

    st.markdown("---")
    st.markdown("**Live Agent Telemetry (The Chain)**")
    telemetry_box = st.empty()

with col2:
    chart_placeholder = st.empty()

# ==========================================
# CORE SIMULATION LOOP (Synthetic Engine)
# ==========================================
if st.session_state.sim_running:
    # Retrieve instantiated tracking references from session state
    engine = st.session_state.engine
    nlp = st.session_state.nlp_agent
    quant = st.session_state.quant_agent
    mm = st.session_state.mm_agent
    
    # Reset visual history arrays on a fresh run start to prevent memory lag
    if len(engine.price_history) <= 1:
        st.session_state.vol_history = [0]
        st.session_state.vol_colors = ['#00FF99']
        
    # Process batch of ticks
    for i in range(400):
        if not st.session_state.sim_running:
            break
            
        S = engine.spot_price
        sigma = engine.sigma
        
        # 1. NLP Sentiment Evaluation
        nlp.evaluate_market(engine.shock_active)
        
        # 2. Quant Agent Risk Management
        if quant.evaluate_risk(S, sigma):
            mm.assume_collar_risk(*quant.collar_strikes)
            
        # 3. Options Market Maker Delta-Hedging
        mm_sell_volume = mm.delta_hedge(S, sigma)
        
        # 4. Advance Market Microstructure step
        engine.step(mm_sell_volume)

        # Record Volume History tick-by-tick
        current_vol = 100 + abs(mm_sell_volume * 10) if mm_sell_volume < 0 else 100 + (S * 0.1)
        vol_color = '#FF3366' if mm_sell_volume < 0 else '#00FF99'
        st.session_state.vol_history.append(current_vol)
        st.session_state.vol_colors.append(vol_color)
        
        # ==========================================
        # BALANCED UI FRAME BATCHING
        # ==========================================
        # Updating every 4 ticks restores high visual granularity (100 distinct steps)
        if i % 4 == 0 or i == 399:
            # --- DYNAMIC TELEMETRY CHAIN UPDATES ---
            if mm.active_collar and mm_sell_volume < 0:
                telemetry_box.warning(f"📉 **2. Quant Agent:** Buying Puts!\n\n🔥 **3. Market Maker:** Hedging! Shorting {abs(mm_sell_volume)} shares!")
            elif nlp.sentiment_score == -1.0:
                telemetry_box.error("🚨 **1. NLP Agent:** Panic detected! Triggering initial market shock.")
            else:
                telemetry_box.success("🟢 **All Agents:** Market is stable. Normal trading.")

            # --- LIVE PLOTLY TELEMETRY (4 TIERS) ---
            fig = make_subplots(
                rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                subplot_titles=(
                    "Spot Price (Jump Diffusion SDE)", 
                    "Market Volume (Buy/Sell Pressure)",
                    "Order Book Imbalance (Liquidity Heatmap)", 
                    "Options MM Forced Selling (Inventory)"
                )
            )
            
            # Row 1: Spot Price
            fig.add_trace(go.Scatter(y=engine.price_history, mode='lines', name='Spot Price', line=dict(color='#00F0FF', width=0.5)), row=1, col=1)
            
            # Row 2: Volume
            fig.add_trace(go.Bar(y=st.session_state.vol_history, marker_color=st.session_state.vol_colors, name='Volume'), row=2, col=1)
            
            # Row 3: Order Book Imbalance
            fig.add_trace(go.Scatter(y=engine.obi_history, mode='lines', fill='tozeroy', name='OBI', line=dict(color='#A200FF', width=1)), row=3, col=1)
            
            # Row 4: MM Inventory
            fig.add_trace(go.Bar(y=mm.inventory_history, name='Short Inventory', marker_color='#FF9900', width=0.5), row=4, col=1)
            
            # UI Styling configurations
            fig.update_layout(height=900, template='plotly_dark', showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            fig.update_yaxes(range=[-1.1, 1.1], row=3, col=1) 
            
            # Render to browser without extra theme wrapping overhead
            chart_placeholder.plotly_chart(fig, use_container_width=True, theme=None)
            
            # Pacing delay: 0.06s allows the browser window to completely finish painting 
            # the current frame before the backend sends the next WebSocket update.
            time.sleep(0.06) 
        
    st.session_state.sim_running = False