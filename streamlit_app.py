# streamlit_app.py

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go # For candlestick chart
from binance.client import Client # For kline interval constants

# Ensure data_fetcher.py is in the same directory and contains get_usd_inr_rate()
from data_fetcher import get_usd_inr_rate, get_candlestick_data

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


# --- Streamlit App Interface ---
st.set_page_config(
    page_title="USD/INR Trading Bot 💹",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("💹 USDT to INR Trading Bot (Proxy for USD)")
st.markdown("Ask me anything about USDT to INR exchange rates or crypto/forex trends.")

# Display current USDT to INR rate prominently
st.markdown("---")
try:
    live_rate = get_usd_inr_rate()
    st.metric(label="Current USDT to INR Rate", value=f"₹{live_rate:.2f} INR")
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


# --- Live Candlestick Chart Section ---
st.header("📊 Live USDT/INR Candlestick Chart")

# Selectbox for interval
interval_options = {
    "1 Minute": Client.KLINE_INTERVAL_1MINUTE,
    "5 Minutes": Client.KLINE_INTERVAL_5MINUTE,
    "15 Minutes": Client.KLINE_INTERVAL_15MINUTE,
    "30 Minutes": Client.KLINE_INTERVAL_30MINUTE,
    "1 Hour": Client.KLINE_INTERVAL_1HOUR,
    "4 Hours": Client.KLINE_INTERVAL_4HOUR,
    "1 Day": Client.KLINE_INTERVAL_1DAY
}
selected_interval_label = st.selectbox(
    "Select Candlestick Interval:",
    list(interval_options.keys()),
    index=0 # Default to 1 Minute
)
selected_interval = interval_options[selected_interval_label]

# Cache the data for 1 minute to avoid hitting API too frequently
@st.cache_data(ttl=60) # Cache for 60 seconds
def get_and_plot_candlesticks(symbol, interval, limit):
    """Fetches candlestick data and creates a Plotly chart."""
    try:
        candlestick_df = get_candlestick_data(symbol=symbol, interval=interval, limit=limit)

        if not candlestick_df.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=candlestick_df.index,
                open=candlestick_df['open'],
                high=candlestick_df['high'],
                low=candlestick_df['low'],
                close=candlestick_df['close']
            )])

            fig.update_layout(
                title=f'{symbol} Candlestick Chart ({selected_interval_label})',
                xaxis_title='Time',
                yaxis_title='Price (INR)',
                xaxis_rangeslider_visible=False # Hide the range slider for cleaner look
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No candlestick data available to display for the selected interval.")
    except Exception as e:
        st.error(f"Error displaying candlestick chart: {e}")

# Call the function to display the chart
get_and_plot_candlesticks("USDTINR", selected_interval, 100) # Fetch last 100 candles

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
                # Note: The bot will still refer to USD/INR, but the chart is USDT/INR
                if "usd" in user_input.lower() and "inr" in user_input.lower() and ("price" in user_input.lower() or "rate" in user_input.lower()):
                    try:
                        rate = get_usd_inr_rate()
                        llm_response = f"The current USDT to INR exchange rate (proxy for USD) is ₹{rate:.2f}."
                    except Exception:
                        llm_response = "I couldn't fetch the live rate at the moment, but I can still discuss forex trends."
                else:
                    # Use the conversational chain for other questions
                    llm_response = st.session_state.conversation.predict(input=user_input)

                st.session_state.chat_history.append({"role": "bot", "content": llm_response})

