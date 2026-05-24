import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(
    api_key=API_KEY
)

MODEL_NAME = "gemini-3.1-flash-lite"