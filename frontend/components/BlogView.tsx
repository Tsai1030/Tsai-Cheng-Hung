"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useLang } from "./LangContext";
import { Pager } from "./ProjectsView";
import LikeButton from "./LikeButton";
import { EyeIcon } from "./icons";
import type { PostCard } from "@/lib/api";

export default function BlogView({
  items,
  current,
  total,
  variant = "blog",
}: {
  items: PostCard[];
  current: number;
  total: number;
  /** "blog" = main feed, "daily" = AI daily reports feed */
  variant?: "blog" | "daily";
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

  const isDaily = variant === "daily";
  const base = isDaily ? "/blog/daily" : "/blog";

  return (
    <main className="page">
      <div className="page-head">
        <div className="page-eyebrow" data-reveal>
          LOG — {isDaily ? t("AI DAILY", "AI 日報") : t("WRITING", "文章")}
        </div>
        <h1 data-reveal>{isDaily ? t("AI DAILY", "AI 日報") : t("BLOG", "部落格")}</h1>
        <p className="page-sub" data-reveal>
          {isDaily
            ? t(
                "Automated daily digest of AI news and LLM research.",
                "每日自動彙整的 AI 新聞與 LLM 技術研究報告。"
              )
            : t("Notes on RAG, agents, and building AI products.", "關於 RAG、Agent 與打造 AI 產品的筆記。")}
        </p>
        <div className="bl-tabs" data-reveal>
          <Link href="/blog" className={isDaily ? "" : "active"} data-hover>
            {t("ARTICLES", "文章")}
          </Link>
          <Link href="/blog/daily" className={isDaily ? "active" : ""} data-hover>
            {t("AI DAILY", "AI 日報")}
          </Link>
        </div>
      </div>

      <div className="bl-feed">
        {items.map((p, i) => {
          const { day, year } = fmtDate(p.published_at);
          return (
            <Link
              className="bl-post"
              href={`/blog/${p.slug}`}
              key={p.id}
              data-reveal
              data-hover
              style={{ "--d": `${i * 0.05}s` } as CSSProperties}
            >
              <div className="bl-rail">
                <div className="bl-d">{day}</div>
                <div className="bl-y">{year}</div>
                <div className="bl-rt">
                  ⊙ {p.reading_minutes} {t("MIN", "分鐘")}
                </div>
              </div>
              <div className="bl-main">
                <h2 className="bl-title">{t(p.title_en, p.title_zh)}</h2>
                <p className="bl-ex">{t(p.excerpt_en, p.excerpt_zh)}</p>
                <div className="bl-tags">
                  {p.tags.map((tag) => (
                    <span key={tag}>#{tag}</span>
                  ))}
                </div>
                <div className="bl-like">
                  <span className="view-count" aria-label={t("Views", "瀏覽次數")}>
                    <EyeIcon />
                    {p.views}
                  </span>
                  <LikeButton kind="post" id={p.id} initial={p.likes} />
                </div>
              </div>
              <span className="bl-arrow" aria-hidden="true">→</span>
            </Link>
          );
        })}
      </div>

      <Pager current={current} total={total} base={base} />
    </main>
  );
}
