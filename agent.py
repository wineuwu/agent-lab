import json
import urllib.request

MODEL = "qwen2.5:3b"
URL = "http://localhost:11434/api/chat"


def chat(msg):

    body = {"model": MODEL, "messages": msg, "stream": False}
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        URL, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        result = json.loads(raw)

        return result["message"]


if __name__ == "__main__":
    reply = chat([{"role": "user", "content": "你好，請用一句話自我介紹"}])
    print(reply)
