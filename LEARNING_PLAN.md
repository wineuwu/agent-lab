# agent-lab 學習計畫：從零寫一個有 harness 的 AI agent

> 目標：親手用 Python 寫一支簡易 AI agent，並逐步加上 harness（讓模型可靠工作的那層規則與檔案），
> 對照 [Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/zh-TW/) 的講次理解每個元件為什麼存在。
> 產出同時是作品集：每一步一個 commit，README 可講故事。

## 環境與限制

| 項目 | 選擇 | 原因 |
|---|---|---|
| 語言 | Python 3.12，只用標準函式庫 | 學語言本身，不被套件遮住原理 |
| 模型 | 本機 Ollama `qwen2.5:3b` | 免費、無 API key；機器 8 GB RAM 只能跑 3B 以下 |
| 進行方式 | 我寫、Claude 當教練（一塊一塊講、我寫完它檢查） | 學得牢 |
| 學習節奏 | 每步「先跑 → 看它怎麼失敗 → 加一道 harness」 | 這正是 L01 的核心論點 |

## 路線總覽

```
Step 1 最小循環 ──► Step 2 邊界 ──► Step 3 功能清單 ──► Step 4 強制驗證 ──► Step 5 可觀測 ──► Step 6 跨 session 交接
   (裸 agent)         (L07)           (L08)              (L09/L10)          (L11)           (L05/L06/L12)
```

---

## Step 1：最小 agent 循環（L02、L13）

**要懂的概念**：agent = 一個 `while` 迴圈：把對話送給模型 → 模型說要用哪個工具 → 幫它跑 → 結果塞回對話 → 再送。對話那個 list 就是 agent 的全部記憶。

| 塊 | 做什麼 | 會學到的 Python | 狀態 |
|---|---|---|---|
| 1-1 | `chat(messages)`：用 `urllib` POST 到 Ollama，回傳 `message` | `import`、`def/return`、dict、`json`、`with`、`if __name__` | ✅ 完成（commit `b2b4783`） |
| 1-2 | 定義工具：用 JSON Schema 告訴模型有 `list_dir / read_file / write_file` 三個工具 | 巢狀 dict、list、把 `tools` 加進 request | ✅ 完成（commit `f3c5629`） |
| 1-3 | 執行工具：寫三個對應的 Python 函式，用「名稱 → 函式」字典分派 | `os`/`pathlib`、開檔讀寫、dict 當 switch、`**kwargs` 展開參數 | ✅ 完成 |
| 1-4 | 主循環：`while True` 收 `tool_calls`、執行、以 `role: tool` 回填，直到模型不再要工具 | `while`、`for`、`if/else`、`append`、`break` | ⬜ |

**驗收**：給任務「在 workspace/ 建 hello.txt，內容寫今天日期」，agent 真的建出檔案。
**預期會看到的失敗**（留下紀錄，這是 Step 2 的動機）：模型亂走目錄、寫到 workspace 外、做完不停、或說「做好了」但檔案不在。

## Step 2：劃清邊界（L07）

**要懂的概念**：agent 會「做過頭」或「做不完」，原因是沒人告訴它範圍。邊界要寫進程式，不是寫進 prompt 求它遵守。

- 做什麼：工具只准碰 `workspace/` 內的路徑（路徑跳脫就拒絕並回錯誤訊息給模型）；主循環加 `MAX_STEPS`，超過就停。
- 會學到：`pathlib.Path.resolve()`、`raise`/`try-except`、把錯誤當成工具回傳值餵回模型。
- 驗收：故意要它寫 `../secret.txt`，它被擋下且能自己改回 workspace 內。

## Step 3：功能清單（L08）

**要懂的概念**：與其在 prompt 裡描述任務，不如給一份機器可讀的 `feature_list.json`：每項功能、完成條件、狀態。agent 對著清單做、也對著清單回報。

- 做什麼：新增 `feature_list.json`；agent 啟動時讀進來、只做 `status: todo` 的項目、做完把狀態改 `done`。
- 會學到：讀寫 JSON 檔、list 篩選（list comprehension）、狀態機的最小形式。
- 驗收：清單三項功能，跑完三項都 `done` 且檔案真的存在。

## Step 4：不准提前宣告完成（L09、L10）

**要懂的概念**：模型會「說做好了」但沒做。解法：完成的判定權不給模型，給一段程式（驗證器）。

- 做什麼：每個 feature 帶一條 `check`（例如「檔案存在且含某字串」）；agent 說 done 時，程式跑 check，失敗就把失敗訊息塞回去要它繼續。
- 會學到：`subprocess`（跑外部指令）、把「驗證」和「執行」拆成兩段。
- 驗收：故意讓一個 check 很嚴，觀察 agent 被打回、修正、再過。

## Step 5：可觀測（L11）

**要懂的概念**：agent 出問題時，你需要事後回放它每一步在想什麼、呼叫了什麼。log 是 harness 的一部分，不是事後補。

- 做什麼：每一輪把 `messages` 增量和工具呼叫寫進 `logs/run-<時間>.jsonl`；寫一支 `replay.py` 把 log 印成可讀時間線。
- 會學到：`logging` 或手寫 JSONL、`datetime`、命令列參數 `sys.argv`。
- 驗收：從 log 能指出「第幾步開始走歪」。

## Step 6：跨 session 交接與初始化（L05、L06、L12）

**要懂的概念**：長任務會跨多次啟動。每次啟動先初始化（環境檢查、讀進度），每次結束前留乾淨交接（進度檔）。

- 做什麼：`init()` 檢查 Ollama 服務與模型是否存在、讀 `progress.md`；結束時寫回「做到哪、下一步、未解問題」。
- 會學到：`urllib` 錯誤處理、檔案追加寫入、程式的啟動/收尾生命週期。
- 驗收：中途 Ctrl+C 殺掉，重開能接著做、不重做已完成項目。

---

## 收尾（作品集）

- `README.md`：一段話說這是什麼、一張路線圖、每個 Step 對應的 commit 與「加了這道 harness 前 vs 後」的實際差異截圖或 log 片段。
- 可選延伸：換成 Anthropic API（只改 `chat()`）、加第四個工具 `run_shell`（配合 Step 2 的邊界）。

## 目前進度

- 2026-08-26：環境就緒（Ollama + qwen2.5:3b），Step 1-1 完成。
- 2026-09-02：1-2 完成（模型會回 tool_calls）；1-3 完成（三個工具函式 + TOOL_FUNCTIONS 分派，手動測通過）。中途踩坑：回傳 generator 而非字串、頂層程式先於定義執行（NameError，見 WIP commit）。下一步：1-4 主循環。
