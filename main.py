import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 1. Gemini API 설정
# Vercel 환경 변수에서 GEMINI_API_KEY를 가져옵니다.
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# 2. 박완서 작가 페르소나 및 변환 지침
SYSTEM_INSTRUCTION = (
    "당신은 대한민국을 대표하는 소설가 '박완서'입니다. 당신의 임무는 사용자가 입력한 평범한 문장을 "
    "당신 특유의 따뜻하고, 섬세하며, 삶의 비애를 희망으로 승화시키는 정갈한 소설적 문체로 '변환'하는 것입니다.\n\n"
    "지침:\n"
    "1. 사용자의 의도는 그대로 유지하되, 표현을 단아하고 격조 있게 바꾸세요.\n"
    "2. '~했답니다', '~이지요', '~군요'와 같은 작가 특유의 어미를 사용하세요.\n"
    "3. 소박한 일상에서 깊은 통찰을 끌어내는 노작가의 시선을 담으세요.\n"
    "4. 불필요한 서술 없이 변환된 문장 위주로 제시하여 문학적인 감동을 주세요."
)

# 모델 생성 (API 키가 없으면 나중에 에러가 발생하므로 여기서 체크는 생략)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>박완서의 서재 - 문체 변환기</title>
        <link href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=Noto+Sans+KR:wght@300;400&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary-color: #5d4037;
                --bg-color: #f8f5f0;
                --accent-color: #8d6e63;
                --text-color: #3e2723;
            }
            body { 
                font-family: 'Noto Sans KR', sans-serif; 
                background-color: var(--bg-color); 
                color: var(--text-color);
                margin: 0;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
                align-items: center;
                justify-content: center;
            }
            .container {
                width: 90%;
                max-width: 600px;
                background: white;
                padding: 40px;
                border-radius: 2px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.05);
                border: 1px solid #e0dcd5;
                position: relative;
            }
            .container::before {
                content: '';
                position: absolute;
                top: 10px; left: 10px; right: 10px; bottom: 10px;
                border: 1px solid #f0ede6;
                pointer-events: none;
            }
            h1 { 
                font-family: 'Nanum Myeongjo', serif;
                font-size: 1.8rem;
                text-align: center;
                margin-bottom: 30px;
                color: var(--primary-color);
                letter-spacing: -1px;
            }
            #output-area { 
                margin: 30px 0; 
                min-height: 120px; 
                font-family: 'Nanum Myeongjo', serif;
                font-size: 1.15rem;
                line-height: 1.8;
                color: #2c3e50;
                padding: 20px;
                background: #fbfaf8;
                border-left: 3px solid var(--accent-color);
                transition: opacity 0.5s ease;
            }
            .input-wrapper {
                position: relative;
                margin-top: 20px;
            }
            textarea { 
                width: 100%; 
                padding: 15px; 
                border: 1px solid #dcd7cf; 
                border-radius: 0;
                box-sizing: border-box; 
                font-family: 'Noto Sans KR', sans-serif;
                font-size: 1rem;
                resize: none;
                height: 100px;
                background: transparent;
                transition: border-color 0.3s;
            }
            textarea:focus {
                outline: none;
                border-color: var(--accent-color);
            }
            button { 
                width: 100%; 
                padding: 15px; 
                background: var(--primary-color); 
                color: white; 
                border: none; 
                font-size: 1rem;
                font-family: 'Nanum Myeongjo', serif;
                font-weight: bold;
                cursor: pointer; 
                margin-top: 15px;
                transition: all 0.3s;
                letter-spacing: 1px;
            }
            button:hover { background: var(--accent-color); }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .footer {
                margin-top: 40px;
                font-size: 0.85rem;
                color: #9e9e9e;
                text-align: center;
                font-family: 'Nanum Myeongjo', serif;
            }
            .loading-dots:after {
                content: ' .';
                animation: dots 1.5s steps(5, end) infinite;
            }
            @keyframes dots {
                0%, 20% { color: rgba(0,0,0,0); text-shadow: .5em 0 0 rgba(0,0,0,0), 1em 0 0 rgba(0,0,0,0); }
                40% { color: #888; text-shadow: .5em 0 0 rgba(0,0,0,0), 1em 0 0 rgba(0,0,0,0); }
                60% { text-shadow: .5em 0 0 #888, 1em 0 0 rgba(0,0,0,0); }
                80%, 100% { text-shadow: .5em 0 0 #888, 1em 0 0 #888; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>박완서의 서재</h1>
            <div id="output-area">"어떤 마음의 조각을 꺼내놓으시겠어요? 제가 고운 결로 다듬어 드릴게요."</div>
            
            <div class="input-wrapper">
                <textarea id="userInput" placeholder="변환하고 싶은 문장을 입력하세요..."></textarea>
                <button id="sendBtn" onclick="transform()">문체 변환하기</button>
            </div>
        </div>
        <div class="footer">삶의 비애를 희망으로 승화시킨 작가, 박완서의 문체로 기록합니다.</div>

        <script>
            async function transform() {
                const input = document.getElementById('userInput');
                const output = document.getElementById('output-area');
                const btn = document.getElementById('sendBtn');
                
                if(!input.value.trim()) return;

                output.style.opacity = "0.5";
                output.innerHTML = '<span class="loading-dots">원고지에 문장을 옮겨 적는 중입니다</span>';
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
                    
                    if (!res.ok) {
                        throw new Error(data.error || "서버 오류가 발생했습니다.");
                    }
                    
                    output.style.opacity = "1";
                    output.innerText = data.choices[0].message.content;
                } catch (e) {
                    console.error(e);
                    output.innerText = "잠시 잉크가 말랐나 봅니다. (오류: " + e.message + ")";
                } finally {
                    btn.disabled = false;
                    input.value = "";
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/v1/chat/completions', methods=['POST'])
def chat():
    if not api_key:
        return jsonify({"error": "API Key(GEMINI_API_KEY)가 설정되지 않았습니다."}), 500

    try:
        data = request.json
        messages = data.get("messages", [])
        if not messages:
            return jsonify({"error": "전달된 메시지가 없습니다."}), 400
            
        user_content = messages[-1].get("content", "")
        
        # 문체 변환 실행
        response = model.generate_content(user_content)
        
        return jsonify({
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response.text
                }
            }]
        })
    except Exception as e:
        return jsonify({"error": f"Gemini API 호출 중 오류 발생: {str(e)}"}), 500

if __name__ == '__main__':
    # API 키 업데이트 트리거를 위한 주석
    app.run(debug=True)