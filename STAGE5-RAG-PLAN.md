# Stage 5 計畫書 — RAG 聊天助手

> 目標：使用者在站上任一頁開聊天，詢問關於蔡承紘 / 專案 / 部落格的問題；助手用 Gemini 作答，
> 答案內含**行內連結**導向 `/projects/<slug>`、`/blog/<slug>` 或首頁 `/`，並在下方附**來源清單**。
> 雙語（依介面語言）。整體 RAG 以 **LangGraph** 編排。

決策（已確認）：Embedding **768 維**；**雙語都索引、依介面語言回答**；**行內連結＋底部來源清單**；**全站右下浮動聊天**。

---

## 1. 模型與套件
- **LLM**：`gemini-3.5-flash`（已確認）
- **Embedding**：`gemini-embedding-2`（已確認）— 最大序列 8,192 tokens；MRL 最高 3,072 維，本專案**截斷為 768 維**使用（`output_dimensionality=768`）
- **後端套件**：`langgraph`、`langchain-core`、`langchain-google-genai`、`pgvector`（SQLAlchemy 向量型別）
- **金鑰**：`GOOGLE_API_KEY`（後端 `.env` / Render Environment；前端不接觸）
- 走雲端 API、不在本機跑模型 → **Render 免費方案即可服務**。

## 2. 資料模型（新增 `doc_chunks`）
```sql
doc_chunks(
  id PK,
  source_type  text,        -- 'project' | 'post' | 'profile'
  source_id    int NULL,    -- projects.id / posts.id（profile 為 NULL）
  lang         text,        -- 'en' | 'zh'
  url          text,        -- 連結目標：/projects/<slug>、/blog/<slug>、/
  title        text,        -- 來源標題（顯示用）
  chunk_index  int,
  content      text,        -- 該 chunk 純文字
  embedding    vector(768),
  created_at   timestamptz
)
-- 索引：HNSW (vector_cosine_ops)
```
**Profile / 首頁來源**：在後端放一份 profile 文件（中英，取自 About / Hero 內容），`url = "/"`，讓助手能回答「你是誰」並導回首頁。

## 3. 索引流程（`scripts/reindex.py`）
1. 讀 `projects`（title＋summary＋body，分 en/zh）、`posts`（title＋excerpt＋body，en/zh）、`profile`（en/zh）。
2. 切塊：先移除 Markdown 內的影片/圖片語法，依標題/段落切，每塊約 500–800 字、重疊 ~80。
3. 每塊呼叫 Gemini embedding（768 維）。
4. 清空並重建 `doc_chunks`（每塊帶 `url`、`title`、`lang`、`source_type/id`）。
5. 執行：`uv run python -m scripts.reindex`（內容更新後重跑；因前後端同一個 Supabase DB，本機跑即可）。

## 4. 檢索 + 生成（LangGraph `StateGraph`）
State：`{ messages, query, lang, docs, answer, sources }`
- `prepare`：取最後一則使用者問題為 query；`lang` 由前端帶入。
- `retrieve`：query → Gemini embedding → pgvector `embedding <=> :q`（cosine）取 top-k（k≈6）；優先取該語言，不足再補另一語言。
- `build_context`：把 docs 整理成「[title](url) + 內容」清單，並對 `url` 去重。
- `generate`：Gemini 2.5 Flash，低溫度。System prompt 重點：
  - 你是蔡承紘個人網站的助理，**只依提供的內容**回答關於他 / 專案 / 部落格的問題。
  - 用**使用者的語言**回答。
  - 引用時**只用 context 內的 url**，以 Markdown 行內連結帶出（不可自行編造連結）。
  - 不知道就誠實說，並建議看首頁；婉拒無關問題。
- 串流輸出 answer；結束時附**去重後的 sources**（`{title, url}`）。

## 5. API（FastAPI）
- `POST /chat`：body `{ messages: [{role, content}], lang }`。
- 回傳 **SSE**：先串 `token` 事件（逐字），最後送 `sources` 事件與 `done`。
- 以 LangGraph streaming（`astream`）接到 `StreamingResponse(media_type="text/event-stream")`。
- **無狀態**：前端帶最近 N 則訊息（先不做 server-side session）。
- Render 需新增 `GOOGLE_API_KEY` 環境變數。

## 6. 前端（聊天小工具 `ChatWidget`）
- **全站右下浮動按鈕**，mount 在 `app/layout.tsx`，點開展開面板（editorial 風格、主題色）。
- 呼叫 `${NEXT_PUBLIC_API_URL}/chat`，用 `fetch` + `ReadableStream` 讀 SSE、逐字顯示。
- 用 `react-markdown` 渲染答案；**站內連結**（以 `/` 開頭）改用 router 導航（不整頁刷新），外部連結開新分頁。
- 下方「來源」區塊列出 sources（可點、站內導航）。
- 雙語 UI（接 LangContext），並把目前 `lang` 傳給後端；`prefers-reduced-motion` 友善。

## 7. 部署
- 後端 deps 增加 → Render 重建；Render Environment 加 `GOOGLE_API_KEY`。
- `doc_chunks` migration（含 HNSW index）→ 部署時 `alembic upgrade head` 自動套用。
- 首次跑一次 `reindex`（本機對 Supabase 跑即可）。
- 前端加 `ChatWidget` → Vercel 重部署（`NEXT_PUBLIC_API_URL` 已設）。

## 8. 實作子步驟（順序）
- **S5.1** Schema：`doc_chunks` model + migration（`vector(768)` + HNSW）；加 `langgraph / langchain-google-genai / pgvector` 等套件；`GOOGLE_API_KEY` 進 config。
- **S5.2** Ingestion：profile 文件 + chunker + embedder + `reindex.py`；跑一次、驗證 chunk 筆數與向量維度。
- **S5.3** 檢索 + LangGraph graph + `POST /chat`（SSE）；用 curl/httpx 驗證一題（含來源連結）。
- **S5.4** 前端 `ChatWidget`（浮動、串流、markdown 連結、來源、雙語）。
- **S5.5** 部署：Render 加 key + migration + reindex；前端重部署；端到端測試。

## 9. 成本 / 風險 / 後續
- Gemini Flash + embedding 成本極低（個人流量多在免費額度內）。
- Render 免費冷啟動：首次 `/chat` 較慢（~30–60 秒）。
- 可選後續：rate limit、對話 session（LangGraph checkpointer）、reindex 自動化（admin 存檔觸發）。

## 10. 已確認的模型
1. **LLM**：`gemini-3.5-flash`
2. **Embedding**：`gemini-embedding-2`（MRL，`output_dimensionality=768`）
