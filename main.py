import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Vercel 환경 변수에 등록한 API 키를 가져옵니다.
# 주의: 배포 시 Vercel Dashboard에서 GEMINI_API_KEY를 설정해야 합니다.
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# 모델 설정 (이전의 박완서 문체 설정을 원하시면 여기에 system_instruction을 추가할 수 있습니다.)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

@app.route('/')
def home():
    return "Gemini Gateway is Running!"

@app.route('/v1/chat/completions', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get("messages", [])
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
            
        user_message = messages[-1].get("content", "")
        
        response = model.generate_content(user_message)
        
        # OpenAI API 규격과 유사하게 응답 구조화
        return jsonify({
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response.text
                },
                "finish_reason": "stop"
            }],
            "model": "gemini-2.0-flash-lite"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)