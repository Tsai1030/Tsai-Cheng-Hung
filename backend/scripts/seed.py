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
            "## At a Glance\n\n"
            "A production system for a construction company that does two things: answers internal-procedure "
            "questions with source-grounded, traceable answers, and turns a previously manual, multi-website "
            "weekly steel-procurement report into a ready-to-download Word document — automatically, in under "
            "three minutes.\n\n"
            "![Construction assistant — system & graph flow](/graph_workflow_new.png)\n\n"
            "## Why I Built This\n\n"
            "The idea came from watching two very different kinds of friction inside the same company.\n\n"
            "New and existing staff regularly need to look up construction procedures, regulations, and the "
            "right form for a given situation — but that knowledge lives scattered across dozens of internal "
            "manuals. Finding the right passage (and trusting it's the *right* one, not an outdated or "
            "similar-sounding one) takes time and institutional memory that new hires simply don't have yet.\n\n"
            "On the procurement side, the pain was more concrete: every week, before a roughly 30-minute "
            "steel-purchasing meeting, someone has to manually visit five-plus external sources — Feng Hsin's "
            "weekly opening prices, international scrap and iron-ore indices, the Xiben mainland-China index, "
            "LME copper, China Steel's monthly/quarterly benchmark prices — copy the numbers down, compute "
            "week-over-week deltas by hand, write up a market narrative, and assemble it all into a Word "
            "meeting record. It's repetitive, easy to get wrong, and it eats real working hours every week "
            "before the meeting even starts.\n\n"
            "Both problems share the same shape underneath: people spending time *finding and assembling* "
            "information rather than *using* it. That's exactly the kind of work an LLM agent — grounded in "
            "the right sources, with deterministic checks where it matters — is good at taking off someone's "
            "plate.\n\n"
            "## System Overview\n\n"
            "The system is a single FastAPI backend and a single Next.js frontend serving two modules behind "
            "one login:\n\n"
            "- **Module A — Knowledge Assistant (RAG):** a LangGraph chat workflow that classifies intent, "
            "retrieves from an internal knowledge base (51 construction documents, ~1,375 chunks), grounds its "
            "answers in retrieved passages with visible sources, and can also find/download static checklists, "
            "fill them out conversationally, or generate brand-new structured forms on the fly\n"
            "- **Module B — Steel Procurement Assistant (SEARCH):** a separate LangGraph pipeline wrapped in a "
            "6-step wizard — pick a meeting date → fetch live market data in the background (~90–180 seconds, "
            "so it never times out an HTTP request) → review fetched values and confidence levels → adjust "
            "China Steel benchmark prices → fill in internal meeting details → download the finished Word "
            "record\n\n"
            "Both modules share the same FastAPI process, the same JWT-based authentication (with a "
            "fine-grained per-user permission flag gating the steel-price module), and the same Next.js "
            "bundle — but they're deliberately kept at arm's length: SEARCH has its own database and an "
            "explicit import boundary, so the two systems can keep evolving without breaking each other.\n\n"
            "In production, everything runs behind PM2, fronted by Caddy, and exposed securely to the company "
            "over a Tailscale Funnel HTTPS endpoint.\n\n"
            "## Technology Choices — and Why\n\n"
            "- **LangGraph for both workflows**, not a simple prompt chain — both the chat assistant and the "
            "report generator need branching (retrieve again? is this a form request?), retries, multi-turn "
            "state, and — for the report generator — the ability to run as a long background job that "
            "survives polling and page reloads\n"
            "- **Hybrid retrieval — ChromaDB vector search + BM25 with a 4,948-term construction-domain jieba "
            "dictionary, fused with Reciprocal Rank Fusion** — pure vector search alone tends to miss "
            "exact-keyword hits that matter a lot in Chinese technical documents (clause numbers, form names, "
            "abbreviations); BM25 catches what embeddings smooth over, and RRF combines the two rankings "
            "without hand-tuning a blend weight\n"
            "- **SQLite to start** — zero ops overhead for a project that needed to ship fast; this later "
            "became one of the bigger lessons of the project (see below), and a migration to PostgreSQL is "
            "now underway\n"
            "- **SSE streaming over FastAPI** — chat needed to feel alive, token-by-token, not \"spinner, then "
            "wall of text\"\n"
            "- **Gemini with Google Search grounding**, replacing a brittle authenticated web scraper for "
            "steel prices — when the scraper's underlying membership lapsed, I redesigned the fetch layer "
            "around an LLM that searches the live web and returns *structured* data, so the rest of the "
            "pipeline (price history, derived grades, Word rendering) didn't need to change at all\n"
            "- **python-docx** for final output — the procurement team already works in a specific Word "
            "template; generating directly into that template means zero behavior change for them, just less "
            "manual work\n"
            "- **Next.js + shadcn/ui + Zustand/React Query** — fast iteration, and a wizard-style UI that "
            "matches how the team already thinks about the weekly task: step by step, with a chance to review "
            "and correct each stage\n\n"
            "## Inside the System: Two Things I'm Proud Of\n\n"
            "**1. A self-correcting retrieval loop (CRAG).** Retrieval doesn't always return good context on "
            "the first try — especially with vague or multi-part questions. So after retrieving and merging "
            "results, a \"grader\" model judges whether the retrieved context actually suffices. If not, a "
            "\"query rewriter\" reformulates the question and the system tries again — capped at two retries, "
            "so a hard question degrades gracefully into \"best effort with a clear answer\" instead of "
            "spinning forever. That loop is the difference between *technically retrieved something* and "
            "*actually answered the question*.\n\n"
            "**2. Keeping the LLM out of the arithmetic.** The steel-price pipeline pulls numbers from several "
            "sources, computes week-over-week deltas, derives related grades (e.g. SD420W = SD280 + 1,000), "
            "converts currencies, and writes a narrative paragraph around all of it. It's tempting to just ask "
            "an LLM to \"write up this week's report\" — but LLMs are unreliable at exact arithmetic and prone "
            "to mixing up absolute values with deltas. So the system splits the work on purpose: the LLM "
            "handles search, structured extraction, and prose; every number that *must* be exactly right is "
            "computed in plain Python from validated inputs. Anything missing or unpublished is explicitly "
            "marked low-confidence (shown in red in the final Word document for human review), and "
            "\"borrowed\" stale values are displayed but never silently written into the historical price "
            "table — so the system never quietly corrupts its own ground truth.\n\n"
            "## Challenges Along the Way\n\n"
            "A few of the harder problems, and what they taught me:\n\n"
            "- **An Alembic migration nearly destroyed production data.** Adding one column to the `users` "
            "table with `batch_alter_table` (SQLite's way of altering tables: create a new table, copy rows, "
            "drop the old one, rename) silently triggered `ON DELETE CASCADE` across the whole chain — wiping "
            "52 conversations and 321 messages. The fix itself was simple (`op.add_column` instead of "
            "`batch_alter_table`), but the real lesson was process: any migration touching `users`/"
            "`conversations` is now treated as high-risk, with a mandatory timestamped backup and a dry-run in "
            "an isolated worktree first. This incident is also the single biggest reason I'm now migrating "
            "from SQLite to PostgreSQL.\n"
            "- **A \"ghost schema\" bug from leftover SQLite WAL files.** Restoring a database backup without "
            "also removing its `-wal`/`-shm` sidecar files left new connections seeing a stale schema — "
            "`alembic` and the `sqlite3` CLI both reported the new column existed, while the app's async ORM "
            "insisted \"no such column.\" It looked like a code bug; it was actually a filesystem one, and it "
            "took a while to track down precisely because of that mismatch (fix: delete the sidecar files "
            "after every restore).\n"
            "- **Streaming that would randomly \"freeze and dump.\"** Chat responses occasionally stopped "
            "streaming token-by-token and appeared all at once after a delay — the classic symptom of "
            "something in the network path buffering the stream. The actual cause: Tailscale's routing config "
            "is *globally overwritten*, not appended to — any single command without the right flag could "
            "silently drop the `/api` path rule. I wrote a one-shot reset script and a short troubleshooting "
            "SOP, turning this from a confused half-hour into a two-minute fix.\n"
            "- **A security tool that didn't trust my own deployment tools.** The company's endpoint-"
            "protection software refused to trust Python processes spawned by PM2 or batch scripts, so the "
            "backend had to be started from an interactive terminal instead of being managed automatically — "
            "an annoying constraint I had to design the deployment process around rather than fight.\n"
            "- **An external data source quietly went dark.** The site the steel-price scraper depended on "
            "required a paid membership that lapsed, breaking one of the system's core data feeds without "
            "warning. Rather than patch the scraper, I treated it as a chance to replace the whole approach — "
            "moving from \"log in and parse HTML\" to \"ask an LLM with live web search for the same "
            "structured data,\" which is both more resilient to site redesigns and easier to extend to new "
            "sources later.\n\n"
            "## Results & Impact\n\n"
            "- **A previously manual, multi-site research-and-writing task now runs as an automated background "
            "pipeline that completes in roughly 90–180 seconds**, leaving the team to review, adjust, and "
            "download rather than research and assemble from scratch.\n"
            "- **Performance work grounded in real usage, not guesswork.** I optimized the hot paths directly "
            "— an LRU cache for embeddings (skipping repeat OpenAI calls on repeated queries), running vector "
            "and keyword search in parallel instead of sequentially, and moving the retrieval grader — one of "
            "the most frequently-called nodes — onto a smaller, cheaper model. To check whether that focus was "
            "right, I later built a token-cost analyzer over production LangSmith traces (~480K tokens across "
            "sampled threads): it confirmed that the responder and retrieval grader together account for the "
            "largest share of token spend — validating those earlier choices and pointing clearly at where the "
            "next round of optimization should go.\n"
            "- **Answers come with sources, not just text** — every retrieved passage keeps its origin "
            "document, section, heading hierarchy, and even image references, so staff can verify an answer "
            "instead of just trusting it. That traceability matters more in a regulated, safety-conscious "
            "industry than a slick-sounding paragraph does.\n"
            "- **The system is in active internal use**, served securely over HTTPS with role- and "
            "feature-level permissions — for example, the steel-price module stays opt-in even for admins.\n\n"
            "## Reflections & What's Next\n\n"
            "Building two related-but-independent modules inside one shared process taught me more about "
            "*boundaries* than about RAG or LangGraph specifically — explicit import rules, separate "
            "databases, and \"no cross-imports except through one mount point\" turned what could have been a "
            "tangled merge into something I could reason about and roll back safely.\n\n"
            "The SQLite incident was a hard lesson, but a useful one: a database choice that's perfect for "
            "\"ship something that works\" can become the wrong choice the moment you have real concurrent "
            "users and real schema migrations. **Migrating to PostgreSQL** is the most concrete next step — "
            "it removes an entire category of Windows/SQLite-specific failure modes I've now hit more than "
            "once.\n\n"
            "I'm also mid-rollout on **adding image input to the knowledge assistant** — a vision-capable "
            "model in the loop, so staff can upload a site photo, a scanned form, or a diagram and ask "
            "questions grounded in *that* image, with multi-turn continuity so follow-up questions still know "
            "which image you meant. The harder design questions (when to re-analyze an image vs. reuse the "
            "last analysis, how to keep it fast) are largely settled; what's left is mostly UX polish.\n\n"
            "Longer-term, I want to keep extending the steel-price source adapters as external sites "
            "inevitably change shape again — and keep applying the idea this project has now validated twice: "
            "don't make people assemble information by hand when an agent, grounded in the right sources and "
            "backed by deterministic checks where correctness matters, can do it for them.\n"
        ),
        "body_zh": (
            "## 一句話介紹\n\n"
            "這是一套服務於營造公司內部員工的正式上線系統：一邊是能附上可追溯來源、回答內部規範問題的知識助理，"
            "另一邊是把過去得手動跑五、六個網站才能完成的鋼筋採購週會記錄，自動產出成可直接下載的 Word 文件 —— "
            "整個過程約一到三分鐘。\n\n"
            "![營建知識助理 — 系統與 graph 流程](/graph_workflow_new.png)\n\n"
            "## 動機與背景\n\n"
            "這個專案的起點，其實是公司裡兩種看似不相關、但本質一樣的「卡關」。\n\n"
            "第一種是同仁查資料的痛點：施工程序、管理規範、各種檢核表格分散在數十份內部文件裡，要找到「對的那一段」、"
            "並且確定它不是舊版或相似但不適用的版本，往往得靠經驗與摸索，新人尤其辛苦。\n\n"
            "第二種是採購端更具體的痛點：每週鋼筋採購會議（約半小時）開始前，承辦人得手動跑過五個以上的外部資料來源 —— "
            "豐興每週開盤、國際廢鋼與鐵礦砂指數、西本新幹線（大陸鋼材指數）、LME 銅價、中鋼月盤／季盤 —— "
            "把數字一一抄下來、手算週對週的漲跌、寫市場分析段落，最後拼成一份 Word 會議記錄。這件事重複性高、"
            "容易抄錯算錯，而且每週都要花掉真實的工時，會議都還沒開始就先耗掉了。\n\n"
            "這兩個問題拆開來看是兩件事，但本質相同：人花在「找資料、拼資料」上的時間，遠多於「使用資料」本身。"
            "而這正是 LLM agent 最適合接手的工作型態 —— 前提是它的輸出要有來源可查，且在「正確性」真正重要的地方"
            "要有確定性的檢查機制兜底。\n\n"
            "## 系統概觀\n\n"
            "整個系統是一個 FastAPI 後端搭配一個 Next.js 前端，共用一次登入、服務兩個模組：\n\n"
            "- **模組 A — 知識助理（RAG）**：以 LangGraph 串接的對話流程，先判斷使用者意圖，再從內部知識庫"
            "（51 份營造文件、約 1,375 個切片）檢索並附上來源回答問題；也能依需求找出、下載、用對話方式逐步代填"
            "既有檢核表，或對沒有對應範本的需求即時生成全新的結構化表格\n"
            "- **模組 B — 鋼筋採購週會助理（SEARCH）**：另一條獨立的 LangGraph pipeline，包成 6 步驟精靈 —— "
            "選定會議日期 → 背景抓取本週行情（約 90–180 秒，採非同步背景任務避免 HTTP 逾時）→ 預覽抓到的數值與"
            "信心級別 → 視需要調整中鋼盤價 → 補上內部會議資訊 → 下載完成的 Word 記錄\n\n"
            "兩個模組共用同一個 FastAPI 進程、同一份前端 bundle 與同一套登入機制（JWT，並以細緻的使用者權限旗標"
            "控制誰能使用鋼筋助理），但刻意維持「井水不犯河水」：SEARCH 模組有自己的資料庫，並透過明確的 import "
            "邊界規則，讓兩邊可以各自演進、互不波及。\n\n"
            "正式環境用 PM2 常駐執行、Caddy 做反向代理，再透過 Tailscale Funnel 以 HTTPS 安全對內開放給全公司"
            "同仁使用。\n\n"
            "## 技術選型與理由\n\n"
            "- **兩條工作流都選 LangGraph，而非單純的 prompt chain** —— 不論是知識助理或週會產生器，都需要分支"
            "判斷（要不要重新檢索？是不是表單需求？）、重試機制、跨輪次的狀態保存，以及（對週會產生器來說特別"
            "重要）能在背景長時間執行、跨輪詢與頁面刷新仍保持狀態的能力\n"
            "- **Hybrid 檢索 —— ChromaDB 向量搜尋 + 自建 4,948 詞營造業詞典的 jieba/BM25 關鍵字搜尋，"
            "再用 Reciprocal Rank Fusion 融合排序** —— 純向量搜尋常常漏掉中文技術文件裡很關鍵的精確關鍵字"
            "（特定條文編號、表單名稱、縮寫）；BM25 補上向量會「模糊掉」的精確匹配，RRF 則讓兩種排序結果自然"
            "融合，不需要手動調整混合權重\n"
            "- **一開始選 SQLite** —— 零維運成本，對需要快速上線的專案是合理選擇；但這後來也成為我學到最多的"
            "一課（詳見下文），目前已著手規劃遷移到 PostgreSQL\n"
            "- **FastAPI + SSE 串流** —— 對話需要的是「逐字浮現」的真實感，而不是「轉圈圈 → 整段彈出」\n"
            "- **改用 Gemini + Google Search grounding 取代原本的會員制爬蟲** —— 當原本鋼價資料來源網站的"
            "會員資格失效後，我把抓取層整個重新設計成「讓 LLM 直接搜尋網路、回傳結構化資料」，下游（價格歷史、"
            "級距推算、Word 渲染）完全不必更動\n"
            "- **python-docx 直接輸出** —— 採購團隊原本就用特定的 Word 範本作業，直接產進同一份範本，"
            "對他們來說是「少做一件事」，而不是「換一套新流程」\n"
            "- **Next.js + shadcn/ui + Zustand/React Query** —— 前端能快速迭代，並且用「精靈式」介面貼合"
            "團隊原本一步步檢查資料的習慣，每一步都能預覽、修正\n\n"
            "## 核心功能亮點\n\n"
            "**1. 會自我修正的檢索迴圈（CRAG）。** 第一次檢索不見得能拿到足夠的內容，尤其是模糊或多重子問題的"
            "情況。所以系統在檢索並合併結果後，會用一個「grader」模型判斷檢索到的內容是否真的足以回答問題；"
            "不夠的話，再用「query rewriter」改寫問題重新檢索 —— 上限兩次重試，確保困難問題能優雅地降級成"
            "「盡力作答並如實告知」，而不是無限迴圈空轉。這個迴圈，正是「技術上有檢索到東西」跟「真正回答了"
            "問題」之間的關鍵差異。\n\n"
            "**2. 把「算數」這件事從 LLM 手中拿走。** 鋼價 pipeline 要從多個來源抓數字、算週對週漲跌、推算"
            "相關級距（例如 SD420W = SD280 + 1,000）、做幣別換算，再寫成市場分析段落。直接叫 LLM「把這週的"
            "報告寫一寫」看似省事，但 LLM 對精確算術並不可靠，常把絕對值跟漲跌幅搞混。所以系統刻意把工作拆開："
            "LLM 負責搜尋、結構化抽取與文字段落；任何「必須完全正確」的數字，一律由 Python 依驗證過的輸入做"
            "確定性運算。抓不到或還沒公布的數值會被明確標記為低信心（在最終 Word 文件裡用紅字標出，提醒人工"
            "複核），而「沿用上週」的舊值只會顯示、絕不會悄悄寫進歷史價格表 —— 確保系統不會在不知不覺間"
            "污染自己的真相來源。\n\n"
            "## 遇到的問題與解決方法\n\n"
            "開發過程中幾個比較硬的關卡，以及從中學到的事：\n\n"
            "- **一次 migration 差點毀了正式資料。** 為 `users` 表加一個欄位時用了 `batch_alter_table`"
            "（SQLite 改表的方式：建新表、複製資料、刪舊表、改名），結果意外觸發整條 `ON DELETE CASCADE`，"
            "砍掉了 52 筆對話與 321 則訊息。修法本身不難（改用 `op.add_column`），但真正的教訓是流程：我現在"
            "把任何牽動 `users`／`conversations` 的 migration 都當成高風險操作，強制先做帶時間戳的備份、"
            "並先在隔離的 worktree 跑過一輪。這次事故，也是後來決定把 SQLite 換成 PostgreSQL 最直接的原因。\n"
            "- **WAL 殘留檔造成的「schema 視角錯亂」。** 從備份還原資料庫後，沒有同時刪掉 `-wal`／`-shm` "
            "暫存檔，導致新連線看到的是舊 schema —— `alembic` 和 `sqlite3` 指令都說新欄位存在，但應用程式的 "
            "async ORM 卻堅持「沒有這個欄位」。症狀看起來像程式碼的 bug，實際上是檔案系統層級的問題，"
            "花了不少時間才精確定位（修法：每次還原備份後手動刪除這兩個暫存檔）。\n"
            "- **會無預警「卡住、再整段蹦出」的串流。** 偶爾聊天回應會從逐字浮現變成停頓後整段彈出 —— "
            "典型的「中間某一層被 buffer 住了」症狀。真正原因是 Tailscale 的路由設定是「整體覆寫」而非"
            "「附加」：任何一條沒帶對旗標的指令，都可能悄悄把 `/api` 那條路由規則洗掉。我寫了一支一鍵重置"
            "腳本與排查 SOP，讓這個問題從「困惑半小時」變成「兩分鐘修好」。\n"
            "- **連自己的部署工具都不被信任的資安軟體。** 公司的端點防護軟體不信任由 PM2 或批次檔啟動的 "
            "Python 子行程（即使它們做的事完全正常），導致後端必須從互動式終端機手動啟動，而不能交給自動化"
            "管理 —— 一個有點麻煩、但只能順著去設計部署流程，而不是硬碰硬解決的限制。\n"
            "- **外部資料來源無預警斷線。** 鋼價爬蟲依賴的網站需要付費會員，資格到期後直接斷了系統最核心的"
            "資料來源之一，毫無預警。與其修補爬蟲本身，我把它當成重新設計的機會 —— 從「登入、解析 HTML」"
            "整個換成「讓 LLM 帶著即時網路搜尋去拿同樣結構化的資料」，不只更耐網站改版，未來要擴充新來源"
            "也更容易。\n\n"
            "## 成果與效益\n\n"
            "- **過去得手動跑多個網站、寫成報告的週會記錄，現在變成一條自動背景管線，約 90–180 秒就能跑完**，"
            "團隊只需要檢視、調整、下載，不用再從零研究、手動拼湊。\n"
            "- **效能優化建立在真實使用數據上，而非憑空猜測。** 我直接針對熱路徑下手：替 embedding 加上 "
            "LRU 快取（重複查詢直接跳過 OpenAI 呼叫）、把向量與關鍵字搜尋從循序改成平行執行、並把呼叫頻率"
            "最高的節點之一 —— retrieval grader —— 換成更小更便宜的模型。為了驗證這些調整的方向是否正確，"
            "我後來又寫了一支工具，分析正式環境裡 LangSmith 留下的真實對話軌跡（抽樣對話累積約 48 萬 token）"
            "—— 結果證實 responder 與 retrieval grader 兩個節點合計就佔了最大宗的 token 花費，這既驗證了"
            "先前的調整方向沒錯，也清楚指出了下一輪優化該往哪裡走。\n"
            "- **回答附上可查證的來源，而不只是一段文字** —— 每個檢索到的段落都保留了來源文件、章節、標題"
            "層級，甚至圖片引用，讓同仁可以驗證答案、而不是單純相信它。在一個重視規範與安全的產業裡，這種"
            "「可追溯性」比一段寫得漂亮的文字更有價值。\n"
            "- **系統已正式上線供內部使用**，透過 HTTPS 安全對內開放，並有角色與功能層級的權限控管 —— "
            "例如鋼筋助理模組即使是管理員也預設關閉，要主動開啟才能用。\n\n"
            "## 反思與未來規劃\n\n"
            "在同一個進程裡開發兩個「相關但獨立」的模組，教會我的東西，其實比 RAG 或 LangGraph 本身還多 —— "
            "明確的 import 規則、各自獨立的資料庫、以及「除了一個掛載點外禁止互相引用」，把原本可能糾結成"
            "一團的整合工作，變成一件我能推理、也能安全回滾的事。\n\n"
            "SQLite 那次事故是個硬教訓，但也很有用：一個對「先做出能動的東西」來說很完美的資料庫選擇，"
            "一旦遇上真實的並發使用者與真實的 schema migration，隨時可能變成錯誤的選擇。**遷移到 "
            "PostgreSQL** 是目前最具體的下一步 —— 它能一次解掉我已經踩過不只一次的整類 Windows / SQLite "
            "特有問題。\n\n"
            "我目前也正在替知識助理**加入圖片輸入能力**（接入具備視覺理解的模型，讓同仁可以上傳工地照片、"
            "表單掃描檔或圖面，針對「這張圖」提問，並支援多輪對話下的圖片延續性，讓追問時系統仍知道你指的"
            "是哪張圖）。這項功能目前正在分階段上線中 —— 比較難的設計問題（什麼時候該重新分析圖片、什麼時候"
            "該沿用上一輪的分析結果、如何兼顧速度）大致都已拍板，剩下主要是體驗上的打磨。\n\n"
            "更長期來看，我想持續擴充鋼價來源的 adapter（畢竟外部網站遲早又會改版），並繼續落實這個專案"
            "驗證了兩次的核心想法：當一個 agent 能夠依靠正確的來源、並在「正確性」真正重要的地方有確定性的"
            "檢查機制兜底時，就不該再讓人花時間手動拼湊資訊。\n"
        ),
        "tech": [
            "LangGraph", "FastAPI", "Hybrid RAG", "ChromaDB", "BM25", "RRF",
            "Gemini Grounded Search", "OpenAI Embeddings", "SQLAlchemy", "python-docx", "Next.js", "TypeScript",
        ],
        "links": {"github": "https://github.com/Tsai1030/LangGraph_RAG_SYSTEM", "demo": "https://kccc3798.tail138ec9.ts.net/"},
        "cover_image": "/Construction%20Knowledge%20RAG.png",
        "video_url": "https://youtu.be/D-g3UW2yE40",
        "period": "2025–",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": True,
        "sort": 1,
    },

    {
        "slug": "eastern-mysticism",
        "cover_image": "/Eastern%20Mysticism%20Platform%20COVERIMG.png",
        "title_en": "Eastern Mysticism Platform",
        "title_zh": "東方命理平台",
        "summary_en": "Multi-agent consultation platform with SSE streaming and a custom Zi-Wei chart engine.",
        "summary_zh": "多 Agent 命理諮詢平台，支援 SSE 串流與自製紫微斗數排盤引擎。",
        "body_en": (
            "## At a Glance\n\n"
            "A production multi-agent platform for Eastern mysticism consultations (Zi Wei Dou Shu, "
            "I Ching, name analysis), built and shipped during a two-month internship. Instead of the "
            "usual fortune-telling site that spits out a wall of hard-to-read jargon, this platform pairs "
            "a custom chart engine with an LLM that talks the result through — so users actually understand "
            "what their chart means. I owned the backend agent design and led the frontend.\n\n"
            "![Eastern Mysticism Platform](/Eastern%20Mysticism%20Platform.png)\n\n"
            "## Why I Built This\n\n"
            "Most fortune-telling sites online stop at something pretty bare-bones: a plain interface, "
            "little interactivity, and — worst of all — output that's just a dense block of terminology. "
            "Users read the result and still have no idea what it means *for them*. I wanted to build "
            "something different: a Web experience that's genuinely interactive, and where the computed "
            "chart isn't just dumped on the user but made understandable through conversation. The goal "
            "was for the reading itself to actually land — to be something the user could engage with and "
            "act on, not just stare at.\n\n"
            "## How It Works\n\n"
            "The core idea is a **personal chart that belongs to each account**. When a user registers, "
            "they fill in their personal details and the system immediately computes their Zi-Wei chart "
            "and stores it in their profile. From then on, every conversation with the LLM is grounded in "
            "*that specific user's chart* — the model doesn't give generic, one-size-fits-all answers, it "
            "reasons from the individual's own result. The remaining feature modules are each designed "
            "around their own functional characteristics.\n\n"
            "## Technology Choices\n\n"
            "- Multi-layer AI agents built on **LangChain / LangGraph**, using function calling to connect "
            "the chart data with the conversation flow\n"
            "- **SSE streaming** responses, so users see the answer appear token-by-token instead of "
            "waiting on a blank screen\n"
            "- A self-built Zi-Wei chart engine (`ziwei_calculator.py`) doing real astronomical computation "
            "via `pyswisseph`, rather than relying on a black-box third-party API\n"
            "- Async micro-services with **Quart + Redis Queue**, and **PostgreSQL + Pinecone** hybrid "
            "storage for structured profile data and vector retrieval respectively\n"
            "- **Next.js 15 / React 19** frontend with Three.js / GSAP for an immersive feel, and "
            "multi-language support via next-intl\n\n"
            "## Challenges Along the Way\n\n"
            "**Validating an open-ended model's output.** The hardest problem was that an LLM's response "
            "is open-ended, and it didn't always conform to the fixed data format the frontend expected. "
            "At first I left the final format-handling to the frontend's TypeScript — but whenever the "
            "model's output drifted even slightly from the expected shape, the frontend would error out "
            "directly. The lesson stuck: **the format has to be defined and validated on the backend "
            "before it's returned**, not patched up on the frontend. Once the backend tightened the "
            "structure, the frontend could render reliably.\n\n"
            "**First time implementing SSE streaming.** So that users weren't just staring at a spinner "
            "while the LLM thought, I implemented SSE streaming for the first time — letting responses "
            "surface token-by-token. It's a small thing technically, but it changes the waiting "
            "experience completely.\n\n"
            "## Reflections & What I Learned\n\n"
            "The biggest growth from this internship wasn't any single piece of technology — it was "
            "learning how to *break problems down*. Every issue I hit, I had to decompose it, locate the "
            "real root cause, and either find a fix or bounce ideas off other engineers to get there. "
            "Shipping a product from zero to live in two months came down to running that loop over and "
            "over: hit a problem, take it apart, solve it. That problem-solving cycle is the most valuable "
            "thing I took away from the experience.\n"
        ),
        "body_zh": (
            "## 一句話介紹\n\n"
            "這是我在兩個月實習期間，從零開發並成功上線的一套產品級東方命理諮詢平台（紫微斗數、易經、姓名學）。"
            "有別於一般算命網站只丟出一堆難懂的術語，這個平台把自製排盤引擎與 LLM 結合 —— 讓 LLM 把命盤結果"
            "「講清楚」，使用者才能真正理解自己的命盤代表什麼。我負責後端 Agent 設計並主導前端。\n\n"
            "![東方命理平台](/Eastern%20Mysticism%20Platform.png)\n\n"
            "## 動機與背景\n\n"
            "目前網路上類似的算命網頁，大多停在很陽春的階段：介面簡單、缺乏互動，最關鍵的是，分析結果往往只是"
            "一大段難以理解的術語文字 —— 使用者讀完，還是不知道「這對我到底代表什麼」。我想做的不一樣：一個"
            "互動體驗豐富的 Web 介面，而且推算出來的命盤結果不只是丟給使用者，而是能透過對話被理解。我希望這份"
            "解析能真正「打中」使用者 —— 是一個他們能參與、能應用的結果，而不只是看著一堆字。\n\n"
            "## 系統設計\n\n"
            "平台的核心是「**每個帳號都有專屬命盤**」的概念。使用者註冊時填入個人資料，系統當下就完成命盤推算，"
            "並把結果存進該使用者的 profile。之後每一次與 LLM 對話，模型都是以「屬於這個人的命盤結果」為依據來"
            "回答 —— 不是泛泛而談的套版回應，而是從個人自己的命盤推理出來的個人化解析。其餘功能模組則依各自的"
            "功能特性分開設計。\n\n"
            "## 技術選型\n\n"
            "- 以 **LangChain / LangGraph** 建構多層次 AI Agent，透過 function calling 串接命盤資料與對話流程\n"
            "- **SSE 串流**回應，讓使用者看著答案逐字浮現，而不是對著空白畫面空等\n"
            "- 自主開發的紫微斗數排盤引擎（`ziwei_calculator.py`），以 `pyswisseph` 進行真正的天文運算，"
            "而非依賴黑盒的第三方 API\n"
            "- 非同步微服務：**Quart + Redis Queue**，並以 **PostgreSQL + Pinecone** 混合儲存，分別處理"
            "結構化的 profile 資料與向量檢索\n"
            "- **Next.js 15 / React 19** 前端，搭配 Three.js / GSAP 營造沉浸感，並以 next-intl 支援多語系\n\n"
            "## 實作中的挑戰\n\n"
            "**驗證開放式模型的輸出格式。** 最棘手的問題是 LLM 的回應是開放式的，面對前端要求的固定資料格式時"
            "並不總是穩定。一開始我把格式的最後處理丟給前端的 TypeScript 去接，結果只要模型回傳的格式稍有偏差，"
            "前端就直接報錯。這件事讓我學到一個重要原則：**格式應該在後端就定義好、驗證好再回傳**，而不是寄望"
            "前端去兜底。後端先把結構收斂乾淨，前端才能穩定渲染。\n\n"
            "**第一次實作 SSE 串流。** 為了讓使用者在等待 LLM 回覆時不是空等，我第一次實作了 SSE 串流，讓回應"
            "逐字浮現。技術上是件小事，卻徹底改變了「等待中」的使用體驗。\n\n"
            "## 反思與收穫\n\n"
            "這次實習最大的成長，其實不在某個特定技術，而在學會「**拆解問題**」這件事。開發過程遇到的每一個"
            "問題，我都得先把它拆開、定位真正的根因，再找解法，或是跟其他工程師討論、腦力激盪一起找方向。能在"
            "兩個月內把一個產品從零做到上線，靠的就是這種「遇到問題 → 拆解 → 解決」的循環不斷重複 —— 這是我"
            "這次實習學到最有價值的東西。\n"
        ),
        "tech": ["LangGraph", "GPT-4o", "Quart", "Redis", "PostgreSQL", "Pinecone", "Next.js 15", "Three.js"],
        "links": {"demo": "https://qiankun.ask-lens.ai/tw"},
        "video_url": "https://youtu.be/5RqoQpOjDKY",
        "period": "2025–",
        "role_en": "Full-stack (lead frontend)",
        "role_zh": "全端（前端主導）",
        "featured": True,
        "sort": 2,
    },
    {
        "slug": "multimodal-rag-knowledge-base",
        "cover_image": "/Multi-modal%20RAG%20Knowledge%20Base%20Platform.png",
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
        "cover_image": "/Ziwei%20Doushu%20Multi-Agent%20AI%20%28LangGraph%20ReAct%29.png",
        "title_en": "Ziwei Doushu AI Platform — From a Take-Home Test to a Full Multi-Agent Product",
        "title_zh": "紫微斗數 AI 命理平台：從面試考題到完整 Multi-Agent 產品",
        "summary_en": "An account-based AI fortune-telling platform pairing a deterministic Ziwei Doushu chart engine (iztro) with a genuine parallel multi-agent LangGraph pipeline, RAG knowledge base, and a full subscription/token system — deployed on Docker + Render.",
        "summary_zh": "一套帳號制的紫微斗數 AI 命理平台，結合精準命盤引擎（iztro）、LangGraph 並行多智能體、RAG 知識庫與完整訂閱代幣系統，並以 Docker + Render 部署上線。",
        "body_en": (
            "## TL;DR\n\n"
            "An AI platform that turns a Ziwei Doushu (Chinese astrology) reading into something you can actually "
            "trust and inspect: the chart is computed by a real astrology engine — never guessed by an LLM — and "
            "the analysis is produced by **three independently-personaed AI agents working in parallel**, then "
            "merged by a fourth. Around that core sits a full product shell: accounts, saved charts, a streaming "
            "chat with a fortune-teller persona, and a subscription system with usage-based tokens.\n\n"
            "## Why I Built This\n\n"
            "This project began as a take-home test before an internship — a simple linear pipeline where an "
            "LLM both \"drew\" and interpreted a chart. Two things bothered me about that approach. First, "
            "**LLMs hallucinate charts**: ask the same birth data twice and you can get two different star "
            "placements, which is a non-starter for anything claiming to be an analysis tool. Second, most "
            "\"multi-agent\" demos I'd seen were really just one model switching personas in a loop — convincing "
            "in a demo, but not an actual multi-agent system. I kept rebuilding this project, partly to fix both "
            "problems properly, and partly to push it from a weekend script into something with the shape of a "
            "real product: accounts, persistence, billing logic, and deployment.\n\n"
            "## System at a Glance\n\n"
            "![Ziwei Doushu Multi-Agent AI](/full%20multi%20agent.png)\n\n"
            "1. The **frontend** computes the chart with the official `iztro` engine directly in the browser — "
            "the same JSON is used to render the chart board *and* sent to the backend, so what the user sees and "
            "what the AI reasons over are guaranteed to match.\n"
            "2. The chart is POSTed to a **FastAPI** backend, where a **LangGraph** graph runs: a `researcher` "
            "node retrieves shared context from a **ChromaDB** RAG knowledge base, then **fans out** to three "
            "parallel Gemini agents — a reasoning analyst, a domain expert, and a creative interpreter — and "
            "**fans back in** to a `coordinator` that synthesizes the final report.\n"
            "3. Around that core sits an account layer (PostgreSQL + JWT + Google OAuth), a sidebar app shell "
            "(saved charts, career/love fortune tools, a real-time streaming chat with the persona \"玄機子\"), "
            "and a subscription system that meters usage with \"star tokens.\"\n\n"
            "## Why These Technology Choices\n\n"
            "- **iztro over LLM-generated charts** — moving chart computation to a deterministic, open-source "
            "engine eliminates hallucination at the source; the LLM's job is reduced to *interpretation*, which "
            "is what it's actually good at.\n"
            "- **LangGraph over a simple prompt chain** — I needed explicit control over branching, parallel "
            "execution, and shared state, plus first-class tracing (LangSmith) to *prove* the agents run "
            "independently rather than just claiming they do.\n"
            "- **Single-vendor Gemini (LLM + embeddings)** — the original version mixed Claude, OpenAI, and "
            "Tavily; consolidating onto one provider with one API key cut both cost and operational surface "
            "area without sacrificing quality.\n"
            "- **ChromaDB** — a lightweight, file-backed vector store that indexes the knowledge base "
            "idempotently on startup; no separate service to operate for a project this size.\n"
            "- **PostgreSQL + SQLAlchemy + Alembic** — once the project grew from a stateless analysis tool into "
            "an account-based product, I needed real relations (users → chart profiles → chat sessions → "
            "messages) and reproducible schema migrations.\n"
            "- **Next.js 14 (App Router) + Tailwind** — fast iteration on a content-and-interaction-heavy UI, "
            "with a route-group sidebar shell that keeps URLs clean after login.\n"
            "- **Docker + Render** — containerized backend, frontend, and Postgres so the whole stack can be "
            "reproduced locally and deployed to a free-tier cloud target with one Blueprint file.\n\n"
            "## What I'm Most Proud Of\n\n"
            "**1. A genuinely parallel multi-agent pipeline, not role-play.** The graph fans out from "
            "`researcher` to three independently-personaed Gemini calls running concurrently, and fans back in "
            "to a `coordinator`. The tricky part was the shared state: three branches writing to the same "
            "`agent_outputs` field at once would normally clobber each other, so I used LangGraph's "
            "`operator.add` reducer to merge concurrent writes safely. The frontend then exposes each agent's "
            "individual analysis in an expandable \"multi-agent process\" view — and LangSmith traces show the "
            "three calls overlapping on the timeline, which is the actual proof that this is parallel execution, "
            "not sequential persona-switching dressed up as one.\n\n"
            "**2. The chart as a single source of truth.** The same `iztro`-computed JSON renders the on-screen "
            "chart board *and* is what the backend reasons over — so the chart a user sees is, by construction, "
            "identical to the chart the AI is interpreting. This single design decision removed an entire class "
            "of \"the AI made up a star that isn't even on my chart\" complaints.\n\n"
            "**3. A real subscription/token economy.** Three plans (free / basic / premium) gate features "
            "(career tools, love tools, compatibility analysis) and meter usage through \"star tokens\" — "
            "every chat message, analysis, and profile creation has a token cost, backed by an atomic "
            "balance-and-ledger system with monthly refresh. It's a small thing to describe, but it's the "
            "difference between a demo and something that could actually run as a product.\n\n"
            "## Challenges & How I Solved Them\n\n"
            "- **\"Multi-agent\" that wasn't.** The earlier version used one LLM cycling through personas in a "
            "ReAct loop — it *looked* multi-agent in the output but wasn't in execution. I rewrote the graph "
            "around LangGraph's fan-out/fan-in primitives so each persona is an independent call, and validated "
            "it externally with LangSmith rather than trusting my own assumptions about the architecture.\n"
            "- **Encoding hell from web-scraped charts.** The original design scraped a third-party chart site "
            "and fought constant cp950/big5-hkscs garbling. Replacing that entirely with client-side `iztro` "
            "computation didn't just fix the encoding bugs — it removed the whole failure category.\n"
            "- **Concurrent writes to shared graph state.** Three parallel agents appending to one list would "
            "race and overwrite each other; solved with an `operator.add` reducer so LangGraph merges the "
            "writes instead of replacing them.\n"
            "- **Streaming chat scroll jitter.** The SSE token-by-token chat kept fighting the user's scroll "
            "position; removing an over-eager `scrollIntoView` call fixed it.\n"
            "- **\"It works on my machine\" — Postgres edition.** Running Docker Compose's Postgres alongside an "
            "already-running native Postgres on port 5432 *looks* healthy (`docker compose ps` says so) but "
            "silently connects to the wrong database with mismatched credentials. Diagnosed via `netstat` and "
            "documented the fix (remap to an alternate host port) so it doesn't cost the next person an hour.\n"
            "- **Google OAuth's three-way config trap.** Sign-in only works when the Google Cloud Console "
            "authorized origin, the frontend's public client ID, and the backend's verification client ID all "
            "match exactly — get one wrong and you get an opaque \"invalid credential\" error. I documented the "
            "checklist so this is a five-minute fix instead of an afternoon of guessing.\n"
            "- **Shipping to a free-tier cloud host.** Render needed an async-driver database URL, automatic "
            "migrations on container start, and a Blueprint that wires backend, frontend, and Postgres together "
            "— all things that don't show up until you actually try to deploy.\n\n"
            "## Results\n\n"
            "- Took the project from a single-purpose take-home test to a deployable product: accounts, "
            "persisted chart profiles, real-time streaming chat, a working subscription/token model, and a "
            "containerized stack running on Docker + Render.\n"
            "- Collapsed a three-vendor LLM stack (Claude + OpenAI + Tavily) into a **single Gemini API key** "
            "for both reasoning and embeddings — simpler config, lower cost, fewer moving parts to monitor.\n"
            "- Replaced a fragile web-scraping chart pipeline (and its encoding bugs) with a deterministic, "
            "client-side engine — eliminating an entire class of correctness complaints at the source.\n"
            "- Independently verified, via LangSmith trace timelines, that the three analysis agents genuinely "
            "execute in parallel rather than merely appearing to.\n\n"
            "## Looking Back, Looking Forward\n\n"
            "The biggest lesson was learning to tell the difference between \"an LLM playing multiple roles\" "
            "and \"an actual multi-agent system\" — and, more importantly, how to *prove* which one you've "
            "built using tracing tools rather than taking the architecture diagram's word for it. The second "
            "was learning to anchor an LLM product on a deterministic ground-truth data source whenever one "
            "exists, instead of asking the model to do something it's structurally bad at.\n\n"
            "Looking ahead: wiring the subscription system to a real payment provider (it currently runs on "
            "manual plan assignment), adding more fortune domains beyond career/love/compatibility, exploring "
            "automated quality scoring across the agents' outputs, and tightening the mobile experience.\n"
        ),
        "body_zh": (
            "## 一句話介紹\n\n"
            "一個讓紫微斗數命理分析「可信、可檢視」的 AI 平台：命盤由真正的排盤引擎精準計算（不靠 LLM 用猜的），"
            "解盤則交由 **三位各自獨立人格設定的 AI 代理人並行分析**，再由第四位整合彙總。圍繞這個核心，"
            "還有一整套產品骨架：帳號系統、命盤典藏、串流對談、以及代幣制訂閱系統。\n\n"
            "## 動機與背景\n\n"
            "這個專案最早是一份實習前的測驗考題——一條簡單的線性流程，讓 LLM 同時「排盤」又「解盤」。"
            "這種做法有兩個讓我很在意的問題。第一，**LLM 排盤會幻覺**：同樣一組生辰，問兩次可能得到兩種不同的星曜配置，"
            "這對任何號稱「分析工具」的產品來說都是不及格的。第二，市面上很多「multi-agent」展示，"
            "其實只是同一個模型在迴圈裡輪流扮演不同角色——demo 看起來唬人，但本質上不是真正的多代理人協作。"
            "於是我持續重寫這個專案，一方面是想把這兩個問題真正解決掉，另一方面也想把它從一支週末腳本，"
            "推進成一個有「產品形狀」的東西：帳號、持久化、計費邏輯、以及部署上線。\n\n"
            "## 系統概觀／架構\n\n"
            "![紫微斗數 Multi-Agent AI 系統](/full%20multi%20agent.png)\n\n"
            "1. **前端**直接在瀏覽器中以官方 `iztro` 引擎排盤——同一份命盤 JSON 同時用來「畫盤」與「送後端解盤」，"
            "確保使用者看到的命盤與 AI 分析依據的命盤完全一致。\n"
            "2. 命盤送到 **FastAPI** 後端後，由 **LangGraph** 圖驅動整個流程：`researcher` 節點先從 **ChromaDB** "
            "RAG 知識庫檢索共享脈絡，接著 **fan-out 並行**展開三位 Gemini 代理人——推理分析師、領域專家、創意詮釋師——"
            "最後 **fan-in** 收斂至 `coordinator` 整合產出最終報告。\n"
            "3. 圍繞這個核心的是完整的帳號層（PostgreSQL + JWT + Google OAuth）、側邊欄應用框架（命盤典藏、"
            "事業／感情算命工具、與算命大師「玄機子」的即時串流對談），以及以「星辰代幣」計量使用量的訂閱系統。\n\n"
            "## 技術選型與理由\n\n"
            "- **iztro 取代 LLM 排盤**——把排盤這件事交給確定性、開源的引擎，從源頭杜絕幻覺；"
            "LLM 的工作收斂到它真正擅長的「解讀」上。\n"
            "- **LangGraph 取代單純的提示鏈**——我需要明確控制分支、並行執行與共享狀態，"
            "也需要第一手的追蹤工具（LangSmith）來「證明」代理人是真的獨立執行，而不是自己說了算。\n"
            "- **單一供應商 Gemini（LLM + Embedding）**——舊版混用 Claude、OpenAI、Tavily 三家，"
            "整合成單一供應商、單一金鑰之後，成本與維運複雜度都明顯下降，品質卻沒有打折。\n"
            "- **ChromaDB**——輕量、檔案型的向量資料庫，啟動時自動 idempotent 索引，"
            "對這個規模的專案來說不需要額外維運一個獨立服務。\n"
            "- **PostgreSQL + SQLAlchemy + Alembic**——當專案從無狀態的分析工具長成帳號制產品，"
            "就需要真正的關聯資料模型（使用者 → 命盤 → 對談 session → 訊息）與可重現的 schema migration。\n"
            "- **Next.js 14（App Router）+ Tailwind**——適合內容與互動密集的介面快速迭代，"
            "並用 route group 做出登入後的側邊欄框架，同時保持網址乾淨。\n"
            "- **Docker + Render**——後端、前端、Postgres 全部容器化，本機可一鍵重現，"
            "雲端則用一份 Blueprint 部署到免費方案上。\n\n"
            "## 核心功能／實作亮點\n\n"
            "**1. 真正並行的 multi-agent，不是換人扮戲。** 圖從 `researcher` fan-out 到三個各自獨立人格設定的 "
            "Gemini 呼叫同時執行，再 fan-in 收斂到 `coordinator`。最棘手的是共享狀態——三個分支同時寫入同一個 "
            "`agent_outputs` 欄位，原本會互相覆蓋，我用 LangGraph 的 `operator.add` reducer 讓並行寫入安全合併。"
            "前端接著把每位代理人的個別分析攤開在可展開的「多代理人分析過程」中——LangSmith trace 上能直接看到"
            "三次呼叫在時間軸上重疊，這才是「並行執行」的真正證據，而不是把循序換角包裝成並行。\n\n"
            "**2. 命盤作為唯一可信來源。** 同一份 `iztro` 排盤 JSON 既用來畫出畫面上的命盤，也是後端解讀的依據——"
            "使用者看到的命盤與 AI 分析的命盤在設計上就保證一致。這一個決策直接消滅了一整類"
            "「AI 編出了我命盤上根本沒有的星曜」的問題。\n\n"
            "**3. 真實運作的訂閱／代幣經濟。** 三個方案（免費／基本／高級）分別開放不同功能"
            "（事業工具、感情工具、合盤分析），並以「星辰代幣」計量使用——每次對談、分析、建立命盤都有代幣成本，"
            "背後是具備原子性的餘額與交易紀錄系統，並按月重新核發。聽起來只是個小細節，"
            "但這正是「demo」與「能真的當產品跑」之間的差別。\n\n"
            "## 遇到的問題與解決方法\n\n"
            "- **名不符實的「multi-agent」。** 舊版是同一個 LLM 在 ReAct 迴圈裡輪流扮演不同人格——"
            "輸出看起來像多代理人，執行上卻不是。我把 graph 改寫成 LangGraph 的 fan-out / fan-in 結構，"
            "讓每個人格都是獨立呼叫，並且不靠自己對架構的假設，而是用 LangSmith 從外部驗證它真的並行。\n"
            "- **爬蟲命盤帶來的編碼地獄。** 舊架構靠爬第三方排盤網站取得命盤資料，長期被 cp950 / big5-hkscs "
            "亂碼問題纏身。改用前端 `iztro` 直接計算後，不只修掉了編碼 bug，而是直接消滅了這整類失敗模式。\n"
            "- **共享 graph 狀態的並行寫入衝突。** 三個並行代理人同時往同一個 list 寫入會互相覆蓋，"
            "用 `operator.add` reducer 讓 LangGraph 合併寫入而非取代，解決了競態問題。\n"
            "- **串流聊天畫面抖動。** SSE 逐字串流時畫面一直跟使用者的捲動「打架」，"
            "移除過於積極的 `scrollIntoView` 呼叫後問題消失。\n"
            "- **「我這邊明明可以跑」── Postgres 篇。** 本機已有原生 PostgreSQL 占用 5432 埠時，"
            "再用 Docker Compose 啟動 Postgres 表面上「健康」（`docker compose ps` 顯示 healthy），"
            "實際上卻悄悄連到錯的資料庫、帳密完全對不上。用 `netstat` 找出真正在監聽的程序，"
            "並把改用替代埠的步驟記錄下來，讓下一個遇到的人不必再花一個下午除錯。\n"
            "- **Google OAuth 的三方設定陷阱。** 登入只有在 Google Cloud Console 的授權來源、"
            "前端的公開 Client ID、後端的驗證 Client ID 三者完全一致時才會成功，"
            "錯一個就會出現語焉不詳的「憑證無效」。把檢查清單寫進文件，讓這從「猜一下午」變成「五分鐘修好」。\n"
            "- **部署到免費雲端方案。** Render 需要 async driver 的資料庫連線字串、容器啟動時自動跑 migration，"
            "以及一份把後端、前端、Postgres 串在一起的 Blueprint——這些事不真的動手部署一次根本不會發現。\n\n"
            "## 成果／效益\n\n"
            "- 把專案從一份單一用途的測驗考題，推進成一個可部署的完整產品：帳號系統、可持久化的多張命盤、"
            "即時串流對談、實際運作的訂閱／代幣模型，以及跑在 Docker + Render 上的容器化架構。\n"
            "- 把原本三家供應商（Claude + OpenAI + Tavily）混用的 LLM 技術棧，整併為**單一 Gemini 金鑰**"
            "同時負責推理與嵌入——設定更簡單、成本更低、需要監控的環節也更少。\n"
            "- 用確定性的前端排盤引擎，取代脆弱又帶有編碼問題的爬蟲命盤流程，從源頭消滅了一整類正確性爭議。\n"
            "- 透過 LangSmith trace 時間軸，獨立驗證了三位分析代理人是「真的並行執行」，而非看似並行。\n\n"
            "## 反思與未來規劃\n\n"
            "最大的收穫，是學會分辨「LLM 在扮演多個角色」與「真正的多代理人系統」的差別——"
            "更重要的是，學會用追蹤工具去「證明」自己做出來的是哪一種，而不是只看架構圖自我感覺良好。"
            "第二個收穫，是學會在有確定性資料來源可用時，把它當成 LLM 產品的「事實基準」，"
            "而不是要求模型去做它在結構上就不擅長的事。\n\n"
            "接下來的規劃：把訂閱系統串接真正的金流服務（目前是手動指派方案）、"
            "在事業／感情／合盤之外擴充更多算命領域、研究對代理人輸出做自動品質評分的方式，"
            "以及持續優化行動裝置體驗。\n"
        ),
        "tech": ["LangGraph", "Google Gemini", "iztro", "ChromaDB RAG", "FastAPI", "PostgreSQL", "Next.js 14", "Docker"],
        "links": {"github": "https://github.com/Tsai1030/Full-multi-agent"},
        "video_url": "https://www.youtube.com/watch?v=aq0F7njXQfM",
        "github_stars": 20,
        "github_forks": 9,
        "period": "2025–2026",
        "role_en": "Solo developer",
        "role_zh": "獨立開發",
        "featured": True,
        "sort": 4,
    },
    {
        "slug": "rag-air-pollution",
        "cover_image": "/RAG%20Air-Pollution.png",
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
        "cover_image": "/Unsloth%20LoRA%20Fine-tuning%20System.png",
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
        "cover_image": "/Graphify%20Atlas%20%E2%80%94%20Graph-Powered%20Knowledge%20Workspace.png",
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
        "slug": "why-i-built-this-site",
        "title_en": "Why I Built This Site (and How It Works)",
        "title_zh": "我為什麼打造這個網站（以及它怎麼運作）",
        "excerpt_en": "The story behind this site — a home for my résumé, projects, and a running log of what I'm learning — plus a quick look at the stack, the data model, and why I chose this architecture.",
        "excerpt_zh": "這個網站的緣起——一個放我的履歷、專案，以及持續記錄學習點滴的地方——順便聊聊技術棧、資料庫結構，以及我為什麼這樣選架構。",
        "body_en": (
            "## Why I built this\n\n"
            "I wanted one place that's truly mine — not just a static résumé, but somewhere I can keep "
            "adding to: projects I ship, things I learn, and the occasional reflection. This blog is where "
            "I'll record the day-to-day — what I'm building, what broke, and what I'd do differently. "
            "Think of it as a running log rather than a finished portfolio.\n\n"
            "## What it runs on\n\n"
            "The site is split into a frontend and a backend:\n\n"
            "- **Frontend** — Next.js (App Router) + TypeScript + Tailwind CSS, deployed on Vercel. "
            "It's bilingual (EN / 中) with a language toggle, renders Markdown content, and uses ISR so "
            "pages stay fast and fresh.\n"
            "- **Backend** — FastAPI + SQLAlchemy (async) + Alembic, managed with uv. It owns all the data "
            "and serves a small JSON API the frontend calls — and it's where a RAG chat assistant will live, soon.\n"
            "- **Database** — Supabase (PostgreSQL) with the pgvector extension.\n\n"
            "## The data model (a peek)\n\n"
            "Everything you see is data, not hardcoded:\n\n"
            "- **projects** — bilingual title / summary / body (Markdown), a tech list, links (JSON), an "
            "optional demo video, GitHub stars / forks, and a date used to order newest-first.\n"
            "- **posts** — bilingual title / excerpt / body, tags, and reading time. This very post is a row "
            "in that table.\n"
            "- **doc_chunks** (reserved) — a pgvector table for embeddings, ready for the chat assistant I'm "
            "building next.\n\n"
            "## Why this architecture\n\n"
            "A few deliberate choices:\n\n"
            "- **A separate Python backend.** Python is my home turf (FastAPI, SQLAlchemy), and the assistant "
            "I want to add next — retrieval-augmented Q&A — is most natural there. A clean API boundary keeps "
            "the frontend simple.\n"
            "- **Next.js on Vercel.** Great developer experience, server rendering + ISR for speed and SEO, "
            "and effortless deploys.\n"
            "- **Supabase + pgvector.** One database for both the content and the future embeddings — fewer "
            "moving parts to maintain.\n"
            "- **Content as data.** Storing projects and posts in the DB (instead of hardcoding them) lets me "
            "add or edit things without redeploying, and bilingual content is just two columns.\n\n"
            "## What's next\n\n"
            "I'll keep writing here as I go. The next big piece is an AI assistant that can answer questions "
            "about me and link you straight to the relevant project or post. More soon.\n"
        ),
        "body_zh": (
            "## 為什麼做這個網站\n\n"
            "我想要一個真正屬於自己的地方——不只是一份靜態履歷，而是一個能持續往上加東西的空間：我做的專案、"
            "學到的東西，偶爾還有一些心得。這個部落格就是我用來記錄點點滴滴的地方：在做什麼、卡在哪、之後會怎麼改。"
            "與其說是完成的作品集，不如說是一份持續更新的紀錄。\n\n"
            "## 目前用什麼做的\n\n"
            "網站分成前端與後端：\n\n"
            "- **前端** — Next.js（App Router）+ TypeScript + Tailwind CSS，部署在 Vercel。支援中英切換、"
            "以 Markdown 呈現內容，並用 ISR 讓頁面又快又新。\n"
            "- **後端** — FastAPI + SQLAlchemy（async）+ Alembic，用 uv 管理。它掌管所有資料、提供一組小巧的 "
            "JSON API 給前端呼叫——之後的 RAG 聊天助手也會放在這裡。\n"
            "- **資料庫** — Supabase（PostgreSQL）＋ pgvector 擴充。\n\n"
            "## 資料庫結構（小小揭露）\n\n"
            "你看到的一切都是「資料」，不是寫死的：\n\n"
            "- **projects** — 雙語的標題／摘要／內文（Markdown）、技術清單、連結（JSON）、可選的示範影片、"
            "GitHub 星數／fork 數，以及一個用來「由新到舊」排序的日期。\n"
            "- **posts** — 雙語的標題／摘要／內文、tags、閱讀時間。你正在看的這篇，就是這張表裡的一筆資料。\n"
            "- **doc_chunks**（保留）— 一張 pgvector 向量表，為我接下來要做的聊天助手預留。\n\n"
            "## 為什麼選這樣的架構\n\n"
            "幾個刻意的選擇：\n\n"
            "- **獨立的 Python 後端。** Python 是我最熟的主場（FastAPI、SQLAlchemy），而我接下來想加的助手——"
            "檢索增強的問答——在 Python 生態最自然。清楚的 API 邊界也讓前端保持單純。\n"
            "- **Next.js + Vercel。** 開發體驗好、有 SSR + ISR 兼顧速度與 SEO，部署也很省事。\n"
            "- **Supabase + pgvector。** 同一個資料庫同時放內容與未來的向量，要維護的東西更少。\n"
            "- **內容即資料。** 把專案與文章存在資料庫（而不是寫死），不重新部署也能新增／修改，雙語也只是多兩個欄位。\n\n"
            "## 接下來\n\n"
            "我會邊做邊持續在這裡寫；下一個大工程是一個 AI 助手，能回答關於我的問題、並直接帶你連到對應的專案或文章。"
            "敬請期待。\n"
        ),
        "tags": ["Meta", "Architecture", "Notes"],
        "reading_minutes": 5,
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
