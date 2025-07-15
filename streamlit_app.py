# streamlit_app.py

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go # For candlestick chart
import numpy as np # For numerical operations
import time
from datetime import datetime, timedelta

# Ensure data_fetcher.py is in the same directory and contains get_usd_inr_rate()
from data_fetcher import get_usd_inr_rate, get_yfinance_candlestick_data, get_current_rate_with_fallback, get_live_candlestick_data

# Import LangChain components for HuggingFaceHub
from langchain_community.llms import HuggingFaceHub
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# --- Configuration and LLM Setup ---
# Set your Hugging Face API key from environment variable for security
# It's highly recommended to set this as an environment variable (e.g., in your .bashrc, .zshrc, or system settings)
# Example of how to set it in your terminal (for current session only):
# export HF_TOKEN="hf_YOUR_ACTUAL_TOKEN_HERE"

# Attempt to retrieve the token from environment variables
hf_token_value = os.getenv("HF_TOKEN")

# --- Debugging print statements for HF_TOKEN ---
print(f"DEBUG: Initial HF_TOKEN value from environment: {hf_token_value}")

if not hf_token_value:
    st.error("Error: Hugging Face API token (HF_TOKEN) not found. Please set it as an environment variable.")
    st.info("Example: In your terminal, run `export HF_TOKEN=\"YOUR_ACTUAL_HF_TOKEN_HERE\"`")
    st.stop() # Stop the app if token is missing

# Assign the retrieved value to HF_TOKEN for use in HuggingFaceHub
HF_TOKEN = hf_token_value
print(f"DEBUG: HF_TOKEN assigned for LLM: {HF_TOKEN[:5]}...{HF_TOKEN[-5:]}") # Print partial token for security

# Initialize HuggingFaceHub LLM
llm = None # Initialize llm to None
try:
    llm = HuggingFaceHub(
        repo_id="HuggingFaceTB/SmolLM3-3B", # Using the previous Hugging Face model
        huggingfacehub_api_token=HF_TOKEN,
        model_kwargs={"temperature": 0.7, "max_new_tokens": 256}
    )
    print("DEBUG: HuggingFaceHub LLM initialized successfully.")
except Exception as e:
    st.error(f"Error initializing HuggingFaceHub LLM: {e}")
    st.info("Please check your HF_TOKEN and ensure the model 'HuggingFaceTB/SmolLM3-3B' is accessible.")
    st.stop()

# Ensure LLM is not None before proceeding
if llm is None:
    st.error("LLM object is None after initialization attempt. Cannot proceed.")
    st.stop()


# Setup LangChain conversational chain with memory
template = """You are a helpful AI assistant specialized in USD to INR exchange rates and general forex trends.
If the user asks for the current USD to INR price, you should provide it.
Keep your responses concise and to the point.

Current conversation:
{history}
Human: {input}
AI:"""
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

# Initialize memory for the conversation
if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(ai_prefix="AI"),
        prompt=prompt,
        verbose=False # Set to False to suppress the "think" block
    )
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --- Initialize Virtual Portfolio in Session State ---
if 'inr_balance' not in st.session_state:
    st.session_state.inr_balance = 100000.0 # Starting INR balance
if 'usd_held' not in st.session_state:
    st.session_state.usd_held = 0.0 # Starting USD held
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = [] # List to store trade records

def reset_portfolio():
    """Resets the virtual portfolio to initial values."""
    st.session_state.inr_balance = 100000.0
    st.session_state.usd_held = 0.0
    st.session_state.trade_history = []
    st.success("Portfolio reset successfully!")

