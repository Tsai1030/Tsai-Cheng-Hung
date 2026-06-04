"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLang } from "./LangContext";
import type { PostDetail } from "@/lib/api";

export default function PostDetailView({ post: p }: { post: PostDetail }) {
  const { lang } = useLang();
  const t = <T,>(en: T, zh: T) => (lang === "en" ? en : zh);
  const locale = lang === "en" ? "en-US" : "zh-TW";

  const date = p.published_at
    ? new Date(p.published_at).toLocaleDateString(locale, {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : "";

  return (
    <div className="pd-wrap">
      <Link className="pd-back" href="/blog">← {t("All posts", "所有文章")}</Link>

      <div className="pd-eyebrow">
        {date}
        {date ? " · " : ""}
        {p.reading_minutes} {t("min read", "分鐘閱讀")}
      </div>
      <h1>{t(p.title_en, p.title_zh)}</h1>
      <p className="pd-summary">{t(p.excerpt_en, p.excerpt_zh)}</p>

      {p.tags.length > 0 && (
        <div className="pd-chips">
          {p.tags.map((tag) => (
            <span key={tag}>{tag}</span>
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
