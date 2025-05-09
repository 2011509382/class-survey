import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

# 设置页面
st.set_page_config(page_title="课后问卷", layout="centered")
st.title("📋 交互式课后问卷")

# 获取 API 密钥
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

# 问卷对话模板
system_prompt = """
你是一位友善且富有洞察力的问卷调查助手，任务是通过对话挖掘学生对课程内容的理解与反馈。
你应该循序渐进地提问，引导学生表达他们的真实想法，包含但不限于以下方面：
1. 课程内容是否清晰，哪些地方没听懂？
2. 是否对某些知识点感兴趣？
3. 有没有建议课程改进的地方？
请用简洁自然的方式提问，不要一次性提太多问题。
"""

# 会话初始化
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# 输入姓名/学号
name = st.text_input("请输入你的姓名或学号：", max_chars=50)

# 显示历史消息
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 提交内容后调用 DeepSeek API
def call_deepseek_api(messages, api_key):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7
    }
    res = requests.post(url, headers=headers, json=payload)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

# 聊天输入框
if prompt := st.chat_input("输入你的想法或问题..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("DeepSeek 正在思考..."):
            reply = call_deepseek_api(st.session_state.messages, DEEPSEEK_API_KEY)
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

    # 保存问卷数据
    def extract_user_answers(messages):
        return "\n".join([m["content"] for m in messages if m["role"] == "user"])

    user_answers = extract_user_answers(st.session_state.messages)
    if name:
        df = pd.DataFrame([{
            "姓名或学号": name,
            "问卷回答": user_answers,
            "提交时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        if os.path.exists("responses.csv"):
            df.to_csv("responses.csv", mode="a", header=False, index=False)
        else:
            df.to_csv("responses.csv", index=False)
