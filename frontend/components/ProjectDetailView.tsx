"use client";

import Link from "next/link";
import Image from "next/image";
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
  // Show the cover on the detail page only when the project has no other media
  // (no video and no image embedded in the body) — otherwise it's redundant.
  const bodyHasImage = /!\[[^\]]*\]\([^)]*\)/.test(p.body_en) || /!\[[^\]]*\]\([^)]*\)/.test(p.body_zh);
  const showCover = Boolean(p.cover_image) && !ytId && !bodyHasImage;

  return (
    <main className="page pd-wrap">
      <Link className="pd-back" href="/projects" data-hover>
        ← {t("ALL PROJECTS", "所有專案")}
      </Link>

      <div className="pd-eyebrow" data-reveal>
        PROJECT_FILE {p.period ? `· ${p.period}` : ""}
        {p.featured ? ` · ★ ${t("FEATURED", "精選")}` : ""}
      </div>
      <h1 data-reveal>{t(p.title_en, p.title_zh)}</h1>
      <p className="pd-summary" data-reveal>{t(p.summary_en, p.summary_zh)}</p>

      {(p.role_en || p.role_zh) && (
        <div className="pd-meta" data-reveal>
          <span>{t(p.role_en, p.role_zh)}</span>
        </div>
      )}

      {(Object.keys(p.links ?? {}).length > 0 || p.github_stars != null || p.github_forks != null) && (
        <div className="pd-links" data-reveal>
          {Object.entries(p.links)
            .sort(([a], [b]) => linkRank(a) - linkRank(b))
            .map(([key, url]) => (
              <a key={key} href={url} target="_blank" rel="noopener" data-hover>
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
        <div className="pd-chips" data-reveal>
          {p.tech.map((tech) => (
            <span key={tech}>{tech}</span>
          ))}
        </div>
      )}

      {showCover && p.cover_image && (
        <div className="pd-cover" data-reveal>
          <Image src={p.cover_image} alt="" fill sizes="(max-width: 820px) 100vw, 880px" style={{ objectFit: "cover" }} />
        </div>
      )}

      {ytId && (
        <div className="pd-video" data-reveal>
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
    </main>
  );
}
