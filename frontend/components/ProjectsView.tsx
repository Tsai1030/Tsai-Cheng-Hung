"use client";

import Link from "next/link";
import Image from "next/image";
import type { CSSProperties, MouseEvent } from "react";
import { useLang } from "./LangContext";
import LikeButton from "./LikeButton";
import { EyeIcon } from "./icons";
import type { ProjectCard } from "@/lib/api";

const pad = (n: number) => String(n).padStart(2, "0");

function Pager({
  current,
  total,
  base,
  query,
}: {
  current: number;
  total: number;
  base: string;
  /** Extra query params to preserve across page links (e.g. an active tag filter). */
  query?: Record<string, string>;
}) {
  const { lang } = useLang();
  const pages = Array.from({ length: total }, (_, i) => i + 1);
  const href = (n: number) => {
    const p = new URLSearchParams(query);
    if (n > 1) p.set("page", String(n));
    const qs = p.toString();
    return qs ? `${base}?${qs}` : base;
  };
  return (
    <div className="pager" role="navigation" aria-label={lang === "en" ? "Pagination" : "分頁"}>
      {current <= 1 ? (
        <span className="disabled arrow">←</span>
      ) : (
        <Link className="arrow" href={href(current - 1)} aria-label="Previous">←</Link>
      )}
      {pages.map((n) =>
        n === current ? (
          <span key={n} className="active" aria-current="page">{pad(n)}</span>
        ) : (
          <Link key={n} href={href(n)}>{pad(n)}</Link>
        )
      )}
      {current >= total ? (
        <span className="disabled arrow">→</span>
      ) : (
        <Link className="arrow" href={href(current + 1)} aria-label="Next">→</Link>
      )}
    </div>
  );
}

export { Pager };

// 3D tilt driven by pointer position, written to CSS vars on the card.
function tilt(e: MouseEvent<HTMLElement>) {
  const el = e.currentTarget;
  const r = el.getBoundingClientRect();
  const px = (e.clientX - r.left) / r.width - 0.5;
  const py = (e.clientY - r.top) / r.height - 0.5;
  el.style.setProperty("--rx", `${(-py * 5).toFixed(2)}deg`);
  el.style.setProperty("--ry", `${(px * 7).toFixed(2)}deg`);
  el.style.setProperty("--gx", `${((px + 0.5) * 100).toFixed(1)}%`);
  el.style.setProperty("--gy", `${((py + 0.5) * 100).toFixed(1)}%`);
}
function untilt(e: MouseEvent<HTMLElement>) {
  const el = e.currentTarget;
  el.style.setProperty("--rx", "0deg");
  el.style.setProperty("--ry", "0deg");
}

export default function ProjectsView({
  items,
  startIndex,
  current,
  total,
}: {
  items: ProjectCard[];
  startIndex: number;
  current: number;
  total: number;
}) {
  const { lang } = useLang();
  const t = <T,>(en: T, zh: T) => (lang === "en" ? en : zh);

  return (
    <main className="page">
      <div className="page-head">
        <div className="page-eyebrow" data-reveal>SYS/05 — {t("SELECTED WORK", "精選專案")}</div>
        <h1 data-reveal>{t("PROJECTS", "專案")}</h1>
        <p className="page-sub" data-reveal>
          {t("Systems shipped, not just demoed.", "不只是 demo，而是真正上線的系統。")}
        </p>
      </div>

      <div className="pj-grid">
        {items.map((p, i) => {
          const n = pad(startIndex + i + 1);
          return (
            <Link
              className="pj-card"
              href={`/projects/${p.slug}`}
              key={p.id}
              data-reveal
              data-hover
              style={{ "--d": `${(i % 2) * 0.08}s` } as CSSProperties}
              onMouseMove={tilt}
              onMouseLeave={untilt}
            >
              <span className="bk bk-tl" /><span className="bk bk-tr" />
              <span className="bk bk-bl" /><span className="bk bk-br" />
              <div className="pj-cover">
                {p.cover_image ? (
                  <Image
                    src={p.cover_image}
                    alt=""
                    fill
                    sizes="(max-width: 820px) 100vw, 600px"
                    style={{ objectFit: "cover" }}
                    priority={i < 2}
                  />
                ) : (
                  <span className="pj-figno">{n}</span>
                )}
                <span className="pj-scan" aria-hidden="true" />
                <span className="pj-fig">FIG_{n}</span>
                {p.featured && <span className="pj-fe">★ {t("FEATURED", "精選")}</span>}
              </div>
              <div className="pj-body">
                <div className="pj-row">
                  <span className="pj-no">{n}</span>
                  {p.period && <span className="pj-yr">{p.period}</span>}
                </div>
                <h3>{t(p.title_en, p.title_zh)}</h3>
                <p className="pj-sum">{t(p.summary_en, p.summary_zh)}</p>
                <div className="pj-chips">
                  {p.tech.slice(0, 4).map((tech) => (
                    <span key={tech}>{tech}</span>
                  ))}
                </div>
                <div className="pj-like">
                  <span className="view-count" aria-label={t("Views", "瀏覽次數")}>
                    <EyeIcon />
                    {p.views}
                  </span>
                  <LikeButton kind="project" id={p.id} initial={p.likes} />
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      <Pager current={current} total={total} base="/projects" />
    </main>
  );
}
