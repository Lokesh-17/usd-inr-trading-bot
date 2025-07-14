# streamlit_app.py

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go # For candlestick chart
import numpy as np # For numerical operations

# Ensure data_fetcher.py is in the same directory and contains get_usd_inr_rate()
from data_fetcher import get_usd_inr_rate, get_yfinance_candlestick_data

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

# --- Debugging print statement ---
# This will print to your terminal where you run 'streamlit run'
print(f"DEBUG: HF_TOKEN value from environment: {hf_token_value}")

if not hf_token_value:
    st.error("Error: Hugging Face API token (HF_TOKEN) not found. Please set it as an environment variable.")
    st.info("Example: In your terminal, run `export HF_TOKEN=\"YOUR_ACTUAL_HF_TOKEN_HERE\"`")
    st.stop() # Stop the app if token is missing

# Assign the retrieved value to HF_TOKEN for use in HuggingFaceHub
HF_TOKEN = hf_token_value

# Initialize HuggingFaceHub LLM
try:
    llm = HuggingFaceHub(
        repo_id="HuggingFaceTB/SmolLM3-3B", # Using the previous Hugging Face model
        huggingfacehub_api_token=HF_TOKEN,
        model_kwargs={"temperature": 0.7, "max_new_tokens": 256}
    )
except Exception as e:
    st.error(f"Error initializing HuggingFaceHub LLM: {e}")
    st.info("Please check your HF_TOKEN and ensure the model 'HuggingFaceTB/SmolLM3-3B' is accessible.")
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
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("💹 USD/INR Trading Bot with Virtual Portfolio")
st.markdown("Ask me anything about USD to INR exchange rates or forex trends.")

# Display current USD to INR rate prominently
st.markdown("---")
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
    st.info("Ensure your `data_fetcher.py` is correctly set up to retrieve the rate.")
st.markdown("---")


# --- Virtual Portfolio Display ---
st.header("💰 Virtual Portfolio Status")
current_portfolio_value_usd = st.session_state.usd_held
current_portfolio_value_inr = st.session_state.inr_balance + (st.session_state.usd_held * live_rate)

col_bal1, col_bal2, col_bal3 = st.columns(3)
with col_bal1:
    st.metric(label="INR Balance", value=f"₹{st.session_state.inr_balance:,.2f}")
with col_bal2:
    st.metric(label="USD Held", value=f"${st.session_state.usd_held:,.2f}")
with col_bal3:
    st.metric(label="Total Portfolio Value (INR)", value=f"₹{current_portfolio_value_inr:,.2f}")

st.button("Reset Portfolio", on_click=reset_portfolio)
st.markdown("---")


# --- Historical Candlestick Chart Section (USD/INR) ---
st.header("📊 Historical USD/INR Candlestick Chart (YFinance)")

# Selectbox for time period for YFinance
time_period_options = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "5 Years": "5y",
    "Max": "max"
}
selected_period_label = st.selectbox(
    "Select Time Period for USD/INR Chart:",
    list(time_period_options.keys()),
    index=0 # Default to 1 Month
)
selected_period_yf = time_period_options[selected_period_label]

st.info("Note: YFinance typically provides daily candlestick data for USD/INR. Intraday intervals are not available.")

# Sliders for SMA periods
col1, col2 = st.columns(2)
with col1:
    short_sma_period = st.slider("Short SMA Period (Days)", min_value=5, max_value=50, value=20, step=1)
with col2:
    long_sma_period = st.slider("Long SMA Period (Days)", min_value=20, max_value=200, value=50, step=5)

if short_sma_period >= long_sma_period:
    st.warning("Short SMA period should be less than Long SMA period for meaningful analysis.")


