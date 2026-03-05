import json
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from google import genai

SRC_PATH = Path(__file__).resolve().parents[1]
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from back.src.app.services.v1 import build_prompt


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

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    result = {
        "input_json_path": str(INPUT_JSON_PATH),
        "prompt": prompt,
        "excuse": response.text,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
