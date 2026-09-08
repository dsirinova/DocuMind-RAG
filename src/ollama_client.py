import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct")

def chat(messages: list[dict[str, str]]) -> str:
    payload = json.dumps(
        {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1},
        }
    ).encode("utf-8")
    request = Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})

    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))["message"]["content"].strip()
    except URLError as error:
        raise RuntimeError("Ollama serveri əlçatan deyil. `ollama serve` işlədiyinə baxın.") from error
