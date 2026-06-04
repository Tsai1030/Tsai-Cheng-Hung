"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLang } from "./LangContext";
import { StarIcon, ForkIcon } from "./icons";
import type { ProjectDetail } from "@/lib/api";

const LINK_LABELS: Record<string, string> = {
  github: "GitHub",
  demo: "Live demo",
  paper: "Paper",
};

// Fixed display order (JSONB doesn't preserve key order); unknown keys go last.
const LINK_ORDER = ["github", "demo", "paper"];
const linkRank = (key: string) => {
  const i = LINK_ORDER.indexOf(key);
  return i === -1 ? LINK_ORDER.length : i;
};

function youtubeId(url: string): string | null {
  const m = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([\w-]{11})/);
  return m ? m[1] : null;
}

export default function ProjectDetailView({ project: p }: { project: ProjectDetail }) {
  const { lang } = useLang();
  const t = <T,>(en: T, zh: T) => (lang === "en" ? en : zh);
  const ytId = p.video_url ? youtubeId(p.video_url) : null;

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

      {(Object.keys(p.links ?? {}).length > 0 || p.github_stars != null || p.github_forks != null) && (
        <div className="pd-links">
          {Object.entries(p.links)
            .sort(([a], [b]) => linkRank(a) - linkRank(b))
            .map(([key, url]) => (
              <a key={key} href={url} target="_blank" rel="noopener">
                {LINK_LABELS[key] ?? key} ↗
              </a>
            ))}
          {(p.github_stars != null || p.github_forks != null) && (
            <span className="pd-ghstats">
              {p.github_stars != null && (
                <span className="ghstat"><StarIcon /> {p.github_stars}</span>
              )}
              {p.github_forks != null && (
                <span className="ghstat"><ForkIcon /> {p.github_forks}</span>
              )}
            </span>
          )}
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

      {ytId && (
        <div className="pd-video">
          <iframe
            src={`https://www.youtube.com/embed/${ytId}?rel=0`}
            title={t("Project demo video", "專案示範影片")}
            loading="lazy"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
          />
        </div>
      )}

      <article className="pd-body">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            img: ({ src, alt }) => (
              <span className="pd-fig">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={typeof src === "string" ? src : ""} alt={alt ?? ""} />
                {alt ? <span className="cap">{alt}</span> : null}
              </span>
            ),
          }}
        >
          {t(p.body_en, p.body_zh)}
        </ReactMarkdown>
      </article>
    </div>
  );
}
