# streamlit_app.py

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import datetime # For timestamps
import json # For JSON serialization/deserialization
import uuid # For generating a unique ID for the session (no persistence)

# Removed Firebase imports:
# import firebase_admin
# from firebase_admin import credentials, firestore, auth

# Ensure data_fetcher.py is in the same directory
from data_fetcher import get_usd_inr_rate, get_alpha_vantage_candlestick_data

# Import LangChain components for HuggingFaceHub
from langchain_community.llms import HuggingFaceHub # CORRECTED: Changed 'llls' to 'llms'
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# --- IMPORTANT: Portfolio Data is NOT Persistent without Firebase ---
# The portfolio and trade history will reset every time the app restarts
# or a new user session begins. This is because we are no longer saving
# to an external database.

# --- Initialize Virtual Portfolio in Session State ---
# Default values if not already in session_state
if 'inr_balance' not in st.session_state:
    st.session_state.inr_balance = 100000.0
if 'usd_held' not in st.session_state:
    st.session_state.usd_held = 0.0
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

# Generate a unique session ID (not a persistent user ID)
if 'session_id' not in st.session_state:
    st.session_state.session_id = "session_" + str(uuid.uuid4())

def reset_portfolio_callback():
    """Callback to reset the virtual portfolio."""
    st.session_state.inr_balance = 100000.0
    st.session_state.usd_held = 0.0
    st.session_state.trade_history = []
    st.success("Portfolio reset successfully! Refreshing app...")
    st.rerun() # Rerun to reflect changes


# --- Hugging Face LLM Setup ---
hf_token_value = os.getenv("HF_TOKEN")
if not hf_token_value:
    st.error("Error: Hugging Face API token (HF_TOKEN) not found. Please set it as an environment variable.")
    st.info("Example: In your terminal, run `export HF_TOKEN=\"YOUR_ACTUAL_TOKEN_HERE\"`")
    st.stop()
HF_TOKEN = hf_token_value

llm = None
try:
    llm = HuggingFaceHub(
        repo_id="HuggingFaceTB/SmolLM3-3B",
        huggingfacehub_api_token=HF_TOKEN,
        model_kwargs={"temperature": 0.7, "max_new_tokens": 256}
    )
except Exception as e:
    st.error(f"Error initializing HuggingFaceHub LLM: {e}")
    st.info("Please check your HF_TOKEN and ensure the model 'HuggingFaceTB/SmolLM3-3B' is accessible.")
    st.stop()

