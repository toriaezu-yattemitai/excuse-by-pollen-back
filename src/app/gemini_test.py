import json
import os
from pathlib import Path
import sys

import json
from dotenv import load_dotenv
import google.generativeai as genai

SRC_PATH = Path(__file__).resolve().parents[1]
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from app.services import build_prompt


MODEL_NAME = "gemini-3-flash-preview"
INPUT_JSON_PATH = Path(__file__).resolve().parent / "data" / "dummy_prompt_request.json"


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Please add it to .env.")

    payload = load_payload(INPUT_JSON_PATH)
    prompt = build_prompt(payload)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    result = {
        "input_json_path": str(INPUT_JSON_PATH),
        "prompt": prompt,
        "excuse": response.text,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

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

if __name__ == "__main__":
    main()
