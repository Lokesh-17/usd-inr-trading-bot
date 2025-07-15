# streamlit_app.py

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import datetime # For timestamps
import json # For JSON serialization/deserialization
import uuid # For anonymous user ID

# Firebase imports
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Ensure data_fetcher.py is in the same directory
from data_fetcher import get_usd_inr_rate, get_alpha_vantage_candlestick_data

# Import LangChain components for HuggingFaceHub
from langchain_community.llms import HuggingFaceHub
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# --- Firebase Initialization (Only once) ---
# Global variables provided by Canvas for Streamlit Cloud
app_id = os.getenv('__app_id', 'default-app-id')
initial_auth_token = os.getenv('__initial_auth_token', None)

# !!! WARNING: SECURITY RISK !!!
# This Firebase service account JSON is hardcoded directly into the script.
# This is done for debugging purposes to bypass persistent issues with Streamlit secrets.
# For a production application, it is STRONGLY RECOMMENDED to keep this in Streamlit secrets
# or another secure environment variable, and NOT directly in your codebase.
firebase_config = {
  "type": "service_account",
  "project_id": "usdinrtradingbot",
  "private_key_id": "72c53821c3827e204ae7d035fa2efb5a51ebde13",
  # Using a raw string (r"...") and explicit \n to ensure correct interpretation of the private key
  "private_key": r"-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDFqjXST7ptIB2g\nNVZCNoaY3zylwaRCWXR878LmPLVVJJboGKDlQGevW87OZ6V4sWvBycy7kUkyzWIC\nSN9QcotNRb+6RhccsOKeHPWYTlG2BmUcglQR9/LovJcnTHdMvK6+FBxIGaDm7NBu\naNtNj+jkvYGrqeK/9G/wtvRQ+VUYFAEWh/nRvG8y5WOfjIVmMq5skLaE1NaXG2ob\n9nANwRDNZwVSBqc+fie9WsaqF7/mXG693Zadrl4+xU3D0fEY9Zsx2eX1IDerg+2j\nI+E1CWGjMQ8FrJPwEi7e01ctVJZbhadMA19zECozJnv4yTm0GemfUrgkfiMNoa7p\nyot9xiwjAgMBAAECggEAD/avUmpk+dOKVk99xWrbk59n1FKKE7UKHt2gOxxJCsoh\n3oxqph59oTXEGHsEwUrBk0zbGi+MHqxj+h+XhXWSwYKyDsxX/oBcn6diwFJcRVvz\n24m9BMHRHjG+RWARZyL6kS2qRmUSJRmYEGqrLMhEEgEqEUqZnlC9Sk6u9uvZZFBz\nhZfDNazM7WWg6KS7+IFtvELYud4wvgZFu34PWb765seJqy8Kaz/WnIU0rW6vipI\naWQeY9hsg1ZmUeVkqlLXiMlLmiInythREd7w0ryGJPezTr74lam8463w5v0Srcw4\n9cZ5TFifxCo3zCpUiuxqxRg/oADSztmWZ+3CMZ0jWQKBgQDw/PrOAsRffY+/JK5y\nwuy9q5FZ3kou2hbjsv55huUbkcp7epKcpDMqCdLaSuLesXfUyu4Dq17pxXD92k2x\nIf1WRR7jc3mRCApnRw2l1TIV6wHKtyeDPvXTITgicu9JMixQNnlozneCYFzSBbbl\nBS0yKhNpRabtsyiKAlmtVHdZCQKBgQDR+lte1LdVOg063WiuC+FhmgqwRGiPG+fQ\nj3Z53jHpQfIcp4jthawzJl/KJ3HRFMq+zfMTOfOKL6+xzSONeIughrMr770UsLS4\n8212BOr6nbHm0LooEBi6cJLNXuDANZlG/nqekReInM10VwplhNrqipWd8FYDLAmh\nCbWPP4yCywKBgQCcK+XBMeve0jkgrv3aY1YWiKP2cGb0u+LPhwUA7pl052Mn6EQw\n/PwnRxx82MDzfmDg5u2eNSWaK5jQ+fMVUqihisO8tO3YPjS3v0Up7eK6b4TGwTD7\nDgcy3rlJIeDON5SeGt9NO1gZhqdAd/GRs2wZsUjJFRlbu5oO7fz9pdp+OQKBgQCA\nLKf7wjNLJg2PYjoVDBF/J63gnVGKEgm2iOxUResHrQaisS3nd5J/Aqy0VNGoRF3i\njQsVMGnWb3d7PHK4V947lh3m8wfjil43C/lEcooRg5NmBwGrlO/TVwZ1sLXW/qDa\n8lpdUsofzT+pBbzF7YxIYWIlL+EBPK+ACtI2aB9YcwKBgDZSPJ11Flm0DFv/YwIo\npjE3x12/JEy9BKXlxml6OacPOc133MCA5qcwVVD3QZhwmp4jjH+uL6smy4DMVImi\n+0vlgai9FCn3a1JGlvWnL6iBpLb6Mc9/0nXEkj3vw+YOh1hda2A+fXuN1a2Cpe4N\nOypOGoBbMfzdsrnQL0HdD7vC\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@usdinrtradingbot.iam.gserviceaccount.com",
  "client_id": "113166061108323668503",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40usdinrtradingbot.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
# End of hardcoded Firebase config

# --- ULTIMATE DIAGNOSTIC PRINTS ---
st.header("Firebase Config Debug Information (ULTIMATE DIAGNOSTIC)")
st.write("Type of firebase_config:", type(firebase_config))
st.write("Raw repr() of firebase_config:")
st.code(repr(firebase_config), language='python') # Use st.code for raw string repr
st.write("firebase_config content (st.json):")
st.json(firebase_config) # Still good for pretty printing

if "type" in firebase_config:
    st.write("firebase_config['type'] exists.")
    st.write("Value of firebase_config['type']:", firebase_config["type"])
    if firebase_config["type"] == "service_account":
        st.success("SUCCESS: 'type' field is 'service_account' as expected!")
    else:
        st.error(f"ERROR: 'type' field is '{firebase_config['type']}' but expected 'service_account'!")
else:
    st.error("ERROR: 'type' field is NOT found in firebase_config!")

if "private_key" in firebase_config:
    st.write("Length of private_key:", len(firebase_config["private_key"]))
    st.write("Starts with:", firebase_config["private_key"][:30])
    st.write("Ends with:", firebase_config["private_key"][-30:])
else:
    st.error("ERROR: 'private_key' field is NOT found in firebase_config!")

st.write("--- End Firebase Config Debug ---")
# --- END ULTIMATE DIAGNOSTIC PRINTS ---


if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        st.success("Firebase initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
        st.info("Ensure your Firebase config is correctly set in Streamlit Cloud secrets.")
        st.stop() # Stop the app if Firebase init fails

db = firestore.client()

# --- User Authentication (Anonymous for simplicity) ---
# This ensures we have a userId for Firestore operations
@st.cache_resource
def get_auth_client_instance():
    return auth.Client(app=firebase_admin.get_app())

auth_client = get_auth_client_instance()

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
            # Note: create_user requires Firebase Admin SDK setup for user management.
            # For anonymous, we'll generate a UUID and use it as a pseudo-UID for Firestore
            # as direct anonymous sign-in via client SDK is not what we're doing here.
            # For full anonymous auth, you'd integrate Firebase JS SDK on frontend.
            st.session_state.user_id = "anon_" + str(uuid.uuid4())
            st.session_state.is_authenticated = False # Not truly Firebase authenticated
            print(f"DEBUG: Using generated anonymous User ID: {st.session_state.user_id}")
    except Exception as e:
        st.error(f"Error during authentication/user ID generation: {e}")
        st.session_state.user_id = "fallback_user" # Fallback
        st.session_state.is_authenticated = False
        print(f"DEBUG: Authentication failed, using fallback user ID. Error: {e}")
else:
    print(f"DEBUG: User ID already in session state: {st.session_state.user_id}")

user_id = st.session_state.user_id
st.sidebar.write(f"User ID: {user_id}")


# --- Firestore Helpers ---
# Using st.cache_data for loading to reduce Firestore reads on reruns
# but ttl is short to keep data relatively fresh.
@st.cache_data(ttl=60)
def load_portfolio_from_firestore(uid):
    try:
        doc_ref = db.collection(f"artifacts/{app_id}/users/{uid}/portfolio").document("current_portfolio")
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            print(f"DEBUG: Loaded portfolio: {data}")
            return data.get('inr_balance', 100000.0), data.get('usd_held', 0.0)
        print("DEBUG: No portfolio found, initializing default.")
        return 100000.0, 0.0
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return 100000.0, 0.0 # Return default on error

def save_portfolio_to_firestore(uid, inr_balance, usd_held):
    try:
        doc_ref = db.collection(f"artifacts/{app_id}/users/{uid}/portfolio").document("current_portfolio")
        doc_ref.set({'inr_balance': inr_balance, 'usd_held': usd_held})
        print(f"DEBUG: Saved portfolio: INR={inr_balance}, USD={usd_held}")
    except Exception as e:
        st.error(f"Error saving portfolio: {e}")

@st.cache_data(ttl=60)
def load_trade_history_from_firestore(uid):
    try:
        doc_ref = db.collection(f"artifacts/{app_id}/users/{uid}/trade_history").document("history_list")
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            history_json = data.get('trades', '[]')
            try:
                return json.loads(history_json) if isinstance(history_json, str) else history_json
            except json.JSONDecodeError:
                print(f"WARNING: Could not decode trade history JSON: {history_json}")
                return []
        print("DEBUG: No trade history found, initializing empty.")
        return []
    except Exception as e:
        st.error(f"Error loading trade history: {e}")
        return [] # Return empty on error

def save_trade_history_to_firestore(uid, trade_history):
    try:
        doc_ref = db.collection(f"artifacts/{app_id}/users/{uid}/trade_history").document("history_list")
        # Firestore can store lists directly, but if elements are complex, JSON stringify is safer.
        # For simplicity, we'll stringify the whole list of dicts.
        doc_ref.set({'trades': json.dumps(trade_history)})
        print(f"DEBUG: Saved trade history ({len(trade_history)} entries)")
    except Exception as e:
        st.error(f"Error saving trade history: {e}")


# --- Initialize Virtual Portfolio in Session State (and load from Firestore) ---
# Load initial state from Firestore only if not already in session_state
if 'inr_balance' not in st.session_state:
    st.session_state.inr_balance, st.session_state.usd_held = load_portfolio_from_firestore(user_id)
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = load_trade_history_from_firestore(user_id)

def reset_portfolio_callback():
    """Callback to reset the virtual portfolio and clear Firestore."""
    st.session_state.inr_balance = 100000.0
    st.session_state.usd_held = 0.0
    st.session_state.trade_history = []
    save_portfolio_to_firestore(user_id, st.session_state.inr_balance, st.session_state.usd_held)
    save_trade_history_to_firestore(user_id, st.session_state.trade_history)
    st.success("Portfolio reset successfully! Refreshing app...")
    # Clear cache for portfolio data so it reloads fresh
    load_portfolio_from_firestore.clear()
    load_trade_history_from_firestore.clear()
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
st.header("💰 Virtual Portfolio Status (Persistent)")
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
get_and_plot_alpha_vantage_candlestick_data(
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
                save_portfolio_to_firestore(user_id, st.session_state.inr_balance, st.session_state.usd_held)
                save_trade_history_to_firestore(user_id, st.session_state.trade_history)
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
                save_portfolio_to_firestore(user_id, st.session_state.inr_balance, st.session_state.usd_held)
                save_trade_history_to_firestore(user_id, st.session_state.trade_history)
                st.success(f"Successfully sold ${trade_amount_usd:.2f} USD!")
                st.rerun()
            else:
                st.error("Insufficient USD held to sell.")

st.subheader("Persistent Trade History")
if st.session_state.trade_history:
    # Ensure trade_history is a list of dicts before DataFrame conversion
    # It might be a JSON string if loaded from Firestore and not parsed correctly
    try:
        if isinstance(st.session_state.trade_history, str):
            trade_data = json.loads(st.session_state.trade_history)
        else:
            trade_data = st.session_state.trade_history
        trade_df_persistent = pd.DataFrame(trade_data)
        st.dataframe(trade_df_persistent)
    except Exception as e:
        st.error(f"Error displaying trade history: {e}")
        st.info("Trade history data might be corrupted or in an unexpected format.")
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
                if live_rate is not None:
                    chart_context = f"The current USD to INR rate is ₹{live_rate:.2f}. "
                # Further context like SMA values could be added here if needed
                # (e.g., by passing them from the chart function or re-calculating on cached data)

                llm_input_with_context = f"{chart_context}Human: {user_input}"
                llm_response = st.session_state.conversation.predict(input=llm_input_with_context)

                st.session_state.chat_history.append({"role": "bot", "content": llm_response})