# --- Streamlit App Interface ---
st.set_page_config(
    page_title="USD/INR Trading Bot 💹",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💹 USD/INR Trading Bot with Live Intraday Charts")
st.markdown("Real-time USD/INR trading with intraday charts, SMA signals, and AI assistant.")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("📊 Chart Settings")
    
    # Data Source Selection
    data_source = st.selectbox(
        "Data Source:",
        ["Alpha Vantage (Intraday)", "Yahoo Finance (Daily)"],
        help="Alpha Vantage provides true intraday data, Yahoo Finance provides daily data"
    )
    
    # Timeframe Selection
    if data_source == "Alpha Vantage (Intraday)":
        timeframe_options = {
            "1 Minute": "1min",
            "5 Minutes": "5min", 
            "15 Minutes": "15min",
            "30 Minutes": "30min",
            "60 Minutes": "60min",
            "Daily": "1d"
        }
        selected_timeframe_label = st.selectbox(
            "Chart Timeframe:",
            list(timeframe_options.keys()),
            index=1,  # Default to 5 minutes
            help="Select the timeframe for intraday data"
        )
        selected_timeframe = timeframe_options[selected_timeframe_label]
        data_source_key = 'alphavantage'
    else:
        # Yahoo Finance periods
        timeframe_options = {
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "5 Years": "5y",
            "Max": "max"
        }
        selected_timeframe_label = st.selectbox(
            "Chart Period:",
            list(timeframe_options.keys()),
            index=0,  # Default to 1 Month
            help="Select the time period for daily data"
        )
        selected_timeframe = timeframe_options[selected_timeframe_label]
        data_source_key = 'yfinance'
    
    # SMA Settings
    st.header("📈 SMA Settings")
    short_sma_period = st.slider("Short SMA Period", min_value=5, max_value=50, value=20, step=1)
    long_sma_period = st.slider("Long SMA Period", min_value=20, max_value=200, value=50, step=5)
    
    if short_sma_period >= long_sma_period:
        st.warning("Short SMA period should be less than Long SMA period for meaningful analysis.")
    
    # Refresh Settings
    st.header("🔄 Refresh Settings")
    if data_source_key == 'alphavantage':
        auto_refresh = st.checkbox("Auto-refresh chart", value=True)
        if auto_refresh:
            refresh_interval = st.slider("Refresh interval (seconds)", min_value=30, max_value=300, value=60, step=30)
    else:
        auto_refresh = st.checkbox("Auto-refresh chart", value=False)
        refresh_interval = st.slider("Refresh interval (seconds)", min_value=300, max_value=3600, value=600, step=300)

# Display current USD to INR rate prominently
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    try:
        live_rate = get_current_rate_with_fallback()
        st.metric(
            label="Current USD to INR Rate", 
            value=f"₹{live_rate:.2f} INR",
            help="Live rate with automatic fallback between Alpha Vantage and Yahoo Finance"
        )
        st.markdown(
            f"""
            <div style='text-align: center; color: gray; font-size: small;'>
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"⚠️ Error fetching live rate: {e}")
        st.info("Please check your API keys and internet connection.")
        live_rate = 83.0  # Fallback rate for calculations

st.markdown("---")

# --- Virtual Portfolio Display ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("💰 Virtual Portfolio Status")
    current_portfolio_value_inr = st.session_state.inr_balance + (st.session_state.usd_held * live_rate)

    portfolio_col1, portfolio_col2, portfolio_col3 = st.columns(3)
    with portfolio_col1:
        st.metric(label="INR Balance", value=f"₹{st.session_state.inr_balance:,.2f}")
    with portfolio_col2:
        st.metric(label="USD Held", value=f"${st.session_state.usd_held:,.2f}")
    with portfolio_col3:
        st.metric(label="Total Value (INR)", value=f"₹{current_portfolio_value_inr:,.2f}")

    st.button("Reset Portfolio", on_click=reset_portfolio)

# --- Live Chart Section ---
with col2:
    st.header(f"📊 Live USD/INR Chart ({selected_timeframe_label})")
    
    # Determine cache TTL based on timeframe
    if data_source_key == 'alphavantage':
        if selected_timeframe in ['1min', '5min']:
            cache_ttl = 60  # 1 minute for very short timeframes
        elif selected_timeframe in ['15min', '30min']:
            cache_ttl = 300  # 5 minutes for medium timeframes
        elif selected_timeframe == '60min':
            cache_ttl = 600  # 10 minutes for hourly
        else:
            cache_ttl = 3600  # 1 hour for daily
    else:
        cache_ttl = 3600  # 1 hour for Yahoo Finance

    @st.cache_data(ttl=cache_ttl)
    def get_and_plot_live_candlesticks_with_signals(timeframe, data_source, short_sma, long_sma):
        """
        Fetches live candlestick data, calculates SMAs, generates signals,
        and creates a Plotly chart.
        """
        try:
            # Get live data
            candlestick_df = get_live_candlestick_data(timeframe=timeframe, data_source=data_source)

            if not candlestick_df.empty:
                # Calculate SMAs
                candlestick_df['SMA_Short'] = candlestick_df['Close'].rolling(window=short_sma).mean()
                candlestick_df['SMA_Long'] = candlestick_df['Close'].rolling(window=long_sma).mean()

                # Generate Signals
                candlestick_df['Signal'] = 0
                candlestick_df.loc[candlestick_df['SMA_Short'] > candlestick_df['SMA_Long'], 'Signal'] = 1
                candlestick_df.loc[candlestick_df['SMA_Short'] < candlestick_df['SMA_Long'], 'Signal'] = -1

                # Identify crossover points
                candlestick_df['Position'] = candlestick_df['Signal'].diff()

                # Trading Simulation
                current_inr_balance = 100000.0
                current_usd_held = 0.0
                simulation_trade_history = []
                trade_amount_inr = 10000.0

                buy_markers_x = []
                buy_markers_y = []
                sell_markers_x = []
                sell_markers_y = []

                # Simulate trades
                for i, row in candlestick_df.iterrows():
                    if row['Position'] == 1:  # Buy signal
                        if current_inr_balance >= trade_amount_inr:
                            usd_bought = trade_amount_inr / row['Close']
                            current_inr_balance -= trade_amount_inr
                            current_usd_held += usd_bought
                            simulation_trade_history.append({
                                'Time': i.strftime('%Y-%m-%d %H:%M:%S'),
                                'Type': 'BUY',
                                'Amount (INR)': trade_amount_inr,
                                'USD Bought': f"{usd_bought:.2f}",
                                'Price': f"₹{row['Close']:.2f}",
                                'INR Balance': f"₹{current_inr_balance:,.2f}",
                                'USD Held': f"${current_usd_held:,.2f}"
                            })
                            buy_markers_x.append(i)
                            buy_markers_y.append(row['Close'])
                    elif row['Position'] == -1:  # Sell signal
                        if current_usd_held > 0:
                            inr_sold = current_usd_held * row['Close']
                            current_inr_balance += inr_sold
                            usd_sold = current_usd_held
                            current_usd_held = 0.0
                            simulation_trade_history.append({
                                'Time': i.strftime('%Y-%m-%d %H:%M:%S'),
                                'Type': 'SELL',
                                'Amount (INR)': f"{inr_sold:,.2f}",
                                'USD Sold': f"{usd_sold:.2f}",
                                'Price': f"₹{row['Close']:.2f}",
                                'INR Balance': f"₹{current_inr_balance:,.2f}",
                                'USD Held': f"${current_usd_held:,.2f}"
                            })
                            sell_markers_x.append(i)
                            sell_markers_y.append(row['Close'])

                # Store simulation results
                st.session_state.inr_balance_sim = current_inr_balance
                st.session_state.usd_held_sim = current_usd_held
                st.session_state.trade_history_sim = simulation_trade_history

                # Create the plot
                fig = go.Figure()

                # Add candlestick chart
                fig.add_trace(go.Candlestick(
                    x=candlestick_df.index,
                    open=candlestick_df['Open'],
                    high=candlestick_df['High'],
                    low=candlestick_df['Low'],
                    close=candlestick_df['Close'],
                    name='USD/INR',
                    increasing_line_color='green',
                    decreasing_line_color='red'
                ))

                # Add SMAs
                fig.add_trace(go.Scatter(
                    x=candlestick_df.index,
                    y=candlestick_df['SMA_Short'],
                    mode='lines',
                    name=f'SMA {short_sma}',
                    line=dict(color='blue', width=2)
                ))

                fig.add_trace(go.Scatter(
                    x=candlestick_df.index,
                    y=candlestick_df['SMA_Long'],
                    mode='lines',
                    name=f'SMA {long_sma}',
                    line=dict(color='orange', width=2)
                ))

                # Add buy/sell signals
                if buy_markers_x:
                    fig.add_trace(go.Scatter(
                        x=buy_markers_x,
                        y=buy_markers_y,
                        mode='markers',
                        marker=dict(symbol='triangle-up', size=12, color='green'),
                        name='Buy Signal'
                    ))

                if sell_markers_x:
                    fig.add_trace(go.Scatter(
                        x=sell_markers_x,
                        y=sell_markers_y,
                        mode='markers',
                        marker=dict(symbol='triangle-down', size=12, color='red'),
                        name='Sell Signal'
                    ))

                # Update layout
                fig.update_layout(
                    title=f'USD/INR Live Chart - {selected_timeframe_label} ({data_source})',
                    xaxis_title='Time',
                    yaxis_title='Price (INR)',
                    xaxis_rangeslider_visible=False,
                    hovermode="x unified",
                    height=500,
                    showlegend=True,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )

                # Auto-scale Y-axis to current price range
                if not candlestick_df.empty:
                    recent_data = candlestick_df.tail(50)  # Last 50 data points
                    y_min = recent_data[['Low', 'SMA_Short', 'SMA_Long']].min().min()
                    y_max = recent_data[['High', 'SMA_Short', 'SMA_Long']].max().max()
                    y_range = y_max - y_min
                    fig.update_yaxes(range=[y_min - 0.1 * y_range, y_max + 0.1 * y_range])

                return fig, candlestick_df

            else:
                st.warning("No data available for the selected timeframe.")
                return None, pd.DataFrame()

        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
            return None, pd.DataFrame()

    # Display the chart
    try:
        fig, chart_data = get_and_plot_live_candlesticks_with_signals(
            timeframe=selected_timeframe,
            data_source=data_source_key,
            short_sma=short_sma_period,
            long_sma=long_sma_period
        )
        
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
            
            # Display data info
            if not chart_data.empty:
                st.info(f"📊 Showing {len(chart_data)} data points | Latest: {chart_data.index[-1].strftime('%Y-%m-%d %H:%M:%S')} | Price: ₹{chart_data['Close'].iloc[-1]:.2f}")
        
        # Auto-refresh functionality
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
            
    except Exception as e:
        st.error(f"Failed to load chart: {str(e)}")
        st.info("Please check your Alpha Vantage API key and internet connection.")

st.markdown("---")

# --- Display Simulation Results ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📈 Trading Simulation Results")
    if 'inr_balance_sim' in st.session_state:
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        with sim_col1:
            st.metric("Final INR Balance", f"₹{st.session_state.inr_balance_sim:,.2f}")
        with sim_col2:
            st.metric("Final USD Held", f"${st.session_state.usd_held_sim:,.2f}")
        with sim_col3:
            total_value = st.session_state.inr_balance_sim + (st.session_state.usd_held_sim * live_rate)
            profit_loss = total_value - 100000.0
            st.metric("Total Portfolio Value", f"₹{total_value:,.2f}", delta=f"₹{profit_loss:,.2f}")

with col2:
    st.subheader("📋 Recent Trade History")
    if 'trade_history_sim' in st.session_state and st.session_state.trade_history_sim:
        trade_df = pd.DataFrame(st.session_state.trade_history_sim)
        st.dataframe(trade_df.tail(10), use_container_width=True)
    else:
        st.info("No trades executed yet in the current simulation.")

st.markdown("---")

# --- Chat Section ---
st.header("💬 AI Trading Assistant")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**🧠 Your Question:** {message['content']}")
    else:
        st.markdown(f"**🤖 Response:** {message['content']}")

# --- Input Form for Chat ---
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("🧠 Ask about USD/INR rates, trading signals, or forex trends:", key="user_question_input")
    submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        if user_input.lower() == 'exit':
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "bot", "content": "Goodbye! The bot session has ended."})
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("🤖 Thinking..."):
                llm_response = ""
                # Check if the user's question explicitly asks for the rate
                if "usd" in user_input.lower() and "inr" in user_input.lower() and ("price" in user_input.lower() or "rate" in user_input.lower()):
                    try:
                        rate = get_current_rate_with_fallback()
                        llm_response = f"The current USD to INR exchange rate is ₹{rate:.2f}. This rate is fetched live from our data sources."
                    except Exception:
                        llm_response = "I couldn't fetch the live USD to INR rate at the moment, but I can still discuss forex trends and trading strategies."
                else:
                    # Use the conversational chain for other questions
                    llm_response = st.session_state.conversation.predict(input=user_input)

                st.session_state.chat_history.append({"role": "bot", "content": llm_response})

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: small;'>
    💹 USD/INR Trading Bot | Powered by Alpha Vantage API & Streamlit | 
    Set ALPHA_VANTAGE_API_KEY environment variable for intraday data
    </div>
    """,
    unsafe_allow_html=True
)

