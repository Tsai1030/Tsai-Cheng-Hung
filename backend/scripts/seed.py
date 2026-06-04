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
        "slug": "eastern-mysticism",
        "title_en": "Eastern Mysticism Platform",
        "title_zh": "東方命理平台",
        "summary_en": "Multi-agent consultation platform with SSE streaming and a custom Zi-Wei chart engine.",
        "summary_zh": "多 Agent 命理諮詢平台，支援 SSE 串流與自製紫微斗數排盤引擎。",
        "body_en": (
            "## Overview\n\n"
            "A production multi-agent platform for Eastern mysticism consultations (Zi Wei Dou Shu, "
            "I Ching, name analysis). I owned the backend agent design and led the frontend.\n\n"
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
        "sort": 1,
    },
    {
        "slug": "multimodal-knowledge-base",
        "title_en": "Multi-modal AI Knowledge Base",
        "title_zh": "多模態 AI 知識庫",
        "summary_en": "Fully local RAG platform: upload PDFs & images, parse, index, and chat — data never leaves the box.",
        "summary_zh": "完全本地的 RAG 平台：上傳 PDF 與圖片，自動解析、索引、問答，資料不外傳。",
        "body_en": (
            "## Overview\n\n"
            "A locally-deployed, multi-modal RAG platform. Upload PDFs and images → auto-parse → "
            "vector index → semantic Q&A, all running on your own machine.\n\n"
            "## Stack\n\n"
            "- **Backend:** Python / FastAPI, async SQLAlchemy + Alembic, ChromaDB, Sentence Transformers, "
            "MinerU (document parsing), RAGAnything (multi-modal RAG)\n"
            "- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, Zustand, shadcn/ui\n"
            "- **Models:** Ollama (local LLM / Vision)\n"
            "- **Infra:** Docker Compose, NVIDIA GPU acceleration\n\n"
            "JWT auth, multi-session chat, fully offline — data never leaves the box.\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "本地部署的多模態 RAG 平台。上傳 PDF 與圖片 → 自動解析 → 向量索引 → 語意問答，全程於本機運行。\n\n"
            "## 技術棧\n\n"
            "- **後端：** Python / FastAPI、async SQLAlchemy + Alembic、ChromaDB、Sentence Transformers、"
            "MinerU（文件解析）、RAGAnything（多模態 RAG）\n"
            "- **前端：** Next.js 16、React 19、TypeScript、Tailwind CSS v4、Zustand、shadcn/ui\n"
            "- **模型：** Ollama（本地 LLM / Vision）\n"
            "- **基礎設施：** Docker Compose、NVIDIA GPU 加速\n\n"
            "支援 JWT 身分驗證、多 Session 對話，完全離線——資料不外傳。\n"
        ),
        "tech": ["FastAPI", "ChromaDB", "MinerU", "RAGAnything", "Next.js 16", "Ollama", "Docker"],
        "links": {"github": "https://github.com/Tsai1030/Multi-modal-AI-Knowledge-Base-Platform"},
        "period": "2026–",
        "role_en": "Full-stack",
        "role_zh": "全端開發",
        "featured": True,
        "sort": 2,
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
        "period": "2024–2025",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": True,
        "sort": 3,
    },
    {
        "slug": "rag-medical-react-agent",
        "title_en": "RAG Medical Q&A (ReAct)",
        "title_zh": "RAG 醫療問答（ReAct）",
        "summary_en": "A ReAct agent that chooses between a local doctor database and live web search per question.",
        "summary_zh": "ReAct 代理可依問題自動選擇本地醫師資料庫或即時網路搜尋。",
        "body_en": (
            "## Overview\n\n"
            "A medical Q&A platform combining RAG with a **ReAct agent**, focused on doctors' specialties, "
            "credentials, and medical news.\n\n"
            "## Implementation\n\n"
            "- **Agent:** LangChain ReAct that picks tools per question — local doctor DB vs. live web "
            "search (Google Serper API)\n"
            "- **Embeddings:** BAAI/bge-m3 into ChromaDB with specialty metadata\n"
            "- **LLM:** OpenAI GPT-4o for reasoning, tool selection, and answer generation\n"
            "- **API:** FastAPI REST with CORS; React + Vite chat frontend (Markdown rendering)\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "結合 RAG 與 **ReAct Agent** 的醫療問答平台，聚焦醫師專長、學經歷與醫療新知。\n\n"
            "## 技術實作\n\n"
            "- **代理：** LangChain ReAct，依問題自動選工具——本地醫師資料庫 vs. 即時網路搜尋（Google Serper API）\n"
            "- **嵌入：** BAAI/bge-m3 存入 ChromaDB，附專長分類 metadata\n"
            "- **LLM：** OpenAI GPT-4o 負責推理、工具選擇與答案生成\n"
            "- **API：** FastAPI REST（支援 CORS）；React + Vite 聊天前端（Markdown 渲染）\n"
        ),
        "tech": ["ReAct Agent", "GPT-4o", "Google Serper", "LangChain", "FastAPI", "ChromaDB"],
        "links": {"github": "https://github.com/Tsai1030/Langchain-ReAct-Agent"},
        "period": "2024–",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": True,
        "sort": 4,
    },
    {
        "slug": "crewai-ziwei",
        "title_en": "CrewAI Multi-Agent — Zi Wei Analysis",
        "title_zh": "CrewAI 多代理 — 紫微斗數分析",
        "summary_en": "A multi-agent Zi-Wei analysis system built on CrewAI with a RAG knowledge base.",
        "summary_zh": "以 CrewAI 打造的多代理紫微斗數智能分析系統，結合 RAG 知識庫。",
        "body_en": (
            "## Overview\n\n"
            "An experiment in collaborative multi-agent reasoning: CrewAI agents coordinate to analyse "
            "Zi-Wei charts, grounded by a RAG knowledge base.\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "多代理協作推理的實驗：以 CrewAI 多個代理協同分析紫微命盤，並以 RAG 知識庫為依據。\n"
        ),
        "tech": ["CrewAI", "Multi-Agent", "RAG", "Python"],
        "links": {"github": "https://github.com/Tsai1030/CrewAI-Multi-Agent"},
        "period": "2025",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": False,
        "sort": 5,
    },
    {
        "slug": "unsloth-lora-finetuning",
        "title_en": "unsloth — LoRA Fine-tuning",
        "title_zh": "unsloth — LoRA 微調",
        "summary_en": "Efficient LoRA / PEFT fine-tuning experiments for domain-specific LLM behaviour.",
        "summary_zh": "以 unsloth 進行高效 LoRA / PEFT 微調，調整 LLM 在特定領域的行為。",
        "body_en": (
            "## Overview\n\n"
            "Hands-on LoRA / PEFT fine-tuning with **unsloth** for fast, memory-efficient training, "
            "evaluating how different methods change domain behaviour.\n"
        ),
        "body_zh": (
            "## 專案概述\n\n"
            "使用 **unsloth** 進行 LoRA / PEFT 微調，追求快速且省記憶體的訓練，並評估不同方法對領域行為的影響。\n"
        ),
        "tech": ["unsloth", "LoRA", "PEFT", "PyTorch", "Hugging Face"],
        "links": {"github": "https://github.com/Tsai1030/unsloth-Lora-fine-tuning"},
        "period": "2025",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": False,
        "sort": 6,
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
