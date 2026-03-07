import json
import os
from pathlib import Path
from typing import Any
import sys

from dotenv import load_dotenv

SRC_PATH = Path(__file__).resolve().parents[1]
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from app.services import PollenRunner

APP_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = APP_ROOT / ".env"
INPUT_JSON_PATH = Path(__file__).resolve().parent / "data" / "dummy_prompt_request.json"


def load_api_key() -> str:
    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("POLLEN_API_KEY")
    if not api_key:
        raise RuntimeError("POLLEN_API_KEY is not set. Please add it to .env.")
    return api_key


def load_payload(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    api_key = load_api_key()
    payload = load_payload(INPUT_JSON_PATH)
    runner = PollenRunner(api_key=api_key)
    result = runner.run(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
