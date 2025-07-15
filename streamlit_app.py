# streamlit_app.py

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import datetime # For timestamps
import json # For JSON serialization/deserialization
import uuid # For anonymous user ID
# Removed: import base64 # No longer needed for decoding Firebase config

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
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDFqjXST7ptIB2g\nNVZCNoaY3zylwaRCWXR878LmPLVVJJboGKDlQGevW87OZ6V4sWvBycy7kUkyzWIC\nSN9QcotNRb+6RhccsOKeHPWYTlG2BmUcglQR9/LovJcnTHdMvK6+FBxIGaDm7NBu\naNtNj+jkvYGrqeK/9G/wtvRQ+VUYFAEWh/nRvG8y5WOfjIVmMq5skLaE1NaXG2ob\n9nANwRDNZwVSBqc+fie9WsaqF7/mXG693Zadrl4+xU3D0fEY9Zsx2eX1IDerg+2j\nI+E1CWGjMQ8FrJPwEi7e01ctVJZbhadMA19zECozJnv4yTm0GemfUrgkfiMNoa7p\nyot9xiwjAgMBAAECggEAD/avUmpk+dOKVk99xWrbk59n1FKKE7UKHt2gOxxJCsoh\n3oxqph59oTXEGHsEwUrBk0zbGi+MHqxj+h+XhXWSwYKyDsxX/oBcn6diwFJcRVvz\n24m9BMHRHjG+RWARZyL6kS2qRmUSJRmYEGqrLMhEEgEqEUqZnlC9Sk6u9uvZZFBz\nhZfDNazM7WWg6KS7+IFtvELYud4wvgZFu34P1Wb765seJqy8Kaz/WnIU0rW6vipI\naWQeY9hsg1ZmUeVkqlLXiMlLmiInythREd7w0ryGJPezTr74lam8463w5v0Srcw4\n9cZ5TFifxCo3zCpUiuxqxRg/oADSztmWZ+3CMZ0jWQKBgQDw/PrOAsRffY+/JK5y\nwuy9q5FZ3kou2hbjsv55huUbkcp7epKcpDMqCdLaSuLesXfUyu4Dq17pxXD92k2x\nIf1WRR7jc3mRCApnRw2l1TIV6wHKtyeDPvXTITgicu9JMixQNnlozneCYFzSBbbl\nBS0yKhNpRabtsyiKAlmtVHdZCQKBgQDR+lte1LdVOg063WiuC+FhmgqwRGiPG+fQ\nj3Z53jHpQfIcp4jthawzJl/KJ3HRFMq+zfMTOfOKL6+xzSONeIughrMr770UsLS4\n8212BOr6nbHm0LooEBi6cJLNXuDANZlG/nqekReInM10VwplhNrqipWd8FYDLAmh\nCbWPP4yCywKBgQCcK+XBMeve0jkgrv3aY1YWiKP2cGb0u+LPhwUA7pl052Mn6EQw\n/PwnRxx82MDzfmDg5u2eNSWaK5jQ+fMVUqihisO8tO3YPjS3v0Up7eK6b4TGwTD7\nDgcy3rlJIeDON5SeGt9NO1gZhqdAd/GRs2wZsUjJFRlbu5oO7fz9pdp+OQKBgQCA\nLKf7wjNLJg2PYjoVDBF/J63gnVGKEgm2iOxUResHrQaisS3nd5J/Aqy0VNGoRF3i\njQsVMGnWb3d7PHK4V947lh3m8wfjil43C/lEcooRg5NmBwGrlO/TVwZ1sLXW/qDa\n8lpdUsofzT+pBbzF7YxIYWIlL+EBPK+ACtI2aB9YcwKBgDZSPJ11Flm0DFv/YwIo\npjE3x12/JEy9BKXlxml6OacPOc133MCA5qcwVVD3QZhwmp4jjH+uL6smy4DMVImi\n+0vlgai9FCn3a1JGlvWnL6iBpLb6Mc9/0nXEkj3vw+YOh1hda2A+fXuN1a2Cpe4N\nOypOGoBbMfzdsrnQL0HdD7vC\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@usdinrtradingbot.iam.gserviceaccount.com",
  "client_id": "113166061108323668503",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40usdinrtradingbot.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
# End of hardcoded Firebase config
