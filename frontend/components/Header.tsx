"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useLang, L } from "./LangContext";

export default function Header() {
  const { lang, toggle } = useLang();
  const [collapsed, setCollapsed] = useState(false);
  const [shrink, setShrink] = useState(false);
  const barRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    let lastY = 0;
    const onScroll = () => {
      const y = window.scrollY;
      setShrink(y > 40);
      setCollapsed(y > lastY && y > 200);
      lastY = y;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      if (barRef.current)
        barRef.current.style.width = `${max > 0 ? Math.min(y / max, 1) * 100 : 0}%`;
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const cls = [collapsed ? "collapsed" : "", shrink ? "shrink" : ""].join(" ").trim();

  return (
    <header className={cls}>
      <div className="bar">
        <Link href="/" className="brand">
          <span className="brand-sig">▚</span> TSAI<span className="brand-dim">_CHENG-HUNG</span>
          <span className="brand-cursor">▌</span>
        </Link>
        <nav>
          <a href="/#about">
            <i>01</i>
            <L en="About" zh="關於" />
          </a>
          <a href="/#career">
            <i>02</i>
            <L en="Career" zh="職涯" />
          </a>
          <Link href="/projects">
            <i>03</i>
            <L en="Projects" zh="專案" />
          </Link>
          <Link href="/blog">
            <i>04</i>
            <L en="Blog" zh="部落格" />
          </Link>
          <button className="lang" onClick={toggle}>
            [{lang === "en" ? "中文" : "EN"}]
          </button>
        </nav>
      </div>
      <span className="head-progress" ref={barRef} aria-hidden="true" />
    </header>
  );
}
