import json
import urllib.request

MODEL = "qwen2.5:3b"
URL = "http://localhost:11434/api/chat"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "讀取一個文字檔的內容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "要讀取的文件路徑"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "列出一個資料夾裡的檔案",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "要查詢的資料夾路徑"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "寫入文字到一個檔案",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "要寫入的文件路徑"},
                    "content": {"type": "string", "description": "要寫入的內容"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


def chat(msg):

    body = {"model": MODEL, "messages": msg, "stream": False, "tools": TOOLS}
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        URL, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        result = json.loads(raw)

        return result["message"]


if __name__ == "__main__":
    reply = chat([{"role": "user", "content": "請列出目前資料夾有哪些檔案?"}])
    print(reply)