# Cache the data for a reasonable period (e.g., 1 hour for historical data)
@st.cache_data(ttl=3600) # Cache for 1 hour
def get_and_plot_yfinance_candlesticks_with_signals(symbol, period, short_sma, long_sma):
    """
    Fetches YFinance candlestick data, calculates SMAs, generates signals,
    and creates a Plotly chart.
    """
    try:
        # Use '1d' interval for daily candles, as more granular is usually not available for forex
        candlestick_df = get_yfinance_candlestick_data(symbol=symbol, period=period, interval="1d")

        if not candlestick_df.empty:
            # Calculate SMAs
            candlestick_df['SMA_Short'] = candlestick_df['Close'].rolling(window=short_sma).mean()
            candlestick_df['SMA_Long'] = candlestick_df['Close'].rolling(window=long_sma).mean()

            # Generate Signals
            # Initialize 'Signal' column: 0 for no signal, 1 for buy, -1 for sell
            candlestick_df['Signal'] = 0
            # Condition for Buy: Short SMA crosses above Long SMA
            candlestick_df.loc[candlestick_df['SMA_Short'] > candlestick_df['SMA_Long'], 'Signal'] = 1
            # Condition for Sell: Short SMA crosses below Long SMA
            candlestick_df.loc[candlestick_df['SMA_Short'] < candlestick_df['SMA_Long'], 'Signal'] = -1

            # Identify actual crossover points for plotting and trading
            # A '1' in 'Position' means a buy signal, '-1' means a sell signal
            candlestick_df['Position'] = candlestick_df['Signal'].diff()

            # --- Trading Simulation ---
            # Reset portfolio for this simulation run based on selected chart period
            # This ensures the simulation starts fresh with the displayed data
            current_inr_balance = 100000.0 # Starting balance for simulation
            current_usd_held = 0.0
            simulation_trade_history = []
            trade_amount_inr = 10000.0 # Amount of INR to use for each trade

            buy_markers_x = []
            buy_markers_y = []
            sell_markers_x = []
            sell_markers_y = []

            # Iterate through the DataFrame to simulate trades
            for i, row in candlestick_df.iterrows():
                if row['Position'] == 1: # Buy signal
                    if current_inr_balance >= trade_amount_inr:
                        usd_bought = trade_amount_inr / row['Close']
                        current_inr_balance -= trade_amount_inr
                        current_usd_held += usd_bought
                        simulation_trade_history.append({
                            'Date': i.strftime('%Y-%m-%d'),
                            'Type': 'BUY',
                            'Amount (INR)': trade_amount_inr,
                            'USD Bought': f"{usd_bought:.2f}",
                            'Price': f"₹{row['Close']:.2f}",
                            'INR Balance': f"₹{current_inr_balance:,.2f}",
                            'USD Held': f"${current_usd_held:,.2f}"
                        })
                        buy_markers_x.append(i)
                        buy_markers_y.append(row['Close'])
                    # else: st.info("Not enough INR to buy.") # Don't show in loop
                elif row['Position'] == -1: # Sell signal
                    if current_usd_held > 0:
                        # Sell all held USD for simplicity
                        inr_sold = current_usd_held * row['Close']
                        current_inr_balance += inr_sold
                        usd_sold = current_usd_held
                        current_usd_held = 0.0 # Sold all USD
                        simulation_trade_history.append({
                            'Date': i.strftime('%Y-%m-%d'),
                            'Type': 'SELL',
                            'Amount (INR)': f"{inr_sold:,.2f}",
                            'USD Sold': f"{usd_sold:.2f}",
                            'Price': f"₹{row['Close']:.2f}",
                            'INR Balance': f"₹{current_inr_balance:,.2f}",
                            'USD Held': f"${current_usd_held:,.2f}"
                        })
                        sell_markers_x.append(i)
                        sell_markers_y.append(row['Close'])
                    # else: st.info("No USD to sell.") # Don't show in loop

            # --- Update global session state with simulation results ---
            # This is to show the *final* balance for the selected period's simulation
            # Note: This will overwrite the main portfolio display if you change chart period
            # For a persistent portfolio, trade execution would be outside this cached function
            st.session_state.inr_balance_sim = current_inr_balance
            st.session_state.usd_held_sim = current_usd_held
            st.session_state.trade_history_sim = simulation_trade_history


            # --- Plotting ---
            fig = go.Figure(data=[go.Candlestick(
                x=candlestick_df.index,
                open=candlestick_df['Open'],
                high=candlestick_df['High'],
                low=candlestick_df['Low'],
                close=candlestick_df['Close'],
                name='Candlesticks'
            )])

            # Add Short SMA
            fig.add_trace(go.Scatter(
                x=candlestick_df.index,
                y=candlestick_df['SMA_Short'],
                mode='lines',
                name=f'SMA {short_sma}',
                line=dict(color='blue', width=1)
            ))

            # Add Long SMA
            fig.add_trace(go.Scatter(
                x=candlestick_df.index,
                y=candlestick_df['SMA_Long'],
                mode='lines',
                name=f'SMA {long_sma}',
                line=dict(color='orange', width=1)
            ))

            # Add Buy signals (from simulation)
            fig.add_trace(go.Scatter(
                x=buy_markers_x,
                y=buy_markers_y,
                mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='green'),
                name='Simulated Buy'
            ))

            # Add Sell signals (from simulation)
            fig.add_trace(go.Scatter(
                x=sell_markers_x,
                y=sell_markers_y,
                mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'),
                name='Simulated Sell'
            ))


            fig.update_layout(
                title=f'{symbol} Candlestick Chart with SMAs & Simulated Trades ({selected_period_label} - Daily)',
                xaxis_title='Date',
                yaxis_title='Price (INR)',
                xaxis_rangeslider_visible=False, # Hide the range slider for cleaner look
                hovermode="x unified" # Show hover info for all traces at a given x-coordinate
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display Simulation Results below the chart
            st.subheader("📈 Simulation Results for Selected Period")
            st.write(f"**Final INR Balance:** ₹{st.session_state.inr_balance_sim:,.2f}")
            st.write(f"**Final USD Held:** ${st.session_state.usd_held_sim:,.2f}")
            st.write(f"**Total Simulated Portfolio Value (at end of period):** ₹{st.session_state.inr_balance_sim + (st.session_state.usd_held_sim * candlestick_df['Close'].iloc[-1]):,.2f}")

            if st.session_state.trade_history_sim:
                st.subheader("Trade History (Simulation)")
                trade_df = pd.DataFrame(st.session_state.trade_history_sim)
                st.dataframe(trade_df)
            else:
                st.info("No trades executed in this simulation period.")


        else:
            st.info("No historical candlestick data available to display for the selected period.")
    except Exception as e:
        st.error(f"Error displaying USD/INR candlestick chart: {e}")

# Call the function to display the chart for USD/INR with signals
get_and_plot_yfinance_candlesticks_with_signals(
    symbol="USDINR=X",
    period=selected_period_yf,
    short_sma=short_sma_period,
    long_sma=long_sma_period
)

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

    if submit_button and user_input: # Process only when button is clicked and input is not empty
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
                        rate = get_usd_inr_rate()
                        llm_response = f"The current USD to INR exchange rate is ₹{rate:.2f}."
                    except Exception:
                        llm_response = "I couldn't fetch the live USD to INR rate at the moment, but I can still discuss forex trends."
                else:
                    # Use the conversational chain for other questions
                    llm_response = st.session_state.conversation.predict(input=user_input)

                st.session_state.chat_history.append({"role": "bot", "content": llm_response})

