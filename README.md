# GPT-5-mini 질의 응답 웹앱

이 예제는 사용자의 질문을 받아 `gpt-5-mini` 모델의 응답을 출력하는 간단한 Streamlit 웹앱입니다.

설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

환경 변수 설정

```bash
export OPENAI_API_KEY="sk-..."
```

앱 실행

```bash
streamlit run streamlit_app.py
```

주의
- 이 앱은 실제 OpenAI API 키가 필요합니다.
- 모델 이름은 `gpt-5-mini`로 설정되어 있습니다.

문의
- 추가 기능(대화 상태 유지, 요청 파라미터 노출 등)을 원하시면 알려주세요.
# 251118