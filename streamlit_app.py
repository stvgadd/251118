import streamlit as st
from openai import OpenAI
import base64

st.set_page_config(page_title="OpenAI Chat + Image Generator", layout="centered")
st.title("🎨 OpenAI Chat + Image Generator (Streamlit)")

st.write("텍스트 응답 또는 이미지 생성을 선택할 수 있는 웹앱입니다.")

# ------------------------------------
# 사용자 API 키 입력
# ------------------------------------
# 세션 상태에 API Key를 저장하여 다른 페이지로 이동했다가 돌아와도 입력값이 유지되도록 합니다.
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# `key` 파라미터를 사용하면 Streamlit이 입력값을 `st.session_state`에 자동으로 저장합니다.
api_key = st.text_input("🔑 OpenAI API Key 입력", type="password", key="api_key")

# 탭 구성
tab1, tab2 = st.tabs(["💬 텍스트 질문하기", "🖼 이미지 생성하기"])

# =======================================================
# 1️⃣ 텍스트 질문 기능
# =======================================================
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

        client = OpenAI(api_key=api_key)

        st.info("AI가 답변을 생성 중입니다...")

        
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            max_output_tokens=300,
        )

        answer = response.output_text
        st.success("✅ 응답 완료")
        st.write(answer)



# =======================================================
# 2️⃣ 이미지 생성 기능
# =======================================================
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

        client = OpenAI(api_key=api_key)

        st.info("🎨 이미지를 생성 중입니다... 잠시만 기다리세요.")

        
            
        img = client.images.generate(
            model="gpt-image-1-mini",
            prompt=img_prompt
        )

        # base64 디코딩
        image_bytes = base64.b64decode(img.data[0].b64_json)

        st.success("✅ 이미지 생성 완료!")
        st.image(image_bytes, caption="Generated Image", use_column_width=True)

        # 다운로드 버튼 추가
        st.download_button(
            label="📥 이미지 다운로드",
            data=image_bytes,
            file_name="generated_image.png",
            mime="image/png"
        )

