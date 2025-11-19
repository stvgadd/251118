import streamlit as st
from openai import OpenAI
import base64
import time
from contextlib import contextmanager
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="OpenAI Chat + Image Generator", layout="centered")
st.title("🎨 OpenAI Chat + Image Generator (Streamlit)")

st.write("텍스트 응답 또는 이미지 생성을 선택할 수 있는 웹앱입니다.")


# 폴백: Streamlit에 `status` 또는 `write_stream`가 없는 환경일 수 있으므로 간단한 구현을 추가합니다.
if not hasattr(st, "status"):
    @contextmanager
    def _status(msg: str):
        with st.spinner(msg):
            yield

    st.status = _status

if not hasattr(st, "write_stream"):
    def _write_stream(container, text: str, chunk_size: int = 64, delay: float = 0.01):
        # container: a DeltaGenerator (e.g., st.empty() or inside st.chat_message())
        for i in range(0, len(text), chunk_size):
            part = text[: i + chunk_size]
            try:
                container.write(part)
            except Exception:
                container.text(part)
            time.sleep(delay)

    st.write_stream = _write_stream



@st.cache_data
def get_text_answer(api_key: str, prompt: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        max_output_tokens=300,
    )
    return response.output_text


@st.cache_data
def generate_image_bytes(api_key: str, img_prompt: str) -> bytes:
    client = OpenAI(api_key=api_key)
    img = client.images.generate(
        model="gpt-image-1-mini",
        prompt=img_prompt
    )
    return base64.b64decode(img.data[0].b64_json)


if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""


api_key = st.text_input("🔑 OpenAI API Key 입력", type="password", key="api_key")


tab1, tab2, tab3 = st.tabs(["💬 텍스트 질문하기", "🖼 이미지 생성하기", "🤖 챗봇"])

# 1️⃣ 텍스트 질문 기능
with tab1:
    st.subheader("💬 텍스트 질문하기")

    prompt = st.text_area("✏️ 질문 입력", height=150, placeholder="예: 양자역학을 쉽게 설명해줘")

    if st.button("질문 실행"):
        if not api_key:
            st.error("❌ API Key를 입력하세요.")
            st.stop()
        if not prompt.strip():
            st.error("❌ 질문을 입력하세요.")
            st.stop()

        st.info("AI가 답변을 생성 중입니다...")

        # 캐시된 함수 호출: 동일한 api_key+prompt이면 캐시된 결과 반환
        answer = get_text_answer(api_key, prompt)
        st.success("✅ 응답 완료")
        st.write(answer)



# 2️⃣ 이미지 생성 기능
with tab2:
    st.subheader("🖼 이미지 생성하기")

    img_prompt = st.text_area(
        "🎨 이미지 프롬프트 입력",
        height=150,
        placeholder="예: 바닷가에서 춤추는 고양이 일러스트"
    )

    if st.button("이미지 생성"):
        if not api_key:
            st.error("❌ API Key를 입력하세요.")
            st.stop()
        if not img_prompt.strip():
            st.error("❌ 이미지 프롬프트를 입력하세요.")
            st.stop()

        st.info("🎨 이미지를 생성 중입니다... 잠시만 기다리세요.")

        # 캐시된 함수 호출: 동일한 api_key+img_prompt이면 캐시된 이미지 바이트 반환
        image_bytes = generate_image_bytes(api_key, img_prompt)

        st.success("✅ 이미지 생성 완료!")
        st.image(image_bytes, caption="Generated Image", use_column_width=True)

        st.download_button(
            label="📥 이미지 다운로드",
            data=image_bytes,
            file_name="generated_image.png",
            mime="image/png"
        )


# 3️⃣ 챗봇 (Responses API 사용자 인터페이스)
with tab3:
    st.subheader("🤖 챗봇 (OpenAI Responses API)")

    # 대화 기록 초기화
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    # 기존 대화 표시 (st.chat_message 사용)
    for msg in st.session_state["chat_messages"]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)

    # 메시지 렌더링 후 자동으로 아래로 스크롤해서 입력창이 항상 보이도록 함
    try:
        st_html("<script>window.scrollTo(0, document.body.scrollHeight);</script>", height=100)
    except Exception:
        pass

    # 입력: st.chat_input 사용, 우측에 Clear 버튼 배치
    col_input, col_clear = st.columns([8, 1])
    with col_input:
        user_input = st.chat_input("메시지를 입력하고 Enter를 누르세요...")
    with col_clear:
        if st.button("Clear", key="chat_clear_tab3"):
            st.session_state["chat_messages"] = []
            st.experimental_rerun()

    # 사용자가 메시지를 입력하면 처리
    if user_input:
        if not api_key:
            st.error("❌ API Key를 입력하세요.")
        else:
            # 사용자 메시지 저장 및 즉시 표시
            st.session_state["chat_messages"].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            # 전체 대화 합치기(왼쪽: User / Assistant 태그 포함)
            convo = []
            for m in st.session_state["chat_messages"]:
                if m["role"] == "user":
                    convo.append("User: " + m["content"])
                else:
                    convo.append("Assistant: " + m["content"])
            convo_text = "\n".join(convo)

            # 상태 표시(폴백으로 spinner 사용) 및 스트리밍 출력
            with st.status("AI가 응답을 생성 중입니다..."):
                assistant_text = get_text_answer(api_key, convo_text)

            # 어시스턴트 메시지용 채팅 블록을 만들고 스트리밍으로 출력
            with st.chat_message("assistant") as chat_blk:
                placeholder = st.empty()
                # st.write_stream이 있으면 이를 사용하여 점진적으로 출력
                try:
                    st.write_stream(placeholder, assistant_text, chunk_size=64, delay=0.01)
                except Exception:
                    # 폴백: 점진적으로 업데이트
                    for i in range(0, len(assistant_text), 64):
                        placeholder.write(assistant_text[: i + 64])
                        time.sleep(0.01)

            # 세션에 어시스턴트 응답 저장
            st.session_state["chat_messages"].append({"role": "assistant", "content": assistant_text})

