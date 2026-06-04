"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLang } from "./LangContext";
import type { ProjectDetail } from "@/lib/api";

const LINK_LABELS: Record<string, string> = {
  github: "GitHub",
  demo: "Live demo",
  paper: "Paper",
};

export default function ProjectDetailView({ project: p }: { project: ProjectDetail }) {
  const { lang } = useLang();
  const t = <T,>(en: T, zh: T) => (lang === "en" ? en : zh);

  return (
    <div className="pd-wrap">
      <Link className="pd-back" href="/projects">← {t("All projects", "所有專案")}</Link>

      <div className="pd-eyebrow">
        {p.period ?? ""}
        {p.featured ? ` · ${t("Featured", "精選")}` : ""}
      </div>
      <h1>{t(p.title_en, p.title_zh)}</h1>
      <p className="pd-summary">{t(p.summary_en, p.summary_zh)}</p>

      <div className="pd-meta">
        {(p.role_en || p.role_zh) && <span>{t(p.role_en, p.role_zh)}</span>}
      </div>

      {Object.keys(p.links ?? {}).length > 0 && (
        <div className="pd-links">
          {Object.entries(p.links).map(([key, url]) => (
            <a key={key} href={url} target="_blank" rel="noopener">
              {LINK_LABELS[key] ?? key} ↗
            </a>
          ))}
        </div>
      )}

      {p.tech.length > 0 && (
        <div className="pd-chips">
          {p.tech.map((tech) => (
            <span key={tech}>{tech}</span>
          ))}
        </div>
      )}

      {p.cover_image && (
        <div className="pd-cover">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={p.cover_image} alt="" />
        </div>
      )}

      <article className="pd-body">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{t(p.body_en, p.body_zh)}</ReactMarkdown>
      </article>
    </div>
  );
}
