import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from dotenv import load_dotenv
from openai import OpenAI

# Read .env first; real environment variables keep precedence because
# load_dotenv() does not overwrite variables that are already set.
load_dotenv()

BASE_URL = os.environ["OPENAI_BASE_URL"]
MODEL = os.environ["MODEL"]
API_KEY = os.environ["OPENAI_API_KEY"]
DATA_BASE_URL = os.environ["DATA_BASE_URL"]


def get_calendar(date: str) -> str:
    """Fetch {DATA_BASE_URL}/calendar/{date}.json. 404 means: no data."""
    url = f"{DATA_BASE_URL}/calendar/{date}.json"
    try:
        with urlopen(url, timeout=10) as response:
            return response.read().decode("utf-8") # bytes to str
    except HTTPError as error:
        if error.code == 404:
            return json.dumps({"error": f"no calendar data for {date}"})
        raise # re-raise other HTTP errors
    except URLError as error:
        return json.dumps({"error": f"calendar request failed: {error.reason}"})


# The tool description the model sees: name, purpose, parameters.
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_calendar",
        "description": (
            "Reads the appointments of one day from the mock calendar. "
            "Use it for every question about what is scheduled on a date."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The day to look up, formatted as YYYY-MM-DD.",
                }
            },
            "required": ["date"],
        },
    },
}

LOG_DIR = Path("logs")


class RunLog:
    """Writes one JSONL file per run: one JSON object per line."""

    def __init__(self) -> None:
        LOG_DIR.mkdir(exist_ok=True) # create logs/ if its missing
        self.run_id = uuid.uuid4().hex 
        self.path = LOG_DIR / f"{self.run_id}.jsonl"

    # example: add("tool_call", ok=True, tool="get_calendar", date="2023-01-01")
    def add(self, event: str, ok: bool, **fields) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "event": event,
            "ok": ok,
            "model": MODEL,
            **fields,
        }
        # creates/appends to the log file
        # json.dumps() dir as json string
        # ensure_ascii=False for umlauts
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    # The question comes from the command line: python -m agent "..."
    user_task = " ".join(sys.argv[1:]).strip()
    if not user_task:
        print('Usage: python -m agent "your question"', file=sys.stderr)
        return 1

    log = RunLog()
    log.add("user_task", True, task=user_task)

    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    messages = [
        {
            "role": "system",
            "content": (
                "You answer questions about a mock calendar. "
                "Always use the get_calendar tool to look up a day before "
                "answering. Dates are in 2026. Answer in the language of "
                "the question."
            ),
        },
        {"role": "user", "content": user_task},
    ]

    # --- First model call: the model decides to call the tool. ---
    started = time.monotonic()
    try:
        # model call returns a response object with a list of choices, each containing a message (default is one choice)
        first = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[TOOL_SCHEMA],
        )
    except Exception as error:
        log.add("error", False, message=str(error),
                duration_ms=int((time.monotonic() - started) * 1000))
        print(f"Model request failed: {error}", file=sys.stderr)
        return 1

    message = first.choices[0].message
    if not message.tool_calls:
        # Model answered directly without the tool.
        log.add("final", True, duration_ms=int((time.monotonic() - started) * 1000))
        print(message.content)
        return 0

    # --- Run the tool(s) the model asked for. ---
    messages.append(message)
    for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments or "{}")
        result = get_calendar(args.get("date", ""))
        log.add("tool_result", True, tool=tool_call.function.name, args=args)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

    # --- Second model call: answer with the tool result. ---
    started = time.monotonic()
    try:
        second = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[TOOL_SCHEMA],
        )
    except Exception as error:
        log.add("error", False, message=str(error),
                duration_ms=int((time.monotonic() - started) * 1000))
        print(f"Model request failed: {error}", file=sys.stderr)
        return 1

    answer = second.choices[0].message.content or ""
    log.add("final", True, duration_ms=int((time.monotonic() - started) * 1000))
    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main()) 

