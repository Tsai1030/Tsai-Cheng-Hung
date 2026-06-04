"use client";

import { createContext, useContext, useEffect, useState, type ReactNode, type ElementType } from "react";

export type Lang = "en" | "zh";

const LangCtx = createContext<{ lang: Lang; toggle: () => void }>({
  lang: "en",
  toggle: () => {},
});

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");

  // restore saved preference after mount (keeps SSR markup = "en", no hydration mismatch)
  useEffect(() => {
    const saved = localStorage.getItem("lang") as Lang | null;
    if (saved === "en" || saved === "zh") setLang(saved);
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang === "en" ? "en" : "zh-Hant";
    document.documentElement.dataset.lang = lang;
  }, [lang]);

  const toggle = () =>
    setLang((prev) => {
      const next = prev === "en" ? "zh" : "en";
      localStorage.setItem("lang", next);
      return next;
    });

  return <LangCtx.Provider value={{ lang, toggle }}>{children}</LangCtx.Provider>;
}

export const useLang = () => useContext(LangCtx);

/** Plain bilingual text node. */
export function L({ en, zh }: { en: string; zh: string }) {
  const { lang } = useLang();
  return <>{lang === "en" ? en : zh}</>;
}

/** Bilingual text that may contain inline HTML (<b>, <br>, <span>, <i>). */
export function Rich({
  en,
  zh,
  as: Tag = "span",
  ...rest
}: { en: string; zh: string; as?: ElementType } & Record<string, any>) {
  const { lang } = useLang();
  return <Tag {...rest} dangerouslySetInnerHTML={{ __html: lang === "en" ? en : zh }} />;
}
