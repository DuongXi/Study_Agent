import os
import requests
from PIL import Image
import json
import base64
import time
import streamlit as st
import streamlit.components.v1 as components
from streamlit_oauth import OAuth2Component

from model_config import *
from util import *
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Cố vấn học tập",
    layout="wide",
    page_icon=Image.open("/app/public/logo.png"),
)

def get_backend_url():
    if os.path.exists('/.dockerenv'):
        return "http://backend:8000"
    else:
        return "http://localhost:8000"

BACKEND_URL = os.getenv("BACKEND_URL", get_backend_url())
models = []

for provider in PROVIDERS:
    for model in LLM_MODELS[provider]:
        models.append(model)

cookie = get_cookies()
email = cookie.get("user_email")
token = cookie.get("access_token")

st.title("Cố vấn học tập")
st.info(
    "Cố vấn học tập hỗ trợ cho sinh viên thông tin của Đại học Bách khoa Hà Nội, thông tin sinh viên và thời khoá biểu."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:    
    selected = st.selectbox(
        "Lựa chọn mô hình",
        models,
        index=0,
        placeholder="Tìm một mô hình",
        key="model_select",
    )
   
    st.markdown("---")
    st.write("Góp ý cho hệ thống")

    with st.form("feedback_form"):
        feedback_text = st.text_area("Nhập góp ý của bạn tại đây...", height=70)
        submitted = st.form_submit_button("Gửi góp ý")
        
        if submitted:
            user_email = st.session_state.get("auth", "anonymous")
            if len(feedback_text.strip()) > 1:
                try:
                    requests.post(
                        f"{BACKEND_URL}/api/feedback",
                        json={"email": user_email, "message": feedback_text}
                    )
                    st.success("Cảm ơn bạn đã góp ý!", icon="👍")
                except:
                    st.warning("Có lỗi khi gửi góp ý!")
            else:
                st.warning("Vui lòng nhập nội dung góp ý phù hợp!", icon="🚨")
    st.write("---")
    
    # Xác thực
    if not email or not token:
        oauth2 = OAuth2Component(
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
            token_endpoint="https://oauth2.googleapis.com/token",
        )
        result = oauth2.authorize_button(name="",
            icon="https://www.google.com.tw/favicon.ico",
            key="google_login",
            redirect_uri="http://localhost:8501",
            scope="openid email profile https://www.googleapis.com/auth/calendar",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
            pkce='S256',
        )
        if result:
            id_token = result["token"]["id_token"]
            payload = id_token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            payload = json.loads(base64.b64decode(payload))
            email = payload["email"]
            st.session_state["auth"] = email
            st.session_state["token"] = result["token"]
            store_login_session(email, result["token"]["access_token"])
            store_token(email, result["token"]["access_token"], result["token"]["refresh_token"], result["token"]["expires_in"])
            st.rerun()
    else:
        st.session_state["auth"] = email
        st.session_state["token"] = token
        if st.button("Logout"):
            del st.session_state["auth"]
            del st.session_state["token"]
            requests.delete(f"{BACKEND_URL}/api/logout")
            components.html(f"<script>document.cookie = 'user_email=; path=/; max-age=0'; document.cookie = 'access_token=; path=/; max-age=0';</script>", height=0)
            st.rerun()
        elif not st.session_state.messages:
            send_token(st.session_state["auth"], st.session_state["token"])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message:
            if isinstance(message["output"], str):
                st.markdown(message["output"])
            elif isinstance(message["output"], list):
                for item in message["output"]:
                    if isinstance(item, dict):
                        if "text" in item:
                            st.markdown(item["text"])
                        if "tool" in item:
                            with st.expander(f"Tool: {item['tool_name']}", expanded=False):
                                st.markdown(f"""
                                    <div style='max-height: 150px; overflow-y: auto;'>
                                        <p>{item["tool"]}</p>
                                    </div>
                                    """, unsafe_allow_html=True)

def render_message(message):
    global output
    if message["role"] == "ai":
        def gen():
            yield "AI message: " + message["text"]
            time.sleep(0.5)
        output.append({'text':st.write_stream(gen)})
    elif message["role"] == "tool":
        with st.expander(f"Tool: {message['tool_name']}", expanded=False):
            st.markdown(f"""
                <div style='max-height: 150px; overflow-y: auto;'>
                    <p>{message["text"]}</p>
                </div>
                """, unsafe_allow_html=True)
        output.append({'tool':message["text"],'tool_name':message['tool_name']})

if message := st.chat_input("Hãy cho tôi câu hỏi?"):
    # Kiểm tra xem có model được chọn không
    if not selected:
        st.error("Vui lòng chọn một mô hình trước khi gửi tin nhắn!")
    else:
        if not st.session_state.messages or (st.session_state.messages and st.session_state.messages[-1].get("model") != selected):
            try:
                model_response = requests.post(f"{BACKEND_URL}/api/model", json={"model": selected})
                if model_response.status_code != 200:
                    st.error(f"Lỗi khi cập nhật model: {model_response.status_code}")
            except Exception as e:
                st.error(f"Không thể kết nối đến backend: {str(e)}")

    st.chat_message("user").markdown(message)

    st.session_state.messages.append({"role": "user", "output": message})

    data = {"message": message}
    metadata = []
    
    try:
        output = []
        with requests.post(f"{BACKEND_URL}/api/chat", json=data, stream=True) as response:
            if response.status_code == 200:
                for chunk in response.iter_lines():
                    render_message(json.loads(chunk))
            else:
                output.append({'text':"""Đã có lỗi xảy ra trong quá trình xử lý yêu cầu của bạn.
                Hãy thử lại một lần nữa và chỉnh sửa yêu cầu của bạn."""
                })
    except:
        warning = "Đã có lỗi xảy ra trong quá trình xử lý yêu cầu của bạn. Vui lòng thử lại sau."
        st.write(warning)
        output.append({'text':warning})
    output.append("")
    st.session_state.messages.append(
        {
            "role": "assistant",
            "model": selected,
            "output": output,
        }
    )
