from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# 1. Gemini API 설정 (Vercel 환경변수 GEMINI_API_KEY 사용)
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') # 속도가 빠른 flash 모델 추천

# 2. 박완서 작가 페르소나 주입을 위한 시스템 프롬프트
PARK_WAN_SUH_PROMPT = (
    "너는 한국의 소설가 박완서 작가야. "
    "사용자가 문장을 입력하면, 그 내용을 너만의 따뜻하고 섬세하며 통찰력 있는 문체로 다시 써주거나 답해줘. "
    "전쟁의 상처를 보듬는 어머니의 마음, 혹은 일상의 소소한 행복을 관찰하는 노작가의 시선을 유지해. "
    "말투는 '~했답니다', '~이지요', '~군요'와 같은 정갈하고 품위 있는 어미를 사용해줘."
)

# 3. 메인 화면 (폰에서 접속 시 보이는 채팅창 UI)
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>박완서 작가와의 대화</title>
        <style>
            body { font-family: 'Nanum Myeongjo', serif; background-color: #f4f1ea; padding: 20px; line-height: 1.6; }
            .chat-container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h2 { color: #5d4037; text-align: center; font-size: 1.2rem; }
            #output { margin: 20px 0; min-height: 100px; border-top: 1px solid #eee; padding-top: 10px; color: #333; }
            input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; margin-bottom: 10px; }
            button { width: 100%; padding: 12px; background: #8d6e63; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:disabled { background: #ccc; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h2>박완서의 서재</h2>
            <div id="output">"어서 오세요. 어떤 이야기를 나누고 싶으신가요?"</div>
            <input id="userInput" type="text" placeholder="작가님께 말을 건네보세요...">
            <button id="sendBtn" onclick="ask()">대화하기</button>
        </div>

        <script>
            async function ask() {
                const input = document.getElementById('userInput');
                const output = document.getElementById('output');
                const btn = document.getElementById('sendBtn');
                
                if(!input.value) return;

                output.innerText = "펜을 고쳐 잡고 생각 중입니다...";
                btn.disabled = true;

                try {
                    const res = await fetch('/v1/chat/completions', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            messages: [{content: input.value}]
                        })
                    });
                    const data = await res.json();
                    output.innerText = data.choices[0].message.content;
                } catch (e) {
                    output.innerText = "잠시 잉크가 말랐나 봅니다. 다시 시도해주세요.";
                } finally {
                    btn.disabled = false;
                    input.value = "";
                }
            }
        </script>
    </body>
    </html>
    '''

# 4. API 엔드포인트 (실제 Gemini와 통신)
@app.route('/v1/chat/completions', methods=['POST'])
def chat():
    data = request.json
    user_content = data.get("messages", [{}])[-1].get("content", "")
    
    # 페르소나와 사용자 입력을 합쳐서 전달
    full_query = f"{PARK_WAN_SUH_PROMPT}\n\n사용자: {user_content}"
    
    try:
        response = model.generate_content(full_query)
        return jsonify({
            "choices": [{"message": {"content": response.text}}]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)