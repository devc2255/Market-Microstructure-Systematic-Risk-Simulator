"""
app.py
Streamlit Dashboard for the Multi-Agent Systemic Risk Sandbox.
Features real-time API, Lot-Size Constraints (Orphan Shares), 5-Tier Gamified P&L, and VIX Spikes.
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
st.title("🏛️ Market Microstructure & Systemic Risk Simulator")
st.markdown("A quantitative microstructure simulation analyzing procyclical AI feedback loops and dynamic delta-hedging cascades.")

# 1. Initialize session state early
if 'sim_running' not in st.session_state:
    st.session_state.sim_running = False

# ==========================================
# SIDEBAR: CONFIGURATION & PORTFOLIO
# ==========================================
with st.sidebar:
    st.header("1. Market Initialization")
    st.markdown("Seed the synthetic engine with real-world aggregated tick data.")
    
    backend_key = os.getenv("POLYGON_KEY", "")
    
    if backend_key:
        polygon_key = backend_key
        st.markdown("🔒 **API Key:** Securely loaded from backend (`.env`)")
    else:
        polygon_key = st.text_input("Polygon.io API Key", type="password")
        st.warning("⚠️ Backend key not found. Please enter manually.")
        
    search_query = st.text_input("Search Company Name", value="Apple")
    ticker = "SPY" 
    
    if search_query and polygon_key:
        polygon_client = PolygonMarketData(polygon_key)
        matches = polygon_client.search_ticker_by_name(search_query)
        
        if matches:
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
                    st.session_state.init_spot = spot
                    st.session_state.init_sigma = sigma
                else:
                    st.error("API Call Failed. Check your key.")
        else:
            st.warning("Please provide a Polygon.io API Key.")

    st.markdown("---")
    st.header("2. Microstructure Status")
    if 'init_spot' in st.session_state:
        st.metric(label="Seeded Spot Price", value=f"${st.session_state.init_spot:,.2f}")
        st.metric(label="Base Volatility (σ)", value=f"{st.session_state.init_sigma:.4f}")
    else:
        st.info("Awaiting initialization. Defaulting to $100.00 / 0.15 σ")

    st.markdown("---")
    st.header("3. Portfolio Configuration")
    
    st.markdown("**Total Portfolio:** 10,000 Shares 🔒")
    total_shares = 10000
    
    # ADVANCED QUANT FEATURE: Step=1 allows granular testing of Lot Sizes
    target_hedge = st.number_input(
        "Target Shares to Hedge (Collar)", 
        min_value=0, 
        max_value=total_shares, 
        value=5000, 
        step=1,
        disabled=st.session_state.get('sim_running', False)
    )
    
    # Lot Size Mathematics
    options_contracts = target_hedge // 100
    effective_hedged_shares = options_contracts * 100
    orphan_shares = target_hedge % 100
    
    st.caption(f"Valid Contracts: **{options_contracts}** ({effective_hedged_shares} shares)")
    
    if orphan_shares > 0:
        st.warning(f"⚠️ **Liquidity Trap:** Options trade in lots of 100. Your {orphan_shares} fractional shares cannot be hedged and will be fully exposed to the market.")
    
    st.session_state.total_shares = total_shares
    st.session_state.effective_hedged_shares = effective_hedged_shares
    st.session_state.orphan_shares = orphan_shares
    st.session_state.options_contracts = options_contracts

# ==========================================
# STORYTELLING: MEET THE AGENTS
# ==========================================
with st.expander("📖 How it Works: Meet the Ecosystem (Click to read)", expanded=False):
    st.markdown("""
    This simulation runs distinct algorithms that interact to mimic a real stock market ecosystem:
    * 🕵️‍♂️ **1. The NLP Sentiment Agent:** Scans the news. Triggers the initial market sell-off during a shock.
    * 🏦 **2. The Quant Hedging Agent:** Panics during high volatility and buys Put Options to protect its capital.
    * ⚖️ **3. The Options Market Maker:** Forced to aggressively short-sell actual stock to hedge the options they sold, creating the Flash Crash.
    * 🛡️ **4. The Portfolio Manager (You):** You decide how much of your 10,000 shares to protect via a Zero-Cost Collar. 
    
    **💡 Note on Market Microstructure (Lot Sizes):** In real financial markets, options are strictly traded in lots of 100 shares. If you attempt to hedge a fractional amount (e.g., 3,427 shares), the market will only allow you to hedge 3,400 shares (34 contracts). The remaining 27 shares become "Orphan Shares" and are forced to take the full hit of a market crash.
    """)

# ==========================================
# STATE MANAGEMENT
# ==========================================
def initialize_simulation():
    spot = st.session_state.get('init_spot', 100.0)
    sigma = st.session_state.get('init_sigma', 0.15)
    
    st.session_state.engine = MatchingEngine(initial_price=spot, sigma=sigma)
    st.session_state.nlp_agent = NLPSentimentAgent()
    st.session_state.quant_agent = QuantHedgingAgent()
    st.session_state.mm_agent = OptionsMarketMaker()
    
    st.session_state.start_price = spot
    st.session_state.sim_running = False
    st.session_state.sim_completed = False 
    st.session_state.panic_triggered = False 
    st.session_state.final_fig = None      

    st.session_state.vol_history = [0]
    st.session_state.vol_colors = ['#00FF99']

if 'engine' not in st.session_state:
    initialize_simulation()

# ==========================================
# UI LAYOUT & EXECUTION CONTROLS
# ==========================================
col1, col2 = st.columns([1, 4])

with col1:
    st.subheader("Control Panel")
    
    if st.button("▶️ Start Market Sim", use_container_width=True, disabled=st.session_state.get('sim_running', False)):
        st.session_state.sim_running = True
        st.session_state.sim_completed = False
        st.session_state.panic_triggered = False 
        st.session_state.final_fig = None
        st.rerun() 
    
    st.markdown("---")
    st.markdown("**Exogenous Shock Trigger**")
    if st.button("🚨 Inject Macro Panic", type="primary", use_container_width=True):
        st.session_state.engine.trigger_exogenous_shock()
        st.session_state.engine.sigma *= 3.0 # VIX Spike
        st.session_state.sim_running = True 
        st.session_state.panic_triggered = True 
        st.rerun() 
        
    st.markdown("---")
    if st.button("🔄 Hard Reset", use_container_width=True):
        initialize_simulation()
        st.rerun()

    st.markdown("---")
    st.markdown("**Live Agent Telemetry**")
    telemetry_box = st.empty()

    # ==========================================
    # POST-SIMULATION PROOF & P&L (TRADE RECEIPT)
    # ==========================================
    if st.session_state.get('sim_completed', False):
        
        start_p = st.session_state.start_price
        end_p = st.session_state.engine.spot_price
        
        if st.session_state.get('panic_triggered', False):
            telemetry_box.warning("🛑 **Simulation Complete:** Trading Halted.")
            st.markdown("---")
            
            effective_hedged = st.session_state.effective_hedged_shares
            unhedged_shares = st.session_state.total_shares - effective_hedged
            contracts = st.session_state.options_contracts
            
            price_drop = max(0, start_p - end_p) 
            unhedged_loss = unhedged_shares * price_drop
            hedged_saved = effective_hedged * price_drop
            
            # --- 5-TIER GAMIFIED RISK GRADING ---
            hedge_ratio = effective_hedged / st.session_state.total_shares
            
            if hedge_ratio >= 0.85:
                st.success("🏆 **Ironclad Hedge (Excellent)**\n\nFlawless downside protection. The portfolio was mathematically immunized against the crash.")
            elif hedge_ratio >= 0.51:
                st.success("🛡️ **Adequate Protection (Good)**\n\nSolid risk mitigation. The majority of the firm's capital was successfully insulated.")
            elif hedge_ratio == 0.50:
                st.info("⚖️ **Balanced Exposure (Neutral)**\n\nDelta-Neutral stance. You perfectly balanced downside protection with upside capital efficiency.")
            elif hedge_ratio >= 0.26:
                st.warning("⚠️ **Dangerous Exposure (Bad)**\n\nInadequate protection. The partial hedge was insufficient to prevent severe portfolio damage.")
            else:
                st.error("🚨 **Catastrophic Exposure (Worst)**\n\nReckless risk management. The fund was decimated by the macro shock.")
            
            st.markdown(f"""
            **Trade Proof Breakdown:**
            * **Original Position:** {st.session_state.total_shares:,} shares
            * **Hedged Capital:** {effective_hedged:,} shares
            * **Exposed Capital:** {unhedged_shares:,} shares *(Includes {st.session_state.orphan_shares} Orphan Shares)*
            
            **Options Executed (1 Contract = 100 Shares):**
            * 📉 **Bought:** {contracts} Put Contracts
            * 📈 **Sold:** {contracts} Call Contracts
            
            ---
            **Financial Impact (P&L):**
            * **Initial Stock Price:** ${start_p:,.2f}
            * **Final Stock Price:** ${end_p:,.2f}
            * **Market Drop:** -${price_drop:,.2f} per share
            
            📉 **Unhedged Exposure:** Lost **${unhedged_loss:,.2f}** 
            
            🛡️ **Collar Protection:** Saved **${hedged_saved:,.2f}**
            """)
            
        else:
            telemetry_box.success("🛑 **Simulation Complete:** Trading Halted.")
            st.markdown("---")
            st.info("✅ **Market Remained Stable.** \n\nNo exogenous shocks detected. The Quant Agent did not execute the Zero-Cost Collar.")
            
            price_diff = end_p - start_p
            drift_direction = "+" if price_diff >= 0 else ""
            total_value_change = st.session_state.total_shares * price_diff
            
            st.markdown(f"""
            **Financial Impact (Normal Drift):**
            * **Initial Stock Price:** ${start_p:,.2f}
            * **Final Stock Price:** ${end_p:,.2f}
            * **Market Drift:** {drift_direction}${price_diff:,.2f} per share
            
            📊 **Total Portfolio Value Change:** **{drift_direction}${total_value_change:,.2f}**
            
            *Without a volatility spike, the portfolio experienced standard baseline market movement.*
            """)

with col2:
    chart_placeholder = st.empty()

# ==========================================
# CHART PERSISTENCE FIX
# ==========================================
if st.session_state.get('sim_completed', False) and not st.session_state.get('sim_running', False):
    if st.session_state.get('final_fig') is not None:
        chart_placeholder.plotly_chart(st.session_state.final_fig, use_container_width=True, theme=None)


# ==========================================
# CORE SIMULATION LOOP (Synthetic Engine)
# ==========================================
if st.session_state.get('sim_running', False):
    engine = st.session_state.engine
    nlp = st.session_state.nlp_agent
    quant = st.session_state.quant_agent
    mm = st.session_state.mm_agent
    
    current_contracts = st.session_state.options_contracts
    
    if len(engine.price_history) <= 1:
        st.session_state.vol_history = [0]
        st.session_state.vol_colors = ['#00FF99']
        
    for i in range(800):
        if not st.session_state.sim_running:
            break
            
        S = engine.spot_price
        sigma = engine.sigma
        
        nlp.evaluate_market(engine.shock_active)
        
        if quant.evaluate_risk(S, sigma):
            mm.assume_collar_risk(*quant.collar_strikes)
            
        base_hedge = mm.delta_hedge(S, sigma) 
        mm_sell_volume = base_hedge * current_contracts 
        
        engine.step(mm_sell_volume)

        current_vol = 100 + abs(mm_sell_volume * 10) if mm_sell_volume < 0 else 100 + (S * 0.1)
        vol_color = '#FF3366' if mm_sell_volume < 0 else '#00FF99'
        st.session_state.vol_history.append(current_vol)
        st.session_state.vol_colors.append(vol_color)
        
        if i % 20 == 0 or i == 799:
            
            if mm.active_collar and mm_sell_volume < 0:
                telemetry_box.warning(f"📉 **Quant Agent:** Buying Puts!\n\n🔥 **Market Maker:** Hedging! Shorting {abs(mm_sell_volume):.2f} shares!")
            elif nlp.sentiment_score == -1.0:
                telemetry_box.error("🚨 **NLP Agent:** Panic detected! Triggering market shock.")
            else:
                telemetry_box.success("🟢 **All Agents:** Market is stable. Normal trading.")

            fig = make_subplots(
                rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                subplot_titles=(
                    "Spot Price (Jump Diffusion SDE)", 
                    "Market Volume (Buy/Sell Pressure)",
                    "Order Book Imbalance (Liquidity Heatmap)", 
                    "Options MM Forced Selling (Inventory)"
                )
            )
            
            x_price = list(range(len(engine.price_history)))
            x_vol = list(range(len(st.session_state.vol_history)))
            x_obi = list(range(len(engine.obi_history)))
            x_inv = list(range(len(mm.inventory_history)))

            fig.add_trace(go.Scatter(x=x_price, y=engine.price_history, mode='lines', name='Spot Price', line=dict(color='#00F0FF', width=0.5)), row=1, col=1)
            fig.add_trace(go.Bar(x=x_vol, y=st.session_state.vol_history, marker_color=st.session_state.vol_colors, name='Volume'), row=2, col=1)
            fig.add_trace(go.Scatter(x=x_obi, y=engine.obi_history, mode='lines', fill='tozeroy', name='OBI', line=dict(color='#A200FF', width=1)), row=3, col=1)
            fig.add_trace(go.Bar(x=x_inv, y=mm.inventory_history, name='Short Inventory', marker_color='#FF9900', width=0.5), row=4, col=1)
            
            fig.update_layout(height=900, template='plotly_dark', showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            fig.update_yaxes(range=[-1.1, 1.1], row=3, col=1) 
            
            chart_placeholder.plotly_chart(fig, use_container_width=True, theme=None)
            st.session_state.final_fig = fig
            
            time.sleep(0.05) 
            
    st.session_state.sim_running = False
    st.session_state.sim_completed = True
    st.rerun()
