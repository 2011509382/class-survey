import streamlit as st
import requests
import os

st.set_page_config(page_title="课后调查问卷 (对话版)", layout="wide")
st.title("🧠 课后互动问卷助手")

# 获取 API 密钥
API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-247a7a2a2e6b404883e104a8edaf658c")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
API_URL = "https://api.deepseek.com/chat/completions"

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一个温和而善于启发学生的老师，想调研上课课后问题和答疑。每次只问一个问题，根据学生回答逐步深入。"}
    ]

# 显示历史消息
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入
user_input = st.chat_input("今天这节课，你印象最深的情节是什么")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):

        st.markdown(user_input)

    # 请求 DeepSeek API
    payload = {
        "model": "deepseek-chat",
        "messages": st.session_state.messages,
        "temperature": 0.7
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    assistant_reply = response.json()["choices"][0]["message"]["content"]

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)
