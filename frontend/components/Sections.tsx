"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { L, Rich, useLang } from "./LangContext";
import { GitHubIcon, LinkedInIcon, MailIcon, PhoneIcon } from "./icons";
import ScrollPaint from "./fx/ScrollPaint";
import type { ProjectCard } from "@/lib/api";

const d = (s: number) => ({ "--d": `${s}s` } as CSSProperties);

function SecLabel({
  idx,
  en,
  zh,
  tagEn,
  tagZh,
}: {
  idx: string;
  en: string;
  zh: string;
  tagEn: string;
  tagZh: string;
}) {
  return (
    <div className="sec-label">
      <div className="idx" data-reveal>SYS/{idx}</div>
      <h2 data-reveal style={d(0.06)}>
        <L en={en} zh={zh} />
      </h2>
      <p className="tag" data-reveal style={d(0.12)}>
        <L en={tagEn} zh={tagZh} />
      </p>
    </div>
  );
}

export function About() {
  return (
    <section id="about" className="sec">
      <div className="layout">
        <SecLabel
          idx="01"
          en="About"
          zh="關於我"
          tagEn="A medical-informatics graduate who fell for frontend craft."
          tagZh="一個愛上前端工藝的醫務資訊背景工程師。"
        />
        <div>
          <Rich
            as="p"
            className="about-tagline"
            data-reveal=""
            en="AI Application & Frontend Engineer — building <b>reliable AI systems</b> and shipping <b>real-world products</b>."
            zh="AI 應用與全端工程師——打造<b>可靠的 AI 系統</b>，交付<b>真正能用的產品</b>。"
          />
          <div className="hi" data-reveal style={d(0.08)}>
            <span className="prompt">&gt;</span> <L en="Hi, I'm Tsai Cheng-Hung!" zh="嗨，我是蔡承紘！" />
          </div>
          <ScrollPaint className="bio">
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
          </ScrollPaint>
          <div className="about-links" data-reveal style={d(0.2)}>
            <a href="https://github.com/Tsai1030" target="_blank" rel="noopener"><GitHubIcon /> GitHub</a>
            <a href="https://www.linkedin.com/in/chenghung-tsai-1970b2390" target="_blank" rel="noopener"><LinkedInIcon /> LinkedIn</a>
            <a href="mailto:pijh102511@gmail.com"><MailIcon /> pijh102511@gmail.com</a>
          </div>
          <div className="about-tags" data-reveal style={d(0.26)}>
            <span><L en="RAG Systems" zh="RAG 系統" /></span>
            <span><L en="Agentic AI" zh="AI Agent" /></span>
            <span><L en="Full-Stack AI" zh="全端 AI" /></span>
          </div>
        </div>
      </div>
    </section>
  );
}

const xp = [
  {
    date: ["2026.04 — PRESENT", "2026.04 — 迄今"],
    role: { en: "AI Application Engineer", zh: "AI 應用工程師" },
    org: "BES / 中華工程",
    desc: {
      en: "Building production RAG systems, autonomous agents, and automation pipelines.",
      zh: "負責產品級 RAG 系統、自主 Agent 與自動化流程開發。",
    },
    live: true,
  },
  {
    date: ["2025.08 — 2025.10", "2025.08 — 2025.10"],
    role: { en: "AI Engineer (Intern)", zh: "AI 工程師（實習）" },
    org: "學思行數位行銷",
    desc: {
      en: "Full-stack on a small product, frontend lead on a large one. Agent flows (LangGraph/LangChain), Flask & FastAPI, RAG, streaming responses; React/Next.js, Zustand, Prisma + PostgreSQL.",
      zh: "小專案全端、大專案前端主導。Agent flow（LangGraph/LangChain）、Flask 與 FastAPI、RAG、串流回覆；React/Next.js、Zustand、Prisma + PostgreSQL。",
    },
  },
  {
    date: ["2025.03 — 2025.06", "2025.03 — 2025.06"],
    role: { en: "Teaching Assistant — Generative AI", zh: "臺灣大專院校人工智慧學程聯盟助教 — 生成式 AI" },
    org: { en: "Kaohsiung Medical University", zh: "高雄醫學大學" },
    desc: {
      en: "Supported ~100 students in model application and coding; designed AI problem-solving tasks.",
      zh: "支援約 100 位學生的模型應用與程式開發，設計 AI 解題任務。",
    },
  },
];

