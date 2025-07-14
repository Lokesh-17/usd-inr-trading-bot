# streamlit_app.py

import streamlit as st
import os # For environment variables
# Ensure data_fetcher.py is in the same directory and contains get_usd_inr_rate()
from data_fetcher import get_usd_inr_rate

# Import LangChain components
# Make sure you have langchain-community installed: pip install langchain-community
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

# CORRECTED LINE: Check hf_token_value, not HF_TOKEN
if not hf_token_value:
    st.error("Error: Hugging Face API token (HF_TOKEN) not found. Please set it as an environment variable.")
    st.info("Example: In your terminal, run `export HF_TOKEN=\"hf_YOUR_ACTUAL_TOKEN_HERE\"`")
    st.stop() # Stop the app if token is missing

# Assign the retrieved value to HF_TOKEN for use in HuggingFaceHub
HF_TOKEN = hf_token_value

# Initialize HuggingFaceHub LLM
# Ensure the model name is correct and accessible via your HF_TOKEN
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
# We'll use a simple prompt for the bot's persona
template = """You are a helpful AI assistant specialized in USD to INR exchange rates and general forex trends.
If the user asks for the current USD to INR price, you should provide it.
Keep your responses concise and to the point.

Current conversation:
{history}
Human: {input}
AI:"""
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

# Initialize memory for the conversation
# Streamlit reruns the script, so we need to store memory in session_state
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

st.title("💹 USD to INR Trading Bot")
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

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**🧠 Your Question:** {message['content']}")
    else:
        st.markdown(f"**🤖 Response:** {message['content']}")

# User input for chat
user_input = st.text_input("🧠 Ask a question (or type 'exit'):", key="chat_input")

if user_input:
    # Clear the input box after submission
    # This is often done by setting a default value or using a form,
    # but for simple text_input, the app rerunning will handle it.
    
    if user_input.lower() == 'exit':
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "bot", "content": "Goodbye! The bot session has ended."})
        # No st.experimental_rerun() here
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
                    llm_response = "I couldn't fetch the live rate at the moment, but I can still discuss forex trends."
            else:
                # Use the conversational chain for other questions
                # The .predict() method will use the LLM
                llm_response = st.session_state.conversation.predict(input=user_input)

            st.session_state.chat_history.append({"role": "bot", "content": llm_response})
            # No st.experimental_rerun() here

    # To clear the input box visually after submission without rerunning the whole app
    # (This is a common pattern, but might require a form or a callback for text_input)
    # For now, relying on natural rerun behavior.
