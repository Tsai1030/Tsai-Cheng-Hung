"use client";

import Link from "next/link";
import { L, Rich, useLang } from "./LangContext";
import { GitHubIcon, LinkedInIcon, MailIcon, PhoneIcon } from "./icons";

export function About() {
  return (
    <section id="about">
      <div className="layout">
        <div className="sticky-label">
          <div className="num">01</div>
          <h2><L en="About" zh="關於我" /></h2>
          <p className="tag">
            <L en="A medical-informatics graduate who fell for frontend craft." zh="一個愛上前端工藝的醫務資訊背景工程師。" />
          </p>
        </div>
        <div>
          <Rich
            as="p"
            className="about-tagline"
            en="AI Application & Frontend Engineer — building <b>reliable AI systems</b> and shipping <b>real-world products</b>."
            zh="AI 應用與全端工程師——打造<b>可靠的 AI 系統</b>，交付<b>真正能用的產品</b>。"
          />
          <div className="hi"><L en="Hi, I'm Tsai Cheng-Hung!" zh="嗨，我是蔡承紘！" /></div>
          <div className="bio">
            <p>
              <L
                en="I'm a Master's graduate from the AI track of Medical Informatics at Kaohsiung Medical University, specializing in RAG systems, agentic workflows, and the frontend interfaces that bring them to life."
                zh="我是高雄醫學大學醫務資訊學系 AI 組碩士，專注於 RAG 系統、agentic workflow，以及讓它們真正好用的前端介面。"
              />
            </p>
            <p>
              <L
                en="With a focus on moving AI from prototype to production, I've built and deployed agentic workflows with LangGraph and RAG-driven Q&A pipelines — from a complete air-pollution thesis system to multi-agent consultation platforms. My strength lies in bridging large language models and robust full-stack systems: integrating vector databases, prompt and persona control, and guardrails that keep model output reliable and user-friendly."
                zh="我擅長把 AI 從原型推向產品——以 LangGraph 打造並部署 agentic workflow 與 RAG 問答流程，從完整的空污論文系統到多 Agent 諮詢平台。我的強項在於銜接大型語言模型與穩健的全端系統：整合向量資料庫、Prompt 與 Persona 控制，以及確保模型輸出可靠且友善的防護機制。"
              />
            </p>
          </div>
          <div className="about-links">
            <a href="https://github.com/Tsai1030" target="_blank" rel="noopener"><GitHubIcon /> GitHub</a>
            <a href="https://www.linkedin.com/in/chenghung-tsai-1970b2390" target="_blank" rel="noopener"><LinkedInIcon /> LinkedIn</a>
            <a href="mailto:pijh102511@gmail.com"><MailIcon /> pijh102511@gmail.com</a>
          </div>
          <div className="about-tags">
            <span><L en="RAG Systems" zh="RAG 系統" /></span>
            <span><L en="Agentic AI" zh="AI Agent" /></span>
            <span><L en="Full-Stack AI" zh="全端 AI" /></span>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Experience() {
  return (
    <section id="experience">
      <div className="layout">
        <div className="sticky-label">
          <div className="num">03</div>
          <h2><L en="Experience" zh="工作經歷" /></h2>
          <p className="tag">
            <L en="1–2 years across AI engineering, full-stack, and teaching." zh="橫跨 AI 工程、全端開發與教學的 1–2 年經歷。" />
          </p>
        </div>
        <div className="xp">
          <div className="xp-item">
            <div className="xp-date">2026.04 — <L en="Present" zh="迄今" /></div>
            <div>
              <h3><L en="AI Application Engineer" zh="AI 應用工程師" /></h3>
              <div className="org">BES / 中華工程</div>
              <p>
                <L
                  en="Building production RAG systems, autonomous agents, and automation pipelines."
                  zh="負責產品級 RAG 系統、自主 Agent 與自動化流程開發。"
                />
              </p>
            </div>
          </div>
          <div className="xp-item">
            <div className="xp-date">2025.08 — 2025.10</div>
            <div>
              <h3><L en="AI Engineer (Intern)" zh="AI 工程師（實習）" /></h3>
              <div className="org">學思行數位行銷</div>
              <p>
                <L
                  en="Full-stack on a small product, frontend lead on a large one. Agent flows (LangGraph/LangChain), Flask & FastAPI, RAG, streaming responses; React/Next.js, Zustand, Prisma + PostgreSQL."
                  zh="小專案全端、大專案前端主導。Agent flow（LangGraph/LangChain）、Flask 與 FastAPI、RAG、串流回覆；React/Next.js、Zustand、Prisma + PostgreSQL。"
                />
              </p>
            </div>
          </div>
          <div className="xp-item">
            <div className="xp-date">2025.03 — 2025.06</div>
            <div>
              <h3><L en="Teaching Assistant — Generative AI" zh="助教 — 生成式 AI" /></h3>
              <div className="org"><L en="Kaohsiung Medical University" zh="高雄醫學大學" /></div>
              <p>
                <L
                  en="Supported ~100 students in model application and coding; designed AI problem-solving tasks."
                  zh="支援約 100 位學生的模型應用與程式開發，設計 AI 解題任務。"
                />
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

const skillCats: { title: { en: string; zh: string }; chips: string[] }[] = [
  { title: { en: "AI / ML", zh: "AI / 機器學習" }, chips: ["PyTorch", "Hugging Face", "RAG", "LangGraph", "Agentic Workflow", "Prompt Engineering", "LoRA / unsloth", "Embeddings"] },
  { title: { en: "Backend", zh: "後端" }, chips: ["FastAPI", "Flask", "LangChain", "Ollama", "ChromaDB", "REST API"] },
  { title: { en: "Frontend", zh: "前端" }, chips: ["React", "Next.js", "TypeScript", "Tailwind", "Vite", "Zustand", "RWD"] },
  { title: { en: "Data / Tools", zh: "資料 / 工具" }, chips: ["PostgreSQL", "MySQL", "Prisma", "Pinecone", "Git", "Docker"] },
];

export function Skills() {
  return (
    <section id="skills">
      <div className="layout">
        <div className="sticky-label">
          <div className="num">04</div>
          <h2><L en="Toolkit" zh="技能" /></h2>
          <p className="tag"><L en="From embeddings to interfaces." zh="從向量嵌入到使用者介面。" /></p>
        </div>
        <div className="skills-grid">
          {skillCats.map((cat, i) => (
            <div className="skill-cat" key={i}>
              <h4><L {...cat.title} /></h4>
              <div className="chips">
                {cat.chips.map((c) => (
                  <span className="chip" key={c}>{c}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const projects: { title: { en: string; zh: string }; stack: string; desc: { en: string; zh: string } }[] = [
  {
    title: { en: "Eastern Mysticism Platform", zh: "東方命理平台" },
    stack: "LangGraph · GPT-4o · Quart · Redis · PostgreSQL + Pinecone · Next.js 15 · Three.js / GSAP",
    desc: { en: "Multi-agent consultation platform with SSE streaming and a custom Zi-Wei chart engine.", zh: "多 Agent 命理諮詢平台，支援 SSE 串流與自製紫微斗數排盤引擎。" },
  },
  {
    title: { en: "Multi-modal AI Knowledge Base", zh: "多模態 AI 知識庫" },
    stack: "FastAPI · ChromaDB · MinerU · RAGAnything · Next.js 16 · Ollama · Docker",
    desc: { en: "Fully local RAG platform: upload PDFs & images, parse, index, and chat — data never leaves the box.", zh: "完全本地的 RAG 平台：上傳 PDF 與圖片，自動解析、索引、問答，資料不外傳。" },
  },
  {
    title: { en: "RAG Air-Pollution Q&A", zh: "RAG 空污問答系統" },
    stack: "bge-m3 · Chroma · Gemma 3:12B · LangChain · FastAPI · MMR + Rerank · RAGAS",
    desc: { en: "My Master's thesis system — deployed publicly via DuckDNS + Nginx with HTTPS.", zh: "我的碩士論文系統——透過 DuckDNS + Nginx 公開部署並支援 HTTPS。" },
  },
  {
    title: { en: "RAG Medical Q&A (ReAct)", zh: "RAG 醫療問答（ReAct）" },
    stack: "ReAct Agent · GPT-4o · Google Serper · LangChain · FastAPI",
    desc: { en: "A ReAct agent that chooses between a local doctor database and live web search per question.", zh: "ReAct 代理可依問題自動選擇本地醫師資料庫或即時網路搜尋。" },
  },
];

export function Projects() {
  const { lang } = useLang();
  return (
    <section id="projects">
      <div className="layout">
        <div className="sticky-label">
          <div className="num">05</div>
          <h2><L en="Selected Work" zh="精選專案" /></h2>
          <p className="tag"><L en="Systems shipped, not just demoed." zh="不只是 demo，而是真正上線的系統。" /></p>
        </div>
        <div className="proj">
          {projects.map((p, i) => (
            <div className="proj-item" key={i}>
              <div>
                <h3><L {...p.title} /></h3>
                <div className="stack">{p.stack}</div>
                <p><L {...p.desc} /></p>
              </div>
              <div className="proj-arrow">↗</div>
            </div>
          ))}
          <div className="proj-more">
            <Link href="/projects">
              {lang === "en" ? "More" : "更多"} <span className="ar">→</span>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Publication() {
  return (
    <section className="pub">
      <div className="layout">
        <div className="sticky-label">
          <div className="num">06</div>
          <h2><L en="Publication" zh="學術發表" /></h2>
          <p className="tag" style={{ color: "var(--middeep)" }}>
            <L en="AIET 2026 · Zagreb, Croatia" zh="AIET 2026 · 克羅埃西亞 札格雷布" />
          </p>
        </div>
        <div className="pub-body">
          <h3>
            <L
              en="From Information Asymmetry to Contextual Intelligence: AI-Supported Innovation Learning for Social Impact in Environmental Governance"
              zh="From Information Asymmetry to Contextual Intelligence：環境治理中以 AI 支持社會影響的創新學習"
            />
          </h3>
          <p className="meta">
            <L
              en="Accepted for Oral Presentation · 7th Intl. Conference on AI in Education Technology · Co-first author · July 2026"
              zh="口頭報告獲接受 · 第七屆人工智慧教育科技國際研討會 · 共同第一作者 · 2026 年 7 月"
            />
          </p>
        </div>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer>
      <Rich as="h2" en="Let's build<br>something." zh="一起<br>打造點什麼。" />
      <div className="contact">
        <a href="https://github.com/Tsai1030" target="_blank" rel="noopener"><GitHubIcon /> github.com/Tsai1030</a>
        <a href="mailto:pijh102511@gmail.com"><MailIcon /> pijh102511@gmail.com</a>
        <a href="tel:+886965072800"><PhoneIcon /> 0965 072 800</a>
      </div>
    </footer>
  );
}
