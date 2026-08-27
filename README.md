# agent-lab

從零用 Python 手寫一個簡易 AI agent，並一步步加上 **harness**（讓模型可靠工作的那層規則、邊界與檔案），
藉此理解 [Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/zh-TW/) 每個設計原則背後的「為什麼」。

這是一個學習紀錄型的作品集：每個階段先讓裸 agent 跑、記錄它怎麼失敗，再加上對應的 harness 元件，用 commit 歷史呈現前後差異。

## 特色

- **零依賴**：只用 Python 標準函式庫（`urllib`、`json`、`pathlib`…），不裝任何套件，原理不被 SDK 遮住。
- **本機模型**：透過 Ollama 跑 `qwen2.5:3b`，免費、不需 API key；之後換 Anthropic API 只需改 `chat()` 一個函式。
- **親手寫**：程式碼由我（Python 初學者）撰寫，Claude 擔任指導者——講解概念與語法、檢查、指錯，不代寫程式。
- **SDD 紀律**：每個學習階段一份規格與任務清單（提案 → 實作 → 歸檔），先寫清楚要做什麼再動手。

## 環境需求

- macOS / Linux，Python 3.10+
- [Ollama](https://ollama.com) 已安裝並啟動（預設 `http://localhost:11434`）
- 模型：`ollama pull qwen2.5:3b`（約 1.9 GB；8 GB RAM 機器可跑）

## 執行

```bash
python3 agent.py
```

目前版本會送一句問候給模型並印出回覆，用來驗證與 Ollama 的連線。

## 專案結構

```
agent.py           # agent 主程式（目前只有 chat()）
LEARNING_PLAN.md   # 六階段學習路線與每階段對應的講次、驗收
README.md
```

## 學習路線

| Step | 主題 | 對應講次 | 狀態 |
|---|---|---|---|
| 1 | 最小 agent 循環：模型 ↔ 工具 | L02、L13 | 🔄 進行中（1/4） |
| 2 | 劃清邊界：路徑沙盒、步數上限 | L07 | ⬜ |
| 3 | 功能清單 `feature_list.json` | L08 | ⬜ |
| 4 | 完成前強制驗證 | L09、L10 | ⬜ |
| 5 | 可觀測：每步寫 log、可回放 | L11 | ⬜ |
| 6 | 跨 session 交接與初始化 | L05、L06、L12 | ⬜ |

細節見 [LEARNING_PLAN.md](LEARNING_PLAN.md)。

## 開發日誌

- **2026-08-26** — 環境就緒。原本選 7B 模型，在 Intel i5 / 8 GB 機器上 swap 到跑不動（3 分鐘無回應），換 3B 後 8 秒回話：第一課就是「環境本身也是 harness 的一部分」。完成 Step 1-1 `chat()`。
