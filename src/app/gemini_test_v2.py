import json
import sys
from pathlib import Path

from dotenv import load_dotenv

SRC_PATH = Path(__file__).resolve().parents[1]
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from app.schemas.v2.api import APIGenerateRequest, APIRetryRequest, APIResult
from app.services.v2.prompt_runner import Runner


INPUT_JSON_PATH = Path(__file__).resolve().parent / "data" / "dummy_prompt_request.json"


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def print_section(title: str, payload: dict) -> None:
    print(f"\n===== {title} =====")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def print_result(title: str, result: APIResult) -> None:
    print_section(title, result.model_dump())


def main() -> None:
    load_dotenv()

    payload = load_payload(INPUT_JSON_PATH)
    print_section("INPUT JSON", payload)

    generate_request = APIGenerateRequest.model_validate(payload)

    runner = Runner()
    result = runner.generate(generate_request)
    print_result("GENERATE RESULT", result)

    while True:
        try:
            retry_instruction = input(
                "\nRetry instruction を入力してください（空Enterで終了）: "
            ).strip()
        except EOFError:
            break

        if not retry_instruction:
            break

        retry_request = APIRetryRequest(
            previous_context=result.used_inputs,
            previous_excuse=result.excuse,
            retry_instruction=retry_instruction,
        )
        result = runner.retry(retry_request)
        print_result("RETRY RESULT", result)


if __name__ == "__main__":
    main()
