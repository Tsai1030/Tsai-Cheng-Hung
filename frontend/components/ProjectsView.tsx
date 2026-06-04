"use client";

import Link from "next/link";
import { useLang } from "./LangContext";
import type { ProjectCard } from "@/lib/api";

const pad = (n: number) => String(n).padStart(2, "0");

function Pager({ current, total }: { current: number; total: number }) {
  const { lang } = useLang();
  const pages = Array.from({ length: total }, (_, i) => i + 1);
  const href = (n: number) => (n === 1 ? "/projects" : `/projects?page=${n}`);
  const prevDisabled = current <= 1;
  const nextDisabled = current >= total;
  return (
    <div className="pager" role="navigation" aria-label={lang === "en" ? "Pagination" : "分頁"}>
      {prevDisabled ? (
        <span className="disabled arrow">←</span>
      ) : (
        <Link className="arrow" href={href(current - 1)} aria-label="Previous">←</Link>
      )}
      {pages.map((n) =>
        n === current ? (
          <span key={n} className="active" aria-current="page">{n}</span>
        ) : (
          <Link key={n} href={href(n)}>{n}</Link>
        )
      )}
      {nextDisabled ? (
        <span className="disabled arrow">→</span>
      ) : (
        <Link className="arrow" href={href(current + 1)} aria-label="Next">→</Link>
      )}
    </div>
  );
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
    <>
      <div className="pj-wrap">
        <div>
          <div className="pj-eyebrow">05 — {t("Selected Work", "精選專案")}</div>
          <h1>{t("Projects", "專案")}</h1>
        </div>
        <p className="pj-intro">
          {t("Jotting down the little moments", "紀錄點點滴滴")}
          <span className="pj-dots" aria-hidden="true">
            <span>.</span>
            <span>.</span>
            <span>.</span>
          </span>
        </p>
      </div>

      <div className="pj-grid">
        {items.map((p, i) => {
          const n = pad(startIndex + i + 1);
          return (
            <Link className="pj-card" href={`/projects/${p.slug}`} key={p.id}>
              <div className="pj-cover">
                {p.cover_image ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={p.cover_image} alt="" />
                ) : (
                  <span className="pj-figno">{n}</span>
                )}
                <span className="pj-fig">fig. {n}</span>
                {p.featured && <span className="pj-fe">{t("Featured", "精選")}</span>}
              </div>
              <div className="pj-body">
                {p.period && <div className="pj-yr">{p.period}</div>}
                <h3>{t(p.title_en, p.title_zh)}</h3>
                <p className="pj-sum">{t(p.summary_en, p.summary_zh)}</p>
                <div className="pj-chips">
                  {p.tech.slice(0, 4).map((tech) => (
                    <span key={tech}>{tech}</span>
                  ))}
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      <Pager current={current} total={total} />
    </>
  );
}
