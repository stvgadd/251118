import streamlit as st
from openai import OpenAI

@st.cache_data
def get_response(prompt):
    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )
    return response.output_text


st.title("OpenAI GPT model")

api_key= st.text_input("OpenAI API Key", type="password")
if api_key:
    st.session_state["OPENAI_API_KEY"] = api_key
    client = OpenAI(api_key=api_key)
    st.session_state["openai_client"] = client
else:
    st.markdown("API KEY를 입력하세요.")
    #st.stop()

prompt = st.text_area("User prompt")

if st.button("Ask!", disabled=(len(prompt)==0)):
    st.write(get_response(prompt))