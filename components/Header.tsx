"use client";

import { useEffect, useState } from "react";
import { useLang, L } from "./LangContext";

export default function Header() {
  const { lang, toggle } = useLang();
  const [collapsed, setCollapsed] = useState(false);
  const [shrink, setShrink] = useState(false);

  useEffect(() => {
    let lastY = 0;
    const onScroll = () => {
      const y = window.scrollY;
      setShrink(y > 40);
      setCollapsed(y > lastY && y > 160);
      lastY = y;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const cls = [collapsed ? "collapsed" : "", shrink ? "shrink" : ""].join(" ").trim();

  return (
    <header className={cls}>
      <div className="bar">
        <div className="brand">
          Tsai <span>Cheng-Hung</span>
        </div>
        <nav>
          <a href="#about"><L en="About" zh="關於" /></a>
          <a href="#career"><L en="Career" zh="職涯" /></a>
          <a href="#projects"><L en="Projects" zh="專案" /></a>
          <a href="#" className="disabled"><L en="Blog" zh="部落格" /></a>
          <button className="lang" onClick={toggle}>{lang === "en" ? "中文" : "EN"}</button>
        </nav>
      </div>
    </header>
  );
}
