import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# -----------------------------
# Python path 修正
# -----------------------------

SRC_PATH = Path(__file__).resolve().parents[1]

if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from app.services.v1 import build_prompt


MODEL_NAME = "gemini-3-flash-preview"
INPUT_JSON_PATH = Path(__file__).resolve().parent / "data" / "dummy_prompt_request.json"


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:

    # -----------------------------
    # APIキー読み込み
    # -----------------------------

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Please add it to .env.")

    # -----------------------------
    # JSON読み込み
    # -----------------------------

    payload = load_payload(INPUT_JSON_PATH)

    print("===== INPUT JSON =====")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    # -----------------------------
    # Prompt Builder
    # -----------------------------

    prompt = build_prompt(payload)
    print(prompt)
    

    # -----------------------------
    # Gemini
    # -----------------------------
    
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    text = response.text

    print("\n===== RAW GEMINI OUTPUT =====")
    print(text)

    # -----------------------------
    # JSON parse
    # -----------------------------

    try:

        data = json.loads(text)

        result = {
            "excuse": data["excuse"],
            "score": data["score"]
        }

        print("\n===== PARSED RESULT =====")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:

        print("\n❌ JSON PARSE ERROR")
        print(e)


if __name__ == "__main__":
    main()