# streamlit_app.py

import streamlit as st
import os # For environment variables
# Ensure data_fetcher.py is in the same directory and contains get_usd_inr_rate()
from data_fetcher import get_usd_inr_rate

# Import LangChain components for Google Gemini
# You will need to install: pip install langchain-google-genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# --- Configuration and LLM Setup ---
# Set your Google API key from environment variable for security
# It's highly recommended to set this as an environment variable (e.g., in your .bashrc, .zshrc, or system settings)
# Example of how to set it in your terminal (for current session only):
# export GOOGLE_API_KEY="YOUR_ACTUAL_GOOGLE_API_KEY_HERE"

# Attempt to retrieve the token from environment variables
google_api_key_value = os.getenv("GOOGLE_API_KEY")

# --- Debugging print statement ---
# This will print to your terminal where you run 'streamlit run'
print(f"DEBUG: GOOGLE_API_KEY value from environment: {google_api_key_value}")

if not google_api_key_value:
    st.error("Error: Google API Key (GOOGLE_API_KEY) not found. Please set it as an environment variable.")
    st.info("Example: In your terminal, run `export GOOGLE_API_KEY=\"YOUR_ACTUAL_GOOGLE_API_KEY_HERE\"`")
    st.stop() # Stop the app if key is missing

# Initialize Gemini LLM
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro", # Or "gemini-1.5-pro-latest" if you have access and prefer
        google_api_key=google_api_key_value,
        temperature=0.7,
        convert_system_message_to_human=True # Recommended for better prompt handling
    )
except Exception as e:
    st.error(f"Error initializing Google Gemini LLM: {e}")
    st.info("Please check your GOOGLE_API_KEY and ensure access to the 'gemini-pro' model.")
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

st.title("💹 USD to INR Trading Bot")
st.markdown("Ask me anything about USD to INR exchange rates or forex trends.")

# Display current USD to INR rate prominently
st.markdown("---")
try:
    live_rate = get_usd_inr_rate()
    st.metric(label="Current USD to INR Rate", value=f"₹{live_rate:.2f} INR") # Updated label
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

# --- Input Form for Chat ---
# Use a form to manage input submission and prevent cyclic reruns
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("🧠 Ask a question:", key="user_question_input")
    submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input: # Process only when button is clicked and input is not empty
        if user_input.lower() == 'exit':
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "bot", "content": "Goodbye! The bot session has ended."})
            # No explicit rerun needed, form submission triggers rerun
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
                    llm_response = st.session_state.conversation.predict(input=user_input)

                st.session_state.chat_history.append({"role": "bot", "content": llm_response})
            # No explicit rerun needed, form submission handles it by clearing input and updating session state
