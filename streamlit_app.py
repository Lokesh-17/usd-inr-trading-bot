# streamlit_app.py

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time # For sleep in auto-refresh

# Firebase imports
from firebase_admin import credentials, initialize_app
from firebase_admin import firestore
from firebase_admin import auth

# Ensure data_fetcher.py is in the same directory
from data_fetcher import get_usd_inr_rate, get_alpha_vantage_candlestick_data

# Import LangChain components for HuggingFaceHub
from langchain_community.llms import HuggingFaceHub
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# --- Firebase Initialization (Only once) ---
# Global variables provided by Canvas for Firebase
app_id = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
firebase_config = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{}');
initial_auth_token = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

if not firebase_admin._apps:
    try:
        # Use credentials from firebase_config
        cred = credentials.Certificate(firebase_config)
        initialize_app(cred)
        st.success("Firebase initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
        st.stop()

db = firestore.client()

# --- User Authentication (Anonymous for simplicity) ---
# This ensures we have a userId for Firestore operations
@st.cache_resource
def get_auth_client():
    return auth.Client(app=firebase_admin.get_app())

auth_client = get_auth_client()

# Get or create user ID
if 'user_id' not in st.session_state:
    try:
        if initial_auth_token:
            # Sign in with custom token if provided (e.g., from Canvas environment)
            decoded_token = auth_client.verify_id_token(initial_auth_token)
            st.session_state.user_id = decoded_token['uid']
            st.session_state.is_authenticated = True
            print(f"DEBUG: Signed in with custom token. User ID: {st.session_state.user_id}")
        else:
            # Sign in anonymously if no custom token
            anon_user = auth_client.create_user(uid=str(uuid.uuid4())) # Create a new anonymous user
            st.session_state.user_id = anon_user.uid
            st.session_state.is_authenticated = True
            print(f"DEBUG: Signed in anonymously. User ID: {st.session_state.user_id}")
    except Exception as e:
        st.error(f"Error during authentication: {e}")
        st.session_state.user_id = "anonymous_user" # Fallback
        st.session_state.is_authenticated = False
        print(f"DEBUG: Authentication failed, using fallback user ID. Error: {e}")
else:
    print(f"DEBUG: User already authenticated. User ID: {st.session_state.user_id}")

user_id = st.session_state.user_id
st.sidebar.write(f"Logged in as: {user_id}")


# --- Firestore Helpers ---
@st.cache_data(ttl=60) # Cache portfolio data for 1 minute
def load_portfolio_from_firestore(uid):
    doc_ref = db.collection(f"artifacts/{app_id}/users/{uid}/portfolio").document("current_portfolio")
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        print(f"DEBUG: Loaded portfolio: {data}")
        return data.get('inr_balance', 100000.0), data.get('usd_held', 0.0)
    print("DEBUG: No portfolio found, initializing default.")
    return 100000.0, 0.0

def save_portfolio_to_firestore(uid, inr_balance, usd_held):
    doc_ref = db.collection(f"artifacts/{app_id}/users/{uid}/portfolio").document("current_portfolio")
    doc_ref.set({'inr_balance': inr_balance, 'usd_held': usd_held})
    print(f"DEBUG: Saved portfolio: INR={inr_balance}, USD={usd_held}")

@st.cache_data(ttl=60) # Cache trade history for 1 minute
def load_trade_history_from_firestore(uid):
    doc_ref = db.collection(f"artifacts/{app_id}/users/{uid}/trade_history").document("history_list")
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        # Firestore stores lists as arrays, but sometimes complex objects need JSON stringify
        history_json = data.get('trades', '[]')
        try:
            return json.loads(history_json) if isinstance(history_json, str) else history_json
        except json.JSONDecodeError:
            print(f"WARNING: Could not decode trade history JSON: {history_json}")
            return []
    print("DEBUG: No trade history found, initializing empty.")
    return []

def save_trade_history_to_firestore(uid, trade_history):
    doc_ref = db.collection(f"artifacts/{app_id}/users/{uid}/trade_history").document("history_list")
    # Convert to JSON string if it contains complex objects not directly supported by Firestore
    doc_ref.set({'trades': json.dumps(trade_history)})
    print(f"DEBUG: Saved trade history ({len(trade_history)} entries)")

import json # Import json for stringify/parse
import uuid # For anonymous user ID if auth token is not present

# --- Initialize Virtual Portfolio in Session State (and load from Firestore) ---
if 'inr_balance' not in st.session_state:
    st.session_state.inr_balance, st.session_state.usd_held = load_portfolio_from_firestore(user_id)
if 'usd_held' not in st.session_state: # Redundant check but harmless
    pass
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = load_trade_history_from_firestore(user_id)

def reset_portfolio():
    """Resets the virtual portfolio to initial values and clears Firestore."""
    st.session_state.inr_balance = 100000.0
    st.session_state.usd_held = 0.0
    st.session_state.trade_history = []
    save_portfolio_to_firestore(user_id, st.session_state.inr_balance, st.session_state.usd_held)
    save_trade_history_to_firestore(user_id, st.session_state.trade_history)
    st.success("Portfolio reset successfully!")
    st.rerun() # Rerun to reflect changes


# --- Hugging Face LLM Setup ---
hf_token_value = os.getenv("HF_TOKEN")
if not hf_token_value:
    st.error("Error: Hugging Face API token (HF_TOKEN) not found. Please set it as an environment variable.")
    st.info("Example: In your terminal, run `export HF_TOKEN=\"YOUR_ACTUAL_HF_TOKEN_HERE\"`")
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
st.header("💰 Virtual Portfolio Status (Persistent)")
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

# Cache the data for 5 minutes (300 seconds) to respect Alpha Vantage free tier limits
@st.cache_data(ttl=300)
def get_and_plot_alpha_vantage_candlesticks_with_signals(symbol, to_symbol, interval, short_sma, long_sma):
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
                title=f'{symbol}/{to_symbol} Candlestick Chart with SMAs ({selected_interval_label})',
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

# Sliders for SMA periods
col_sma1, col_sma2 = st.columns(2)
with col_sma1:
    short_sma_period = st.slider("Short SMA Period (Candles)", min_value=5, max_value=50, value=20, step=1)
with col_sma2:
    long_sma_period = st.slider("Long SMA Period (Candles)", min_value=20, max_value=200, value=50, step=5)

if short_sma_period >= long_sma_period:
    st.warning("Short SMA period should be less than Long SMA period for meaningful analysis.")


# Call the function to display the chart for USD/INR with signals
get_and_plot_alpha_vantage_candlesticks_with_signals(
    symbol="USD",
    to_symbol="INR",
    interval=selected_interval_av,
    short_sma=short_sma_period,
    long_sma=long_sma_period
)

st.markdown("---")


# --- Manual Trade Execution (Updates Persistent Portfolio) ---
st.header("🛒 Manual Trade Execution")
st.markdown("Execute trades directly to update your persistent virtual portfolio.")

col_trade_amount, col_trade_buttons = st.columns([0.7, 0.3])
with col_trade_amount:
    trade_amount_usd = st.number_input("Amount to Trade (USD)", min_value=0.01, value=100.0, step=10.0)

with col_trade_buttons:
    st.write("") # Spacer
    st.write("") # Spacer
    if st.button("Buy USD"):
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
            save_portfolio_to_firestore(user_id, st.session_state.inr_balance, st.session_state.usd_held)
            save_trade_history_to_firestore(user_id, st.session_state.trade_history)
            st.success(f"Successfully bought ${trade_amount_usd:.2f} USD!")
            st.rerun()
        else:
            st.error("Insufficient INR balance to buy USD.")

    if st.button("Sell USD"):
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
            save_portfolio_to_firestore(user_id, st.session_state.inr_balance, st.session_state.usd_held)
            save_trade_history_to_firestore(user_id, st.session_state.trade_history)
            st.success(f"Successfully sold ${trade_amount_usd:.2f} USD!")
            st.rerun()
        else:
            st.error("Insufficient USD held to sell.")

st.subheader("Persistent Trade History")
if st.session_state.trade_history:
    trade_df_persistent = pd.DataFrame(st.session_state.trade_history)
    st.dataframe(trade_df_persistent)
else:
    st.info("No persistent trade history yet.")
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
                try:
                    # Attempt to get the latest SMA values for LLM context
                    # This requires re-fetching or passing data, which can be complex.
                    # For simplicity, we'll just tell it about the current rate.
                    chart_context = f"The current USD to INR rate is ₹{live_rate:.2f}. "
                    # If you want to feed SMA values, you'd need to calculate them here
                    # or pass them from the cached chart function.
                except Exception:
                    pass # Ignore if live_rate not available

                llm_input_with_context = f"{chart_context}Human: {user_input}"
                llm_response = st.session_state.conversation.predict(input=llm_input_with_context)

                st.session_state.chat_history.append({"role": "bot", "content": llm_response})

