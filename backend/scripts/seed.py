"""Seed real projects + a sample post. Idempotent (upsert by slug).

Run from the backend/ directory:
    uv run python -m scripts.seed
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert

from app.db import SessionLocal, engine
from app.models import Post, Project

PROJECTS: list[dict] = [
    {
        "slug": "langgraph-construction-rag-steel-meeting",
        "title_en": "Construction Knowledge RAG & Steel Procurement Meeting Automation",
        "title_zh": "營建知識 RAG 與鋼筋採購週會自動化系統",
        "summary_en": "A production-oriented construction knowledge assistant and steel procurement meeting generator built with LangGraph, hybrid RAG, Gemini grounded search, structured extraction, and DOCX automation.",
        "summary_zh": "以 LangGraph、Hybrid RAG、Gemini grounded search、結構化抽取與 Word 自動化打造的營建知識問答與鋼筋採購週會產生系統。",
        "body_en": (
            "## Overview\n\n"
            "A construction-domain AI system designed for two practical workflows: internal construction knowledge Q&A "
            "and weekly steel procurement meeting record generation. The system lets users ask questions against internal "
            "construction manuals, retrieve source-backed answers, request or fill forms, and automatically generate Word "
            "meeting records from live steel-market data, internal inputs, and historical price tables.\n\n"
            "![Construction assistant — system & graph flow](/graph%20flow.png)\n\n"
            "## Use Cases\n\n"
            "- Internal staff can ask construction procedure questions and get answers grounded in company documents\n"
            "- Project teams can find, download, fill, and export construction forms through a conversational flow\n"
            "- Procurement teams can generate weekly steel-purchasing meeting records with Feng Hsin prices, CSC prices, "
            "international scrap / iron ore, Xiben indices, LME copper, historical deltas, and internal notes\n"
            "- Admin users can manage CSC monthly / quarterly price seeds and review generation usage\n\n"
            "## Implementation\n\n"
            "- **LangGraph chat workflow:** `StateGraph` routes through compact_check → unified_intent → retrieval / form / export / responder. "
            "The graph supports long-conversation summarization, intent-aware routing, static form download, static form filling, "
            "dynamic form generation, form continuation, and dynamic export\n"
            "- **CRAG retrieval loop:** retrieved chunks are graded by an LLM; insufficient retrieval triggers query rewriting and "
            "another retrieval pass, capped at 2 retries to keep latency bounded\n"
            "- **Hybrid RAG algorithm:** combines ChromaDB vector search with jieba + BM25 keyword search, then merges rankings using "
            "Reciprocal Rank Fusion (RRF) for better Chinese construction-document retrieval\n"
            "- **Document-aware context building:** retrieved chunks preserve source file, section code, parent headings, tags, and image "
            "references so answers can expose traceable sources instead of generic text\n"
            "- **Steel meeting generation graph:** a separate LangGraph pipeline runs fetch → validate → persist → narrate → render, "
            "separating live data collection, confidence grading, historical storage, slot rendering, and DOCX output\n"
            "- **Market-data extraction:** Feng Hsin weekly prices use Gemini + Google Search grounding plus structured JSON extraction; "
            "Python then derives SD280W, SD420, and SD420W by deterministic business rules\n"
            "- **Deterministic calculation layer:** Xiben, international scrap, historical price deltas, CSC monthly / quarterly values, "
            "and currency conversions are computed in Python to avoid LLM arithmetic drift\n"
            "- **Robust fallback design:** missing or unpublished prices are marked low-confidence, stale borrowed values are display-only "
            "and never persisted, and generated Word fields are visually marked for review\n"
            "- **Streaming UX:** FastAPI streams LangGraph responder tokens over SSE; the frontend also uses a polling workflow for long-running "
            "meeting generation jobs to avoid request timeouts\n"
            "- **Frontend:** Next.js + React + TypeScript workflow UI with a 6-step wizard for meeting generation, CSC override editing, "
            "internal-data completion, result review, and DOCX download\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "這是一套面向營建公司內部使用的 AI 系統，核心場景分成兩條：一是營建知識庫問答，二是鋼筋採購週會記錄自動產生。"
            "使用者可以用聊天方式詢問施工管理制度、查找來源、下載或填寫表單；採購端則能自動抓取本週鋼鐵行情、套入內部資料與歷史價格，"
            "最後輸出可下載的 Word 會議記錄。\n\n"
            "![營建知識助理 — 系統與 graph 流程](/graph%20flow.png)\n\n"
            "## 使用場景\n\n"
            "- 工務／內業人員查詢公司施工管理文件、流程、表單規範與檢核重點\n"
            "- 透過對話找出指定表單、下載空白表、逐步補資料並產出已填寫版本\n"
            "- 採購人員產生每週鋼筋採購會議紀錄，整合豐興盤價、中鋼月盤／季盤、國際廢鋼、鐵礦、LME 銅價與歷史漲跌\n"
            "- 管理者維護中鋼盤價種子資料，並追蹤各使用者產生週會記錄的次數與狀態\n\n"
            "## 技術實作\n\n"
            "- **LangGraph 對話流程：** 以 `StateGraph` 串接 compact_check → unified_intent → retrieval / form / export / responder，"
            "支援長對話摘要、意圖判斷、RAG 問答、靜態表單下載、表單填寫、動態表格生成與匯出\n"
            "- **CRAG 自我修正：** retrieval 後由 grader 判斷資料是否足夠；不足時交給 query_rewriter 改寫查詢並重搜，最多 2 次，兼顧準確度與延遲\n"
            "- **Hybrid RAG 演算法：** ChromaDB 向量搜尋搭配 jieba + BM25 關鍵字搜尋，再用 Reciprocal Rank Fusion 合併排序，提升中文營建文件檢索品質\n"
            "- **來源可追溯：** chunk 保留文件名稱、章節代碼、父層標題、tags 與圖片路徑，回答時能回傳 SourcesPanel 所需來源資訊\n"
            "- **週會產生 Graph：** 另一條 LangGraph pipeline 採 fetch → validate → persist → narrate → render，將抓資料、驗證、存歷史、組 slot、輸出 Word 拆開處理\n"
            "- **鋼價資料抽取：** 豐興盤價以 Gemini + Google Search grounding 搜尋本週開盤資料，再用 structured output 抽取 SD280、廢鋼、型鋼；"
            "SD280W、SD420、SD420W 則由 Python 依商業規則推算\n"
            "- **演算法與規則分工：** 西本新幹線、國際廢鋼、歷史週差、中鋼月盤／季盤與匯率換算由 Python 做 deterministic 計算，"
            "LLM 主要負責搜尋、結構化抽取與段落生成，避免模型自行亂算\n"
            "- **容錯設計：** 尚未公布或抓不到的行情會標成 low confidence；沿用上週價格時標記 stale 且不寫入歷史表，避免產生假的週差資料\n"
            "- **Word 自動化：** 使用 python-docx 將 `{{slot_key}}` 寫入模板；低信心或缺漏欄位會以顏色標示，方便人工複核\n"
            "- **前端流程：** Next.js + React + TypeScript 建立 6 步驟 wizard，包含日期設定、抓取盤價、結果檢視、中鋼盤價覆寫、內部資料補填與 Word 下載\n"
        ),
        "tech": [
            "LangGraph", "FastAPI", "Hybrid RAG", "ChromaDB", "BM25", "RRF",
            "Gemini Grounded Search", "OpenAI Embeddings", "SQLAlchemy", "python-docx", "Next.js", "TypeScript",
        ],
        "links": {"github": "https://github.com/Tsai1030/LangGraph_RAG_SYSTEM", "demo": "https://kccc3798.tail138ec9.ts.net/"},
        "video_url": "https://youtu.be/OpPr688_f8M",
        "period": "2025–",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": True,
        "sort": 1,
    },
    {
        "slug": "eastern-mysticism",
        "title_en": "Eastern Mysticism Platform",
        "title_zh": "東方命理平台",
        "summary_en": "Multi-agent consultation platform with SSE streaming and a custom Zi-Wei chart engine.",
        "summary_zh": "多 Agent 命理諮詢平台，支援 SSE 串流與自製紫微斗數排盤引擎。",
        "body_en": (
            "## Overview\n\n"
            "A production multi-agent platform for Eastern mysticism consultations (Zi Wei Dou Shu, "
            "I Ching, name analysis). I owned the backend agent design and led the frontend.\n\n"
            "![Eastern Mysticism Platform](/Eastern%20Mysticism%20Platform.png)\n\n"
            "## Highlights\n\n"
            "- Multi-layer AI agents built on **LangChain / LangGraph**\n"
            "- **SSE streaming** responses for a live, conversational feel\n"
            "- Self-built Zi-Wei chart engine (`ziwei_calculator.py`) with astronomy via `pyswisseph`\n"
            "- Async micro-services: **Quart** + **Redis Queue**, **PostgreSQL + Pinecone** hybrid storage\n"
            "- **Next.js 15 / React 19** frontend with Three.js / GSAP and multi-language (next-intl)\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "一套產品級的東方命理諮詢平台（紫微斗數、易經、姓名學）。我負責後端 Agent 設計並主導前端。\n\n"
            "![東方命理平台](/Eastern%20Mysticism%20Platform.png)\n\n"
            "## 技術亮點\n\n"
            "- 以 **LangChain / LangGraph** 建構多層次 AI Agent\n"
            "- **SSE 串流**回應，帶來即時對話體驗\n"
            "- 自主開發紫微斗數排盤引擎（`ziwei_calculator.py`），以 `pyswisseph` 進行天文運算\n"
            "- 非同步微服務：**Quart** + **Redis Queue**、**PostgreSQL + Pinecone** 混合儲存\n"
            "- **Next.js 15 / React 19** 前端，搭配 Three.js / GSAP 與多語系（next-intl）\n"
        ),
        "tech": ["LangGraph", "GPT-4o", "Quart", "Redis", "PostgreSQL", "Pinecone", "Next.js 15", "Three.js"],
        "links": {"demo": "https://qiankun.ask-lens.ai/tw"},
        "period": "2025–",
        "role_en": "Full-stack (lead frontend)",
        "role_zh": "全端（前端主導）",
        "featured": True,
        "sort": 2,
    },
    {
        "slug": "multimodal-rag-knowledge-base",
        "title_en": "Multi-modal RAG Knowledge Base Platform",
        "title_zh": "多模態 RAG 知識庫平台",
        "summary_en": "A production-grade, fully containerized multi-modal RAG platform with real-time SSE streaming, multi-turn conversation compaction, session-scoped retrieval, and an admin console — all running locally via Docker Compose.",
        "summary_zh": "生產級、全容器化的多模態 RAG 知識庫平台，具備即時 SSE 串流對話、多輪歷史壓縮、Session 範圍檢索與管理員後台，全部以 Docker Compose 在本機運行。",
        "body_en": (
            "## Overview\n\n"
            "A **production-grade, multi-modal RAG** knowledge base platform featuring real-time streaming "
            "chat, multi-turn conversation-history compaction, session-scoped document retrieval, and an "
            "admin console — fully containerized and running **entirely on local hardware** via Docker "
            "Compose (no external API calls).\n\n"
            "## Implementation\n\n"
            "- **Layered backend:** FastAPI with a clean Router → Service → Repository → Schema architecture, "
            "async SQLAlchemy 2.x (AsyncSession + aiosqlite), Alembic migrations, and JWT (HS256) + bcrypt auth "
            "with role-based access (admin / user)\n"
            "- **Local LLM stack via Ollama:** `gpt-oss` for reasoning/chat, `llava:7b` as the vision model for "
            "image and multi-modal document parsing, and `bge-m3` for 1024-dim GPU embeddings\n"
            "- **RAG engine:** RAGAnything built on **LightRAG**, with custom adapters (LLM / vision / embedding) "
            "and a `ChromaVectorDBStorage` adapter implementing LightRAG's `BaseVectorStorage` interface against ChromaDB\n"
            "- **Multi-modal ingestion:** MinerU for PDF layout/OCR parsing, LibreOffice for DOCX/PPTX/XLSX, and "
            "llava vision captioning for images — all chunked, embedded, and indexed into ChromaDB\n"
            "- **Conversation compaction:** an automatic mechanism that, once a session passes a message "
            "threshold, summarizes older turns via the LLM and keeps recent turns verbatim, keeping the context "
            "window bounded without breaking the conversation\n"
            "- **Session-scoped retrieval:** retrieval is automatically confined to documents attached to the "
            "current session, preventing cross-contamination with the global knowledge base\n"
            "- **Streaming frontend:** Next.js 16 App Router + TypeScript + shadcn/ui + Zustand, consuming an SSE "
            "stream (`useSSEStream`) for live token rendering, with a WebGL galaxy background (OGL)\n"
            "- **Three query modes:** Hybrid (semantic + knowledge graph), Local (focused chunks), and Global "
            "(graph-wide synthesis)\n"
            "- **Infra:** Docker Compose orchestrating ChromaDB, Ollama, backend, and a multi-stage-built "
            "frontend, with health checks and dependency gating\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "一個 **生產級、多模態 RAG** 知識庫平台，具備即時串流對話、多輪對話歷史壓縮、以 Session 為範圍的"
            "文件檢索，以及管理員後台。整套系統 **完全在本機硬體上運行**（不呼叫外部 API），透過 Docker Compose "
            "容器化部署。\n\n"
            "## 技術實作\n\n"
            "- **分層後端：** FastAPI，採 Router → Service → Repository → Schema 清晰分層架構；"
            "async SQLAlchemy 2.x（AsyncSession + aiosqlite）、Alembic 遷移，並以 JWT（HS256）+ bcrypt 實作"
            "身份驗證與角色權限（admin / user）\n"
            "- **本機 LLM 技術棧（Ollama）：** `gpt-oss` 負責推理與對話、`llava:7b` 視覺模型負責圖片與多模態"
            "文件解析、`bge-m3` 負責 1024 維 GPU 向量嵌入\n"
            "- **RAG 引擎：** 以 **LightRAG** 為核心的 RAGAnything，搭配自訂 LLM／視覺／嵌入適配器，並實作 "
            "`ChromaVectorDBStorage` 對接 LightRAG 的 `BaseVectorStorage` 介面與 ChromaDB\n"
            "- **多模態文件解析：** PDF 以 MinerU 進行版面偵測與 OCR、DOCX/PPTX/XLSX 透過 LibreOffice 轉換、"
            "圖片以 llava 視覺模型生成文字說明，所有區塊統一切塊、嵌入並索引至 ChromaDB\n"
            "- **對話壓縮機制：** 當 Session 訊息數超過閾值時，自動以 LLM 摘要較舊訊息、原文保留最近數則，"
            "在不中斷對話體驗的前提下將 Context 維持在可控範圍\n"
            "- **Session 範圍檢索：** 檢索自動限制在當前 Session 所附加的文件，避免與全域知識庫交叉干擾\n"
            "- **串流前端：** Next.js 16 App Router + TypeScript + shadcn/ui + Zustand，透過 SSE（`useSSEStream`）"
            "即時渲染 token，並含 WebGL 星系背景（OGL）\n"
            "- **三種查詢模式：** Hybrid（語意 + 知識圖譜）、Local（聚焦片段）、Global（全域圖譜綜合）\n"
            "- **基礎設施：** Docker Compose 編排 ChromaDB、Ollama、後端與多階段建置的前端，含健康檢查與依賴啟動順序控制\n"
        ),
        "tech": ["LightRAG", "RAG", "Ollama", "ChromaDB", "FastAPI", "Next.js 16", "MinerU", "Docker Compose"],
        "links": {"github": "https://github.com/Tsai1030/Multi-modal-AI-Knowledge-Base-Platform"},
        "video_url": "https://www.youtube.com/embed/kCAHPnSwVV8?rel=0",
        "period": "2025–",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": True,
        "sort": 3,
    },
    {
        "slug": "ziwei-multi-agent-langgraph",
        "title_en": "Ziwei Doushu Multi-Agent AI (LangGraph ReAct)",
        "title_zh": "紫微斗數 Multi-Agent AI 系統（LangGraph ReAct）",
        "summary_en": "A Graph-based multi-agent fortune-telling system using a LangGraph ReAct loop, a custom Python MCP server, ChromaDB RAG, and web search.",
        "summary_zh": "以 LangGraph ReAct Loop 打造的圖式多智能體紫微斗數分析系統，整合自訂 Python MCP Server、ChromaDB RAG 與網路搜尋。",
        "body_en": (
            "## Overview\n\n"
            "A Graph-based **multi-agent** Ziwei Doushu (Chinese astrology) analysis system built on a "
            "**LangGraph ReAct loop**, replacing a traditional linear pipeline. It combines a custom Python "
            "MCP server, a ChromaDB RAG knowledge base, and web search to deliver in-depth readings.\n\n"
            "![Ziwei Doushu Multi-Agent AI](/full%20multi%20agent.png)\n\n"
            "## Implementation\n\n"
            "- **Agent core:** LangGraph `StateGraph` with a Reason → Act → Observe loop "
            "(orchestrator → tools → synthesizer), dynamic conditional-edge routing, and an iteration cap "
            "to keep response time bounded\n"
            "- **Custom MCP server:** FastAPI sub-application mounted at `/mcp`, with a `BaseMCPTool` ABC "
            "and `ToolRegistry` for fast tool extension; includes a `ZiweiChartTool` that scrapes birth-chart data\n"
            "- **RAG:** ChromaDB persistent vector store with OpenAI `text-embedding-3-small`, idempotent "
            "auto-indexing on startup\n"
            "- **Web search:** Tavily Search API with automatic fallback to DuckDuckGo\n"
            "- **LLM:** Claude (Anthropic) for reasoning, tool selection, and answer synthesis\n"
            "- **Frontend:** Next.js 14 App Router + TypeScript + Tailwind CSS, with a Canvas StarField "
            "particle animation and Framer Motion transitions\n"
            "- **Encoding robustness:** multi-stage cp950 / big5-hkscs fallback to fix garbled chart parsing\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "以 **LangGraph ReAct Loop** 打造的圖式 **多智能體** 紫微斗數分析系統，取代傳統線性 pipeline。"
            "結合自訂 Python MCP Server、ChromaDB RAG 知識庫與網路搜尋，提供深度命理分析體驗。\n\n"
            "![紫微斗數 Multi-Agent AI 系統](/full%20multi%20agent.png)\n\n"
            "## 技術實作\n\n"
            "- **代理核心：** LangGraph `StateGraph`，採 Reason → Act → Observe 循環"
            "（orchestrator → tools → synthesizer），動態條件邊路由，並設迭代上限確保回應時間可控\n"
            "- **自訂 MCP Server：** FastAPI sub-application 掛載於 `/mcp`，以 `BaseMCPTool` 抽象類別與 "
            "`ToolRegistry` 支援快速擴充工具；內含爬取命盤的 `ZiweiChartTool`\n"
            "- **RAG：** ChromaDB 持久化向量庫搭配 OpenAI `text-embedding-3-small`，啟動時自動索引（idempotent，不重複建立）\n"
            "- **網路搜尋：** 主用 Tavily Search API，自動 fallback 至 DuckDuckGo\n"
            "- **LLM：** Claude（Anthropic）負責推理、工具選擇與答案生成\n"
            "- **前端：** Next.js 14 App Router + TypeScript + Tailwind CSS，含 Canvas StarField 粒子動畫與 Framer Motion 轉場\n"
            "- **編碼修復：** cp950 / big5-hkscs 多重 fallback，解決命盤解析亂碼問題\n"
        ),
        "tech": ["LangGraph", "ReAct Agent", "MCP", "Claude", "ChromaDB", "Tavily", "FastAPI", "Next.js 14"],
        "links": {"github": "https://github.com/Tsai1030/Full-multi-agent"},
        "github_stars": 20,
        "github_forks": 9,
        "period": "2025–",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": True,
        "sort": 4,
    },
    {
        "slug": "rag-air-pollution",
        "title_en": "RAG Air-Pollution Q&A",
        "title_zh": "RAG 空污問答系統",
        "summary_en": "My Master's thesis system — deployed publicly via DuckDNS + Nginx with HTTPS.",
        "summary_zh": "我的碩士論文系統——透過 DuckDNS + Nginx 公開部署並支援 HTTPS。",
        "body_en": (
            "## Overview\n\n"
            "My Master's thesis: a RAG Q&A platform focused on air pollution, environmental policy, and "
            "public health — combining semantic retrieval with a local LLM.\n\n"
            "## Implementation\n\n"
            "- **Embeddings:** BAAI/bge-m3 (Chinese semantic), recursive punctuation-aware chunking\n"
            "- **Vector DB:** ChromaDB with rich metadata (source, page, topic), **MMR + reranking**\n"
            "- **Inference:** Gemma 3:12B via **Ollama**, orchestrated with **LangChain**, served by **FastAPI**\n"
            "- **Frontend:** React + Vite chat UI with format switching (paragraph / bullet / emoji)\n"
            "- **Eval:** RAGAS (faithfulness, context & answer relevance)\n"
            "- **Deploy:** DuckDNS dynamic domain + Nginx reverse proxy with Let's Encrypt HTTPS\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "我的碩士論文系統：聚焦空氣污染、環境政策與醫療健康的 RAG 問答平台，結合語意檢索與本地 LLM。\n\n"
            "## 技術實作\n\n"
            "- **嵌入：** BAAI/bge-m3（中文語意），遞迴式標點切割\n"
            "- **向量庫：** ChromaDB，搭配豐富 metadata（來源、頁碼、主題），**MMR + Reranking**\n"
            "- **推論：** 以 **Ollama** 部署 Gemma 3:12B，**LangChain** 串接流程，**FastAPI** 提供 API\n"
            "- **前端：** React + Vite 聊天介面，支援段落／條列／Emoji 格式切換\n"
            "- **評估：** RAGAS（Faithfulness、Context / Answer Relevance）\n"
            "- **部署：** DuckDNS 動態網域 + Nginx 反向代理，Let's Encrypt HTTPS\n"
        ),
        "tech": ["bge-m3", "ChromaDB", "Gemma 3:12B", "LangChain", "FastAPI", "MMR + Rerank", "RAGAS"],
        "links": {"github": "https://github.com/Tsai1030/deploy-safe"},
        "video_url": "https://youtu.be/X5xws68YYRo",
        "period": "2024–2025",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": True,
        "sort": 5,
    },
    {
        "slug": "unsloth-lora-finetune",
        "title_en": "Unsloth LoRA Fine-tuning System",
        "title_zh": "Unsloth LoRA 微調系統",
        "summary_en": "A modular LoRA fine-tuning pipeline built on Unsloth for sentiment analysis, with 4-bit quantization, early stopping, and adaptive Llama-2/Llama-3 support.",
        "summary_zh": "以 Unsloth 打造的模組化 LoRA 微調系統，用於情感分析，支援 4-bit 量化、Early Stopping 與 Llama-2/Llama-3 自適應切換。",
        "body_en": (
            "## Overview\n\n"
            "A comprehensive **LoRA (Low-Rank Adaptation)** fine-tuning system built on **Unsloth** for "
            "sentiment-analysis tasks. It covers the full lifecycle — training, evaluation, and interactive "
            "testing — and adapts automatically to different base models (Llama-2 / Llama-3).\n\n"
            "## Implementation\n\n"
            "- **Efficient training:** Unsloth optimization for ~2x faster training, with **4-bit "
            "quantization** so large models fit on a single consumer GPU (~7GB VRAM)\n"
            "- **LoRA config:** rank-32 adapters on attention layers, cosine LR scheduling, ~100MB adapter output\n"
            "- **Early stopping:** custom callback with patience/threshold to prevent overfitting and cut training time\n"
            "- **Modular architecture:** clean separation across `config` / `data_processor` / `model_manager` "
            "/ `training_pipeline` / `evaluator` / `model_saver`, orchestrated by a single `lora_system` controller\n"
            "- **Dataset:** IMDb movie reviews (25k samples, 80/20 split), extensible to other Hugging Face datasets\n"
            "- **Tooling:** interactive & automated training launchers, model version management, and a free-form "
            "text tester returning predictions with confidence scores\n"
            "- **Result:** ~85–90% accuracy on the IMDb test set, ~15–30 min training on an RTX 4090\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "以 **Unsloth** 打造、用於情感分析的完整 **LoRA（Low-Rank Adaptation）** 微調系統，"
            "涵蓋訓練、評估到互動測試的完整流程，並能依不同基礎模型（Llama-2 / Llama-3）自動調整設定。\n\n"
            "## 技術實作\n\n"
            "- **高效訓練：** 透過 Unsloth 最佳化達約 2 倍訓練速度，搭配 **4-bit 量化**，"
            "讓大模型可在單張消費級 GPU（約 7GB VRAM）上訓練\n"
            "- **LoRA 設定：** 在 attention 層套用 rank-32 adapter，採 cosine 學習率排程，輸出約 100MB adapter\n"
            "- **Early Stopping：** 自訂 callback，以 patience／threshold 防止過擬合並節省訓練時間\n"
            "- **模組化架構：** `config`／`data_processor`／`model_manager`／`training_pipeline`／"
            "`evaluator`／`model_saver` 清楚分層，由單一 `lora_system` 主控制器整合\n"
            "- **資料集：** IMDb 影評（2.5 萬筆，80/20 切分），可擴充至其他 Hugging Face 資料集\n"
            "- **工具：** 互動式與自動化訓練啟動腳本、模型版本管理，以及可自由輸入文字、回傳信心分數的測試工具\n"
            "- **成果：** IMDb 測試集約 85–90% 準確率，RTX 4090 約 15–30 分鐘完成訓練\n"
        ),
        "tech": ["Unsloth", "LoRA", "Llama-3", "PyTorch", "Hugging Face", "4-bit Quantization"],
        "links": {"github": "https://github.com/Tsai1030/Unsloth-Lora-fine-tune"},
        "period": "2025",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": False,
        "sort": 6,
    },
    {
        "slug": "graphify-atlas-knowledge-workspace",
        "title_en": "Graphify Atlas — Graph-Powered Knowledge Workspace",
        "title_zh": "Graphify Atlas — 圖譜知識工作台",
        "summary_en": "A cinematic, graph-backed knowledge workspace that turns a private Markdown corpus into a queryable knowledge graph with conversational retrieval, evidence inspection, and Obsidian browsing.",
        "summary_zh": "以知識圖譜為核心的知識工作台，將私有 Markdown 文件轉成可對話查詢的知識圖譜，支援對話檢索、證據檢視與 Obsidian 瀏覽。",
        "body_en": (
            "## Overview\n\n"
            "**Graphify Atlas** is a graph-powered knowledge workspace that turns a private document corpus "
            "into an explorable knowledge graph — supporting conversational retrieval, graph-backed evidence "
            "inspection, image/table previews, and optional Obsidian browsing of community clusters and node notes.\n\n"
            "The published repo is intentionally a **data-free shareable shell**: it ships the product "
            "architecture, frontend, and retrieval scaffolding, while the private corpus and generated graph "
            "outputs stay local and out of version control — a clean pattern for open-sourcing a UI without "
            "exposing confidential data.\n\n"
            "## Implementation\n\n"
            "- **Graph retrieval:** built on **Graphify**, which parses a local Markdown corpus into graph "
            "outputs (`graph.json`, an HTML graph view, a wiki, and an Obsidian vault) used as the retrieval source\n"
            "- **Workspace UI:** a landing page plus a dedicated `/home` workspace split into an Atlas Rail "
            "(context & dataset stats), a Conversation Canvas (main interaction), a Signal Rail (source signals "
            "& related nodes), and a floating Evidence Viewer for focused graph exploration\n"
            "- **Frontend:** Next.js + React + TypeScript + Tailwind CSS with shadcn/ui primitives and a "
            "cinematic, motion-driven landing experience\n"
            "- **Chat:** conversational Q&A over the generated graph via the OpenAI API, available both in the "
            "web workspace and a terminal chat helper\n"
            "- **Local-first workflow:** PowerShell scripts (`build_kb` / `chat_kb` / `run_frontend`) that "
            "bootstrap a venv, install Graphify, build the graph from `data_markdown/`, and launch the app\n"
            "- **Obsidian integration:** generated node notes, community-cluster overviews, and a graph canvas "
            "that can be opened directly as an Obsidian vault for visual knowledge-map navigation\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "**Graphify Atlas** 是一個以知識圖譜為核心的知識工作台，將私有文件語料轉換成可探索的知識圖譜，"
            "支援對話式檢索、圖譜證據檢視、圖片／表格預覽，以及可選的 Obsidian 社群群組與節點筆記瀏覽。\n\n"
            "公開版本刻意設計為 **不含資料的可分享外殼**：開源產品架構、前端與檢索流程，而私有語料與生成的圖譜"
            "輸出全部留在本機、不納入版控——是一種「公開介面與架構、但不暴露機密資料」的乾淨模式。\n\n"
            "## 技術實作\n\n"
            "- **圖譜檢索：** 以 **Graphify** 為核心，將本機 Markdown 語料解析為圖譜輸出"
            "（`graph.json`、HTML 圖譜視圖、wiki 與 Obsidian vault），作為檢索來源\n"
            "- **工作區介面：** 包含產品 landing page 與專屬 `/home` 工作區，分為 Atlas Rail（情境與資料集統計）、"
            "Conversation Canvas（主要互動區）、Signal Rail（來源訊號與關聯節點），以及浮動式 Evidence Viewer"
            "（聚焦圖譜探索）\n"
            "- **前端：** Next.js + React + TypeScript + Tailwind CSS，搭配 shadcn/ui 元件與動態運鏡的 landing 體驗\n"
            "- **對話：** 透過 OpenAI API 對生成的圖譜進行對話式問答，可在 Web 工作區或終端機 chat 工具中使用\n"
            "- **本機優先流程：** 以 PowerShell 腳本（`build_kb` / `chat_kb` / `run_frontend`）自動建立虛擬環境、"
            "安裝 Graphify、從 `data_markdown/` 建立圖譜並啟動應用\n"
            "- **Obsidian 整合：** 生成節點筆記、社群群組概覽與 graph canvas，可直接以 Obsidian vault 開啟，"
            "進行視覺化知識地圖導覽\n"
        ),
        "tech": ["Graphify", "Knowledge Graph", "Next.js", "TypeScript", "Tailwind CSS", "shadcn/ui", "OpenAI API", "Obsidian"],
        "links": {"github": "https://github.com/Tsai1030/Graphify-Wiki"},
        "period": "2025–",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": False,
        "sort": 7,
    },
]

POSTS: list[dict] = [
    {
        "slug": "building-a-rag-system-end-to-end",
        "title_en": "Building a RAG System End to End",
        "title_zh": "從零打造一套 RAG 系統",
        "excerpt_en": "Notes from shipping a real RAG Q&A system — chunking, embeddings, retrieval tuning, and the parts nobody warns you about.",
        "excerpt_zh": "把一套真正能用的 RAG 問答系統做上線的筆記——切塊、嵌入、檢索調校，以及那些沒人提醒你的細節。",
        "body_en": (
            "Retrieval-Augmented Generation looks simple on a slide: embed your docs, search, stuff the "
            "context into a prompt. Shipping one taught me the gap is in the details.\n\n"
            "## 1. Chunking matters more than the model\n\n"
            "Recursive, punctuation-aware splitting kept semantics intact and beat naive fixed-size chunks "
            "on retrieval quality.\n\n"
            "## 2. Metadata is half the system\n\n"
            "Tagging each chunk with source, page, and topic let me filter before similarity search — "
            "fewer, better candidates.\n\n"
            "## 3. MMR + reranking\n\n"
            "Maximal Marginal Relevance balanced relevance with coverage; a rerank pass cleaned up the top-k.\n\n"
            "## 4. Guardrails for the UI\n\n"
            "LLM output isn't always valid — a formatter + graceful fallbacks kept the frontend from breaking "
            "when a field was missing.\n"
        ),
        "body_zh": (
            "RAG 在投影片上看起來很簡單：把文件嵌入、檢索、把內容塞進 prompt。真正做上線後，我才發現魔鬼都在細節裡。\n\n"
            "## 1. 切塊比模型更關鍵\n\n"
            "遞迴、考慮標點的切割能保留語意，檢索品質明顯優於單純的固定長度切塊。\n\n"
            "## 2. Metadata 是系統的一半\n\n"
            "為每個 chunk 標上來源、頁碼、主題，就能在相似度搜尋前先過濾——候選更少、更準。\n\n"
            "## 3. MMR + Reranking\n\n"
            "以 Maximal Marginal Relevance 平衡相關性與覆蓋度，再加一段 rerank 把 top-k 清乾淨。\n\n"
            "## 4. 給前端的防護機制\n\n"
            "LLM 輸出不一定合法——加一層 formatter 與優雅的 fallback，讓欄位缺漏時前端也不會壞掉。\n"
        ),
        "tags": ["RAG", "LLM", "Notes"],
        "reading_minutes": 6,
        "published": True,
        "published_at": datetime.now(timezone.utc),
    },
]


async def _upsert(session, model, rows: list[dict]) -> None:
    for row in rows:
        stmt = insert(model).values(**row)
        update_cols = {k: getattr(stmt.excluded, k) for k in row if k != "slug"}
        stmt = stmt.on_conflict_do_update(index_elements=["slug"], set_=update_cols)
        await session.execute(stmt)


async def main() -> None:
    async with SessionLocal() as session:
        await _upsert(session, Project, PROJECTS)
        await _upsert(session, Post, POSTS)
        await session.commit()
    await engine.dispose()
    print(f"Seeded {len(PROJECTS)} projects and {len(POSTS)} posts.")


if __name__ == "__main__":
    asyncio.run(main())
