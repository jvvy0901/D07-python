import os
from pathlib import Path

import requests
import streamlit as st

API = {
    "chat": "https://api.openai.com/v1/chat/completions",  # 🔌 OpenAI 챗봇 (ChatGPT)
}
KEY_NAME = "OPENAI_API_KEY"
MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = "너는 친절한 한국어 챗봇이야. 짧고 알기 쉽게 답해 줘."
ERRORS = {
    401: "OpenAI 키가 틀렸어요. .env를 확인해 주세요",
    429: "요청이 너무 많거나 사용 한도를 넘었어요. 잠시 후 다시 해 주세요",
    500: "OpenAI 서버에 문제가 있어요. 잠시 후 다시 해 주세요",
    503: "OpenAI 서버가 바빠요. 잠시 후 다시 해 주세요",
}


def load_env():
    """같은 폴더의 .env 를 읽어 환경변수로 등록 (KEY=값 형식)."""
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip())


def ask(messages, api_key):
    """(답변, 오류메시지) 를 돌려준다. 키·주소는 화면에 내보내지 않는다."""
    headers = {"Authorization": f"Bearer {api_key}"}  # 🔌 키는 헤더로만 보냄
    body = {"model": MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages}
    try:
        res = requests.post(API["chat"], headers=headers, json=body, timeout=60)  # 🔌 API 호출
    except requests.RequestException:
        return None, "OpenAI 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요"

    if res.status_code != 200:
        return None, ERRORS.get(res.status_code, f"답변을 가져오지 못했어요 (오류 코드 {res.status_code})")

    try:
        return res.json()["choices"][0]["message"]["content"], None  # choices[0].message.content = 답변
    except (ValueError, KeyError, IndexError):
        return None, "답변 형식이 이상해요. 다시 시도해 주세요"


def main():
    st.set_page_config(page_title="챗봇", page_icon="💬")
    st.title("💬 챗봇")

    load_env()
    api_key = os.getenv(KEY_NAME)
    if not api_key:
        st.error(f".env에 {KEY_NAME}가 없어요. .env.example을 보고 채워 주세요")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.sidebar.button("🗑️ 대화 지우기"):
        st.session_state.messages = []
    st.sidebar.caption(f"모델: {MODEL}")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("메시지를 입력하세요")
    if not prompt:
        return

    with st.chat_message("user"):
        st.markdown(prompt)
    history = st.session_state.messages + [{"role": "user", "content": prompt}]

    with st.chat_message("assistant"):
        with st.spinner("생각하는 중..."):
            answer, error = ask(history, api_key)
        if error:
            st.error(error)
            return  # 실패한 질문은 기록에 넣지 않아 다시 보낼 수 있다
        st.markdown(answer)

    st.session_state.messages = history + [{"role": "assistant", "content": answer}]


if __name__ == "__main__":
    main()
