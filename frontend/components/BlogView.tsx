"use client";

import Link from "next/link";
import { useLang } from "./LangContext";
import type { PostCard } from "@/lib/api";

function Pager({ current, total }: { current: number; total: number }) {
  const { lang } = useLang();
  const pages = Array.from({ length: total }, (_, i) => i + 1);
  const href = (n: number) => (n === 1 ? "/blog" : `/blog?page=${n}`);
  return (
    <div className="pager" role="navigation" aria-label={lang === "en" ? "Pagination" : "分頁"}>
      {current <= 1 ? (
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
      {current >= total ? (
        <span className="disabled arrow">→</span>
      ) : (
        <Link className="arrow" href={href(current + 1)} aria-label="Next">→</Link>
      )}
    </div>
  );
}

export default function BlogView({
  items,
  current,
  total,
}: {
  items: PostCard[];
  current: number;
  total: number;
}) {
  const { lang } = useLang();
  const t = <T,>(en: T, zh: T) => (lang === "en" ? en : zh);
  const locale = lang === "en" ? "en-US" : "zh-TW";

  const fmtDate = (iso: string | null) => {
    if (!iso) return { day: "", year: "" };
    const d = new Date(iso);
    return {
      day: d.toLocaleDateString(locale, { month: "short", day: "numeric" }),
      year: String(d.getFullYear()),
    };
  };

  return (
    <>
      <div className="bl-head">
        <div className="bl-eyebrow">{t("Writing", "文章")}</div>
        <h1>{t("Blog", "部落格")}</h1>
      </div>

      <div className="bl-feed">
        {items.map((p) => {
          const { day, year } = fmtDate(p.published_at);
          return (
            <Link className="bl-post" href={`/blog/${p.slug}`} key={p.id}>
              <div className="bl-rail">
                <div className="bl-d">{day}</div>
                <div className="bl-y">{year}</div>
                <div className="bl-rt">
                  {p.reading_minutes} {t("min", "分鐘")}
                </div>
              </div>
              <div>
                <h2 className="bl-title">{t(p.title_en, p.title_zh)}</h2>
                <p className="bl-ex">{t(p.excerpt_en, p.excerpt_zh)}</p>
                <div className="bl-tags">
                  {p.tags.map((tag) => (
                    <span key={tag}>{tag}</span>
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
