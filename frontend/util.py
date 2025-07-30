import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
from datetime import datetime, timedelta, timezone
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def store_token(user_email, access_token, refresh_token=None, expires_in=None):
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
    res = requests.post(f"{BACKEND_URL}/api/token", json={
        "user_email": user_email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at
    })
    return res.ok

def store_login_session(email, access_token):
    st.session_state["user_email"] = email
    st.session_state["access_token"] = access_token

    js = f"""
    document.cookie = "user_email={email}; path=/; max-age=3600";
    document.cookie = "access_token={access_token}; path=/; max-age=3600";
    """
    components.html(f"<script>{js}</script>", height=0)

def send_token(user_email, access_token):
    res = requests.get(f"{BACKEND_URL}/api/token/{user_email}", json={
        "user_email": user_email,
        "access_token": access_token
    })
    return res.ok

def get_cookies():
    cookie_str = streamlit_js_eval(js_expressions="document.cookie", key="get_cookie")
    if cookie_str:
        cookie_info = cookie_str.split(";")[1:3]
        cookie_json = {i.split("=")[0].strip(" "):i.split("=")[1] for i in cookie_info}
    else:
        cookie_json = {}
    return cookie_json