# Setup LangChain conversational chain with memory
template = """You are a helpful AI assistant specialized in USD to INR exchange rates and general forex trends.
You can analyze the provided chart data (candlesticks and SMAs) to give insights.
If the user asks for the current USD to INR price, you should provide it.
Keep your responses concise and to the point.

Current conversation:
{history}
Human: {input}
AI:"""
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(ai_prefix="AI"),
        prompt=prompt,
        verbose=False
    )
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --- Streamlit App Interface ---
st.set_page_config(
    page_title="USD/INR Trading Bot 💹",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("💹 USD/INR Trading Bot with Virtual Portfolio")
st.markdown("Ask me anything about USD to INR exchange rates or forex trends.")

# Display current USD to INR rate prominently
st.markdown("---")
live_rate = None
try:
    live_rate = get_usd_inr_rate()
    st.metric(label="Current USD to INR Rate", value=f"₹{live_rate:.2f} INR")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: small;'>
        (Live rate updates on app refresh or when asked)
        </div>
        """,
        unsafe_allow_html=True
    )
except Exception as e:
    st.error(f"⚠️ Error fetching live rate: {e}")
    st.info("Ensure your `data_fetcher.py` is correctly set up to retrieve the rate and `ALPHA_VANTAGE_API_KEY` is set.")
st.markdown("---")


# --- Virtual Portfolio Display ---
st.header("💰 Virtual Portfolio Status (Non-Persistent)")
if live_rate is not None:
    current_portfolio_value_inr = st.session_state.inr_balance + (st.session_state.usd_held * live_rate)
else:
    current_portfolio_value_inr = st.session_state.inr_balance # Cannot calculate USD value without live rate

col_bal1, col_bal2, col_bal3 = st.columns(3)
with col_bal1:
    st.metric(label="INR Balance", value=f"₹{st.session_state.inr_balance:,.2f}")
with col_bal2:
    st.metric(label="USD Held", value=f"${st.session_state.usd_held:,.2f}")
with col_bal3:
    st.metric(label="Total Portfolio Value (INR)", value=f"₹{current_portfolio_value_inr:,.2f}")

st.button("Reset Portfolio", on_click=reset_portfolio_callback)
st.markdown("---")


# --- Live Candlestick Chart Section (USD/INR) ---
st.header("📊 Live USD/INR Candlestick Chart (Alpha Vantage)")
st.warning("Note: Alpha Vantage free tier has rate limits (e.g., 5 requests/minute). Chart data refreshes every 5 minutes to avoid hitting limits.")

# Selectbox for interval for Alpha Vantage
interval_options = {
    "1 Minute": "1min",
    "5 Minutes": "5min",
    "15 Minutes": "15min",
    "30 Minutes": "30min",
    "1 Hour": "60min",
}
selected_interval_label = st.selectbox(
    "Select Candlestick Interval:",
    list(interval_options.keys()),
    index=1 # Default to 5 Minutes
)
selected_interval_av = interval_options[selected_interval_label]

# Sliders for SMA periods
col_sma1, col_sma2 = st.columns(2)
with col_sma1:
    short_sma_period = st.slider("Short SMA Period (Candles)", min_value=5, max_value=50, value=20, step=1)
with col_sma2:
    long_sma_period = st.slider("Long SMA Period (Candles)", min_value=20, max_value=200, value=50, step=5)

if short_sma_period >= long_sma_period:
    st.warning("Short SMA period should be less than Long SMA period for meaningful analysis.")


# Cache the data for 5 minutes (300 seconds) to respect Alpha Vantage free tier limits
@st.cache_data(ttl=300)
def plot_candlestick_chart(symbol, to_symbol, interval, short_sma, long_sma):
    """
    Fetches Alpha Vantage candlestick data, calculates SMAs, generates signals,
    and creates a Plotly chart.
    """
    try:
        candlestick_df = get_alpha_vantage_candlestick_data(
            symbol=symbol, to_symbol=to_symbol, interval=interval, outputsize="compact"
        )

        if not candlestick_df.empty:
            # Calculate SMAs
            candlestick_df['SMA_Short'] = candlestick_df['Close'].rolling(window=short_sma).mean()
            candlestick_df['SMA_Long'] = candlestick_df['Close'].rolling(window=long_sma).mean()

            # Generate Signals
            candlestick_df['Signal'] = 0
            candlestick_df.loc[candlestick_df['SMA_Short'] > candlestick_df['SMA_Long'], 'Signal'] = 1
            candlestick_df.loc[candlestick_df['SMA_Short'] < candlestick_df['SMA_Long'], 'Signal'] = -1
            candlestick_df['Position'] = candlestick_df['Signal'].diff()

            # --- Trading Simulation (for chart display, not actual portfolio updates) ---
            # This simulation is for visualizing signals on the chart, not for the persistent portfolio
            buy_markers_x = []
            buy_markers_y = []
            sell_markers_x = []
            sell_markers_y = []

            # Find points where position changes
            for i in range(1, len(candlestick_df)):
                if candlestick_df['Position'].iloc[i] == 1: # Buy signal
                    buy_markers_x.append(candlestick_df.index[i])
                    buy_markers_y.append(candlestick_df['Close'].iloc[i])
                elif candlestick_df['Position'].iloc[i] == -1: # Sell signal
                    sell_markers_x.append(candlestick_df.index[i])
                    sell_markers_y.append(candlestick_df['Close'].iloc[i])

            # --- Plotting ---
            fig = go.Figure(data=[go.Candlestick(
                x=candlestick_df.index,
                open=candlestick_df['Open'],
                high=candlestick_df['High'],
                low=candlestick_df['Low'],
                close=candlestick_df['Close'],
                name='Candlesticks'
            )])

            fig.add_trace(go.Scatter(
                x=candlestick_df.index,
                y=candlestick_df['SMA_Short'],
                mode='lines',
                name=f'SMA {short_sma}',
                line=dict(color='blue', width=1)
            ))

            fig.add_trace(go.Scatter(
                x=candlestick_df.index,
                y=candlestick_df['SMA_Long'],
                mode='lines',
                name=f'SMA {long_sma}',
                line=dict(color='orange', width=1)
            ))

            fig.add_trace(go.Scatter(
                x=buy_markers_x,
                y=buy_markers_y,
                mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='green'),
                name='Buy Signal'
            ))

            fig.add_trace(go.Scatter(
                x=sell_markers_x,
                y=sell_markers_y,
                mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'),
                name='Sell Signal'
            ))

            fig.update_layout(
                title=f'{symbol}/{to_symbol} Candlestick Chart with SMAs & Signals ({selected_interval_label})',
                xaxis_title='Time',
                yaxis_title='Price (INR)',
                xaxis_rangeslider_visible=False,
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No candlestick data available to display for the selected period/interval. Check API key or limits.")
    except Exception as e:
        st.error(f"Error displaying USD/INR candlestick chart: {e}")

# Call the function to display the chart for USD/INR with signals
plot_candlestick_chart( # Renamed function call
    symbol="USD",
    to_symbol="INR",
    interval=selected_interval_av,
    short_sma=short_sma_period,
    long_sma=long_sma_period
)

st.markdown("---")


# --- Manual Trade Execution (Updates Non-Persistent Portfolio) ---
st.header("🛒 Manual Trade Execution")
st.markdown("Execute trades directly to update your virtual portfolio. (Data is NOT persistent across sessions)")

col_trade_amount, col_trade_buttons = st.columns([0.7, 0.3])
with col_trade_amount:
    trade_amount_usd = st.number_input("Amount to Trade (USD)", min_value=0.01, value=100.0, step=10.0)

with col_trade_buttons:
    st.write("") # Spacer
    st.write("") # Spacer
    if st.button("Buy USD"):
        if live_rate is None:
            st.error("Cannot execute trade: Live rate not available.")
        else:
            cost_inr = trade_amount_usd * live_rate
            if st.session_state.inr_balance >= cost_inr:
                st.session_state.inr_balance -= cost_inr
                st.session_state.usd_held += trade_amount_usd
                st.session_state.trade_history.append({
                    'Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Type': 'MANUAL BUY',
                    'Amount (USD)': f"{trade_amount_usd:.2f}",
                    'Cost (INR)': f"₹{cost_inr:,.2f}",
                    'Price': f"₹{live_rate:.2f}",
                    'INR Balance': f"₹{st.session_state.inr_balance:,.2f}",
                    'USD Held': f"${st.session_state.usd_held:,.2f}"
                })
                st.success(f"Successfully bought ${trade_amount_usd:.2f} USD!")
                st.rerun()
            else:
                st.error("Insufficient INR balance to buy USD.")

    if st.button("Sell USD"):
        if live_rate is None:
            st.error("Cannot execute trade: Live rate not available.")
        else:
            if st.session_state.usd_held >= trade_amount_usd:
                revenue_inr = trade_amount_usd * live_rate
                st.session_state.inr_balance += revenue_inr
                st.session_state.usd_held -= trade_amount_usd
                st.session_state.trade_history.append({
                    'Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Type': 'MANUAL SELL',
                    'Amount (USD)': f"{trade_amount_usd:.2f}",
                    'Revenue (INR)': f"₹{revenue_inr:,.2f}",
                    'Price': f"₹{live_rate:.2f}",
                    'INR Balance': f"₹{st.session_state.inr_balance:,.2f}",
                    'USD Held': f"${st.session_state.usd_held:,.2f}"
                })
                st.success(f"Successfully sold ${trade_amount_usd:.2f} USD!")
                st.rerun()
            else:
                st.error("Insufficient USD held to sell.")

st.subheader("Trade History (Non-Persistent)")
if st.session_state.trade_history:
    trade_df = pd.DataFrame(st.session_state.trade_history)
    st.dataframe(trade_df)
else:
    st.info("No trade history yet for this session.")
st.markdown("---")


# --- Chat Section ---
st.header("💬 Chat with the Bot")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**🧠 Your Question:** {message['content']}")
    else:
        st.markdown(f"**🤖 Response:** {message['content']}")

# --- Input Form for Chat ---
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("🧠 Ask a question:", key="user_question_input")
    submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        if user_input.lower() == 'exit':
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "bot", "content": "Goodbye! The bot session has ended."})
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("🤖 Thinking..."):
                llm_response = ""
                # Enhance LLM prompt with current chart context if available
                chart_context = ""
                if live_rate is not None:
                    chart_context = f"The current USD to INR rate is ₹{live_rate:.2f}. "
                # Further context like SMA values could be added here if needed
                # (e.g., by passing them from the chart function or re-calculating on cached data)

                llm_input_with_context = f"{chart_context}Human: {user_input}"
                llm_response = st.session_state.conversation.predict(input=llm_input_with_context)

                st.session_state.chat_history.append({"role": "bot", "content": llm_response})

