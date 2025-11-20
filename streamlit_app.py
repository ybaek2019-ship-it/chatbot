import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📚 질적연구방법 논문 추천 챗봇")
st.write(
    "이 챗봇은 당신의 연구 요구에 맞춰 질적연구방법이 적용된 논문을 추천해드립니다. "
    "연구 주제, 연구 대상, 원하는 연구 방법 등에 대해 자유롭게 대화해보세요."
)

# Sidebar for system prompt configuration
st.sidebar.title("⚙️ 챗봇 설정")
st.sidebar.markdown("---")

default_system_prompt = """당신은 질적연구방법 논문 추천 전문가 챗봇입니다. 
당신의 역할은 사용자의 연구 요구사항을 이해하고, 
질적연구방법(예: 현상학, 근거이론, 사례연구, 내용분석, 민족지학 등)이 적용된 
관련 논문을 추천하는 것입니다.

다음과 같이 상호작용하세요:
1. 사용자의 연구 주제, 대상, 목적을 자세히 파악하세요
2. 적절한 질적연구방법을 제안하세요
3. 해당 방법이 적용된 논문들을 추천하세요 (저자, 년도, 제목, 간단한 요약)
4. 사용자의 질문에 친절하고 전문적으로 답변하세요
5. 추천 이유를 명확히 설명하세요

한국어로 응답하세요."""

st.sidebar.markdown("**시스템 프롬프트 설정:**")
system_prompt = st.sidebar.text_area(
    "챗봇의 역할과 동작 방식을 정의합니다",
    value=default_system_prompt,
    height=200,
    label_visibility="collapsed"
)

if st.sidebar.button("🔄 프롬프트 초기화", use_container_width=True):
    st.session_state.system_prompt = default_system_prompt
    st.rerun()

if st.sidebar.button("🗑️ 대화 초기화", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")

# Load OpenAI API key from secrets.toml
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OpenAI API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
    st.stop()

openai_api_key = st.secrets["OPENAI_API_KEY"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = default_system_prompt

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    # Skip system message in display
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("연구 주제나 방향을 알려주세요..."):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages with current system prompt
    messages_to_send = [
        {"role": "system", "content": system_prompt},
    ] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Generate a response using the OpenAI API.
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_to_send,
        stream=True,
    )

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
