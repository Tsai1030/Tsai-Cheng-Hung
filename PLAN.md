# 個人網站建置計畫書（履歷 / 部落格 / 專案 + AI 助手）

> 對象：蔡承紘個人網站
> 決策日期：2026-06-03
> 架構：**Option B** — Python 後端（FastAPI + SQLAlchemy）＋ Next.js 前端

---

## 1. 系統架構（Topology）

```
┌─────────────┐        HTTPS / JSON         ┌──────────────────────────┐
│   Vercel    │ ─────────────────────────►  │   Render / Railway / Fly  │
│  Next.js    │  ◄─── SSE（聊天串流）─────── │   FastAPI + SQLAlchemy     │
│  （前端）    │                             │   + Alembic + RAG          │
└─────────────┘                             └────────────┬─────────────┘
                                                          │ asyncpg
                                                 ┌────────▼─────────┐
                                                 │ Supabase Postgres │
                                                 │   + pgvector      │
                                                 └───────────────────┘
```

原則：
- **Next.js 不直接連資料庫**，只透過 FastAPI API 取得內容並渲染（頁面用 SSG/ISR，聊天用 client fetch）。
- **Alembic 是 schema 的唯一來源**，整個專案不使用 Prisma。
- **雙語 payload**：API 同時回傳 `*_en` 與 `*_zh`，前端 EN/中 切換即時生效（沿用目前的 `<L>` 機制）。
- 內文（body）以 **Markdown** 儲存，前端用 `react-markdown` 渲染。
- 詳細頁網址用 **slug**（`/projects/<slug>`、`/blog/<slug>`），數字 id 僅作為內部主鍵。
- **內容更新（ISR）策略**：頁面以時間式 `revalidate`（預設 300 秒）為基底；另提供受保護的 on-demand revalidate endpoint（`/api/revalidate?secret=...`），seed/更新內容後由腳本或手動呼叫即可即時刷新。
- **資料庫連線**：Alembic migration 走 **direct 連線（5432）**；FastAPI runtime 走 **session pooler 或 direct**（Render 為常駐程序，SQLAlchemy 連線池即可）。若改用 Supabase transaction pooler（PgBouncer / 6543，多見於 serverless），asyncpg 需關閉 prepared statement 快取：`create_async_engine(..., connect_args={"statement_cache_size": 0})`，必要時搭配 `NullPool`。

---

## 2. 專案目錄結構（Monorepo）

```
resume4/
├── app/ components/ ...      # 既有 Next.js 前端（部署到 Vercel）
├── lib/api.ts                # 新增：型別化 API client（讀 NEXT_PUBLIC_API_URL）
└── backend/                  # 新增：Python 服務（部署到 Render）
    ├── app/
    │   ├── main.py           # FastAPI app + CORS
    │   ├── db.py             # async engine / session
    │   ├── models.py         # SQLAlchemy models
    │   ├── schemas.py        # Pydantic DTOs
    │   ├── routers/          # projects.py, posts.py, chat.py, admin.py
    │   └── rag/              # chunk.py, embed.py, retrieve.py（Stage 5）
    ├── alembic/              # migrations
    ├── scripts/seed.py       # 內容建檔
    ├── pyproject.toml
    └── Dockerfile
```

---

## 3. 資料模型（Data Model，定稿）

```sql
projects(
  id PK, slug UNIQUE,
  title_en, title_zh, summary_en, summary_zh,
  body_en, body_zh,                       -- Markdown
  cover_image, tech text[], links jsonb,  -- {github, demo, paper}
  period, role_en, role_zh,
  meta_title_en, meta_title_zh,            -- SEO；留空自動由 title 帶入
  meta_description_en, meta_description_zh, -- SEO；留空自動由 summary 帶入
  og_image,                                -- 分享預覽圖；留空 fallback 至 cover_image
  featured bool, sort int, published bool,
  created_at, updated_at )

posts(
  id PK, slug UNIQUE,
  title_en, title_zh, excerpt_en, excerpt_zh,
  body_en, body_zh,                       -- Markdown
  cover_image, tags text[], reading_minutes int,
  meta_title_en, meta_title_zh,            -- SEO；留空自動由 title 帶入
  meta_description_en, meta_description_zh, -- SEO；留空自動由 excerpt 帶入
  og_image,                                -- 分享預覽圖；留空 fallback 至 cover_image
  published bool, published_at, created_at, updated_at )

doc_chunks(                               -- 只有 Stage 5 才建立
  id PK, source_type, source_id, url, lang,
  title, chunk text, embedding vector(1536),
  created_at )                            -- HNSW index, cosine 距離
```

---

## 4. API 介面（Contract）

| Method | Route | 用途 |
|---|---|---|
| GET | `/projects?published=true` | 專案卡片列表（含雙語） |
| GET | `/projects/{slug}` | 專案完整內容 |
| GET | `/posts?published=true` | 文章卡片列表 |
| GET | `/posts/{slug}` | 文章完整內容 |
| POST | `/chat`（SSE） | RAG 回答串流 + 來源連結 — *Stage 5* |
| POST/PUT/DELETE | `/admin/...`（Bearer token） | 內容 CRUD — *Stage A（可選）* |
| —（CLI） | `scripts/reindex.py` | 重新建立向量 — *Stage 5*（腳本，非 API） |

雙語 payload 範例：每筆同時含 `title_en` / `title_zh`，前端依目前語系挑選。

---

## 5. 階段清單（Stage List）

> RAG 助手放在**最後**；建議 **Stage 2 完成後就先部署**，持續取得回饋。

