import streamlit as st
from openai import OpenAI
import base64

st.set_page_config(page_title="OpenAI Chat + Image Generator", layout="centered")
st.title("🎨 OpenAI Chat + Image Generator (Streamlit)")

st.write("텍스트 응답 또는 이미지 생성을 선택할 수 있는 웹앱입니다.")



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

    # 대화 표시
    for msg in st.session_state["chat_messages"]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Assistant:** {content}")

    # 입력창 및 Clear 버튼
    input_col, clear_col = st.columns([4, 1])
    with input_col:
        st.text_input("메시지 입력", key="chat_input_tab3")
    with clear_col:
        if st.button("Clear", key="chat_clear_tab3"):
            st.session_state["chat_messages"] = []
            st.session_state["chat_input_tab3"] = ""
            st.experimental_rerun()

    # 보내기 버튼 처리
    if st.button("보내기", key="chat_send_tab3"):
        if not api_key:
            st.error("❌ API Key를 입력하세요.")
            st.stop()
        if not st.session_state.get("chat_input_tab3", "").strip():
            st.error("❌ 메시지를 입력하세요.")
            st.stop()

        user_text = st.session_state.get("chat_input_tab3", "").strip()
        st.session_state["chat_messages"].append({"role": "user", "content": user_text})

        # 대화 전체를 하나의 프롬프트로 결합
        convo = []
        for m in st.session_state["chat_messages"]:
            if m["role"] == "user":
                convo.append("User: " + m["content"])
            else:
                convo.append("Assistant: " + m["content"])
        convo_text = "\n".join(convo)

        st.info("AI가 응답을 생성 중입니다...")
        assistant_text = get_text_answer(api_key, convo_text)

        st.session_state["chat_messages"].append({"role": "assistant", "content": assistant_text})
        st.session_state["chat_input_tab3"] = ""
        st.experimental_rerun()

