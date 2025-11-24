import streamlit as st

client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("API Key를 입력하세요."):
        st.switch_page("streamlit_app.py")
    st.stop()

def get_response(prompt):
    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )
    return response.output_text

if st.button("Clear"):
    del st.session_state["messages"]

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role":"user","content":prompt})

    response = get_response(st.session_state.messages)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role":"assistant", "content":response})