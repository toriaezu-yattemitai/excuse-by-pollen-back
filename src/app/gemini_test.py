import os
import json
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

# プロンプト
prompt = """
次の条件で言い訳を作ってください。

・花粉症がしんどい時の面白く、大げさな言い訳
・説得力スコア(0〜100)

JSONのみ出力してください。
説明文は禁止です。

{
  "excuse": "...",
  "score": number
}
"""

# AIに質問
response = model.generate_content(prompt)

# Geminiの出力（文字列）
text = response.text

# JSONに変換
data = json.loads(text)

# 最終結果
result = {
    "excuse": data["excuse"],
    "score": data["score"]
}

print(result)