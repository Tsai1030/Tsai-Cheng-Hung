"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

/**
 * Fixed HUD chrome around the viewport: blueprint grid + noise backdrop,
 * side rails with coordinates, live scroll readout, corner ticks.
 */
export default function Chrome() {
  const pctRef = useRef<HTMLSpanElement>(null);
  const barRef = useRef<HTMLSpanElement>(null);
  const pathname = usePathname();

  useEffect(() => {
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const p = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
      if (pctRef.current) pctRef.current.textContent = String(Math.round(p * 100)).padStart(3, "0");
      if (barRef.current) barRef.current.style.height = `${p * 100}%`;
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, [pathname]);

  return (
    <>
      <div className="bg-grid" aria-hidden="true" />
      <div className="bg-noise" aria-hidden="true" />
      <div className="rail rail-l" aria-hidden="true">
        <span className="rail-txt">TSAI.SYS — PORTFOLIO // 2026</span>
      </div>
      <div className="rail rail-r" aria-hidden="true">
        <span className="rail-meter">
          <span className="rail-bar" ref={barRef} />
        </span>
        <span className="rail-pct">
          SCR_<span ref={pctRef}>000</span>%
        </span>
      </div>
      <div className="corner c-tl" aria-hidden="true" />
      <div className="corner c-tr" aria-hidden="true" />
      <div className="corner c-bl" aria-hidden="true" />
      <div className="corner c-br" aria-hidden="true" />
    </>
  );
}
