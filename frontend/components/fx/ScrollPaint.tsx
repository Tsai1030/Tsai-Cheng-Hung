"use client";

import { useEffect, useRef, type ReactNode } from "react";

/**
 * Scroll-driven text staining: a hard-edged vertical gradient (set via the
 * --fp CSS var) sweeps down the block as it crosses the viewport, so lines
 * are "painted" one by one. Pair with the `.paint` class in globals.css.
 */
export default function ScrollPaint({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      el.style.setProperty("--fp", "100%");
      return;
    }

    let raf = 0;
    const update = () => {
      raf = 0;
      const r = el.getBoundingClientRect();
      const vh = window.innerHeight;
      const start = vh * 0.88; // painting begins when the top crosses here
      const end = vh * 0.38; // fully painted once the bottom crosses here
      const p = Math.min(Math.max((start - r.top) / (r.height + start - end), 0), 1);
      el.style.setProperty("--fp", `${(p * 100).toFixed(2)}%`);
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <div ref={ref} className={`paint${className ? ` ${className}` : ""}`}>
      {children}
    </div>
  );
}