export function Experience() {
  return (
    <section id="experience" className="sec">
      <div className="layout">
        <SecLabel
          idx="03"
          en="Experience"
          zh="工作經歷"
          tagEn="1–2 years across AI engineering, full-stack, and teaching."
          tagZh="橫跨 AI 工程、全端開發與教學的 1–2 年經歷。"
        />
        <div className="xp">
          {xp.map((item, i) => (
            <div className="xp-item" key={i} data-reveal style={d(i * 0.08)}>
              <div className="xp-date">
                <span className="xp-node" />
                <L en={item.date[0]} zh={item.date[1]} />
                {item.live && <span className="xp-live"><L en="● LIVE" zh="● 進行中" /></span>}
              </div>
              <div className="xp-body">
                <h3><L {...item.role} /></h3>
                <div className="org">
                  {typeof item.org === "string" ? item.org : <L {...item.org} />}
                </div>
                <p><L {...item.desc} /></p>
              </div>
            </div>
          ))}
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
    <section id="skills" className="sec">
      <div className="layout">
        <SecLabel
          idx="04"
          en="Toolkit"
          zh="技能"
          tagEn="From embeddings to interfaces."
          tagZh="從向量嵌入到使用者介面。"
        />
        <div className="skills-grid">
          {skillCats.map((cat, i) => (
            <div className="skill-cat" key={i} data-reveal style={d(i * 0.08)}>
              <h4>
                <span className="mod">MOD.{String(i + 1).padStart(2, "0")}</span>
                <L {...cat.title} />
              </h4>
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

export function Projects({ projects }: { projects: ProjectCard[] }) {
  const { lang } = useLang();
  const t = <T,>(en: T, zh: T) => (lang === "en" ? en : zh);
  return (
    <section id="projects" className="sec">
      <div className="layout">
        <SecLabel
          idx="05"
          en="Selected Work"
          zh="精選專案"
          tagEn="Systems shipped, not just demoed."
          tagZh="不只是 demo，而是真正上線的系統。"
        />
        <div className="proj">
          {projects.map((p, i) => (
            <Link className="proj-item" href={`/projects/${p.slug}`} key={p.id} data-reveal style={d(i * 0.06)}>
              <span className="proj-idx">{String(i + 1).padStart(2, "0")}</span>
              <div className="proj-main">
                <h3>{t(p.title_en, p.title_zh)}</h3>
                <div className="stack">{p.tech.join(" / ")}</div>
                <p>{t(p.summary_en, p.summary_zh)}</p>
              </div>
              <span className="proj-arrow">↗</span>
            </Link>
          ))}
          <div className="proj-more" data-reveal>
            <Link href="/projects" data-hover>
              {lang === "en" ? "ALL PROJECTS" : "所有專案"} <span className="ar">→</span>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Publication() {
  return (
    <section className="sec pub">
      <div className="layout">
        <SecLabel
          idx="06"
          en="Publication"
          zh="學術發表"
          tagEn="AIET 2026 · Zagreb, Croatia"
          tagZh="AIET 2026 · 克羅埃西亞 札格雷布"
        />
        <div className="pub-body" data-reveal>
          <span className="pub-badge"><L en="ACCEPTED // ORAL" zh="獲接受 // 口頭報告" /></span>
          <h3>
            <L
              en="From Information Asymmetry to Contextual Intelligence: AI-Supported Innovation Learning for Social Impact in Environmental Governance"
              zh="From Information Asymmetry to Contextual Intelligence：環境治理中以 AI 支持社會影響的創新學習"
            />
          </h3>
          <p className="meta">
            <L
              en="7th Intl. Conference on AI in Education Technology · Co-first author · July 2026"
              zh="第七屆人工智慧教育科技國際研討會 · 共同第一作者 · 2026 年 7 月"
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
      <div className="foot-eyebrow" data-reveal>
        <L en="// NEXT_PROCESS" zh="// 下一步" />
      </div>
      <Rich as="h2" className="foot-title" data-reveal en="LET'S BUILD<br>SOMETHING." zh="一起打造<br>點什麼。" />
      <div className="contact" data-reveal>
        <a href="https://github.com/Tsai1030" target="_blank" rel="noopener"><GitHubIcon /> github.com/Tsai1030</a>
        <a href="mailto:pijh102511@gmail.com"><MailIcon /> pijh102511@gmail.com</a>
        <a href="tel:+886965072800"><PhoneIcon /> 0965 072 800</a>
      </div>
      <div className="foot-meta">
        <span>© 2026 TSAI CHENG-HUNG</span>
        <span>BUILT WITH NEXT.JS + THREE.JS</span>
        <span>KAOHSIUNG // TAIPEI — TW</span>
      </div>
    </footer>
  );
}
