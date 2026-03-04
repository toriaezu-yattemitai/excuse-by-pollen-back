import os
from dotenv import load_dotenv
import google.generativeai as genai

# .env 読み込み
load_dotenv()

# APIキー取得
api_key = os.getenv("GEMINI_API_KEY")

print("API KEY:", api_key[:5], "...")  # 確認用

# Gemini設定
genai.configure(api_key=api_key)

# モデル生成
model = genai.GenerativeModel("gemini-3-flash-preview")

# AIに質問
response = model.generate_content(
    "花粉症がしんどい時の面白い言い訳を1つ作ってください"
)

result = {
    "excuse": response.text,
    "score": 85
}

print(result)