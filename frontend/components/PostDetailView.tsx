"use client";

import Link from "next/link";
import Image from "next/image";
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
    <main className="page pd-wrap">
      <Link className="pd-back" href="/blog" data-hover>
        ← {t("ALL POSTS", "所有文章")}
      </Link>

      <div className="pd-eyebrow" data-reveal>
        LOG_ENTRY {date ? `· ${date}` : ""} · ⊙ {p.reading_minutes} {t("MIN READ", "分鐘閱讀")}
      </div>
      <h1 data-reveal>{t(p.title_en, p.title_zh)}</h1>
      <p className="pd-summary" data-reveal>{t(p.excerpt_en, p.excerpt_zh)}</p>

      {p.tags.length > 0 && (
        <div className="pd-chips" data-reveal>
          {p.tags.map((tag) => (
            <span key={tag}>#{tag}</span>
          ))}
        </div>
      )}

      {p.cover_image && (
        <div className="pd-cover" data-reveal>
          <Image src={p.cover_image} alt="" fill sizes="(max-width: 820px) 100vw, 880px" style={{ objectFit: "cover" }} />
        </div>
      )}

      <article className="pd-body">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{t(p.body_en, p.body_zh)}</ReactMarkdown>
      </article>
    </main>
  );
}
