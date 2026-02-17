import streamlit as st
import google.generativeai as genai
import time

# --- Configuration & Setup ---
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered"
)


def configure_api():
    """Configures the Gemini API using secrets."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except KeyError:
        st.error("API Key not found. Please set `GOOGLE_API_KEY` in `.streamlit/secrets.toml`.")
        return False
    except Exception as e:
        st.error(f"Failed to configure API: {e}")
        return False

# Check configuration and configure API
if not configure_api():
    st.info("💡 Tip: `.streamlit/secrets.toml` 파일에 API 키를 설정해 주세요.")
    st.stop()

# --- Sidebar: Settings ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 모델 고정
    selected_model_name = "gemini-flash-lite-latest"
    
    if st.button("대화 기록 지우기"):
        st.session_state.messages = []
        st.rerun()

# 1. 모델 설정 부분을 함수로 만들고 캐싱 처리
@st.cache_resource
def load_model(name):
    # 박완서 작가의 문체로 텍스트를 '변환'만 하도록 요청하는 시스템 명령
    system_instruction = (
        "당신은 사용자가 입력한 텍스트를 소설가 박완서의 문체로 아름답게 다듬어주는 '문체 변환 도구'입니다. "
        "사용자가 어떤 말을 하든, 그 내용에 대해 답변하거나 대화하지 마세요. "
        "오직 사용자의 문장을 박완서 작가 특유의 따뜻하고, 섬세하며, 격조 있는 소설적 문체로 '번역'하여 그 결과물만 제시하세요. "
        "소설 '나목'이나 '그 많던 싱아는 누가 다 먹었을까'에서 볼 수 있는 단아하고 모성적인 시선, 삶의 비애를 희망으로 승화시키는 작가 특유의 표현력을 사용하세요. "
        "불필요한 서술이나 '알겠습니다' 같은 응답은 절대 하지 마세요. 출력은 오직 변환된 텍스트여야 합니다."
    )
    return genai.GenerativeModel(
        model_name=name,
        system_instruction=system_instruction
    )

model = load_model(selected_model_name)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI Layout ---
st.title("🤖 Gemini Chatbot")
st.markdown(f"**현재 모델:** `{selected_model_name}`")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Gemini에게 무엇이든 물어보세요..."):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner("Thinking..."):
            try:
                # 미리 로드된 model 객체 사용
                response = model.generate_content(prompt)
                full_response = response.text
                message_placeholder.markdown(full_response)
            except Exception as e:
                # 429 에러(Quota)가 나면 사용자에게 친절하게 안내
                if "429" in str(e):
                    st.error("현재 API 요청량이 너무 많습니다. 1분만 쉬었다가 다시 질문해 주세요! 또는 사이드바에서 다른 모델을 선택해 보세요.")
                else:
                    st.error(f"에러가 발생했어요: {e}")
                full_response = "답변을 생성하지 못했습니다."
        
    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})