### Stage 0 — 基礎建設（Foundations）
- 建立 Supabase 專案；執行 `create extension vector;`，取得連線字串（pooled + direct）。
- 建立 `backend/` 骨架（FastAPI、async SQLAlchemy、Alembic、pydantic-settings）、`pyproject.toml`、`.env.example`、Dockerfile。
- 前端新增 `lib/api.ts` 與 `NEXT_PUBLIC_API_URL` 環境變數。
- **驗收：** 本機 `GET /health` 回 200；後端能連上 Supabase。

### Stage 1 — 後端：內容 API
- 建立 `projects` / `posts` 的 SQLAlchemy models 與第一份 Alembic migration。
- Pydantic DTOs；讀取端點（列表 + by-slug）；設定 CORS 允許 Vercel 網域。
- `scripts/seed.py` 匯入真實專案與一篇範例文章。
- 內容建檔一律透過 `scripts/seed.py`（SQLAlchemy）；**Stage 1 只做 read API，不做 admin 寫入 API**（避免過早建置；寫入後台延到 Stage A）。
- **驗收：** `GET /projects`、`/projects/{slug}` 能回傳種子資料（用 `/docs` Swagger 或 curl 測）。

### Stage 2 — 前端：Projects 功能
- 以 API 資料取代目前的 `/projects` 佔位頁，做成 **卡片列表**（沿用 editorial 風格）。
- 新增 **`/projects/[slug]`** 詳細頁（server component），用 `react-markdown` 渲染內文，含封面、技術標籤、連結、EN/中；`generateMetadata` 套用 SEO 欄位（meta/og，留空則 fallback）。
- 設定 ISR：頁面 `export const revalidate = 300`；新增受保護的 `/api/revalidate`（用 `REVALIDATE_SECRET`）供內容更新後即時刷新。
- 首頁「Selected Work」與「More →」改接 API（featured 專案，單一資料來源）。
- **驗收：** 點卡片進詳細頁；語言切換正常；SEO/Lighthouse 正常。

### Stage 3 — 前端：Blog 功能（同樣式）
- `/blog` 列表 + `/blog/[slug]` 詳細頁（tags、閱讀時間、日期）。
- **開啟 header 的 Blog 分頁**（目前是 disabled）。
- **驗收：** 部落格列表與詳細頁可雙語從 API 渲染。

### Stage 4 — 部署 + 內容建檔流程
- 後端部署到 **Render**（環境變數；release 時用 **direct 連線**跑 Alembic migrate；runtime 連線依「資料庫連線」原則；CORS 設定 Vercel 網域）。
- Vercel 設定 `NEXT_PUBLIC_API_URL`、`REVALIDATE_SECRET`，重新部署前端。
- 內容建檔：透過 `seed.py` / SQLAlchemy 直接寫 DB；寫入後呼叫 `/api/revalidate` 即時刷新（平時另有時間式 ISR 兜底）。
- **admin 後台 UI 不在此階段**，列為可選的 Stage A。
- **驗收：** 線上前端讀到線上內容；新增一筆專案並觸發 revalidate → 立即出現。

### Stage 5 — RAG 聊天助手（最後，Python）
- 建立 `doc_chunks` migration（pgvector）＋ HNSW cosine index。
- **Ingestion：** 以 `scripts/reindex.py`（或併入 seed 流程）將 projects/posts/about 切塊 → 產生 embedding → 存入（含 `url`、`lang`）；內容更新後重跑此腳本（若日後做了 Stage A admin，可改為存檔自動觸發）。
- **Retrieve：** 將使用者問題轉成向量 → pgvector top-k（依語言過濾）。
- **Generate：** LLM 帶入檢索內容，限制在「關於我 / 部落格」範圍，回答並附**來源連結**；用 FastAPI SSE 串流。
- **前端：** 浮動聊天小工具（EN/中），渲染串流回答 + 可點擊的來源連結。
- **驗收：** 問一個問題 → 得到有根據的回答，且連結能正確導向對應的 `/projects` 或 `/blog` 頁。

### Stage A（可選，延後）— Admin 後台
- 受保護的 admin 寫入 API（Bearer token）＋ Next.js `/admin` 後台 UI，可線上新增/編輯 projects、posts；存檔後自動 revalidate 並 reindex。
- 僅在「想離開 seed 腳本、改用線上編輯」時才做；在那之前所有內容皆由 `seed.py` 建檔。

---

## 6. 待定決策（到該階段再定，目前不阻塞）
- **Stage 4：** Python 主機選 Render / Railway / Fly（Render 最簡單；免費方案會休眠 → 冷啟動較慢）。
- **Stage 5：** Embedding 模型 + LLM。預設候選：**OpenAI `text-embedding-3-small`（1536 維）** + **`gpt-4o-mini`**。註：自架 bge-m3 需要較大記憶體（付費方案），用雲端 embedding API 可避開。此決定會定下 `vector(N)`，故於 Stage 5 確認。
- **內容建檔：** 先用 seed 腳本（Stage 1）；線上編輯後台列為可選的 Stage A。

## 7. 成本 / 風險
- Supabase 免費方案 + Render 免費方案 + LLM/embedding 金鑰（此流量下幾乎只花幾分錢）即可涵蓋全部。
- 免費 Python 主機會休眠 → 首次請求較慢；若在意可升級到約 $7/月方案。
- 兩處部署 + CORS 是 Option B 的主要額外維運成本（為了能用 Python/SQLAlchemy/LangChain 的取捨）。

---

## 8. 目前狀態
- ✅ 前端（Editorial 風格）已用 Next.js + Tailwind v4 建好，首頁完成（Hero / About / Career Slices / Experience / Skills / Projects / Publication / Footer）。
- ✅ `/projects` 目前是佔位頁；header「Projects」會捲動到首頁 Selected Work，「More →」連到 `/projects`。
- ⏳ 下一步：**Stage 0**（基礎建設）。
