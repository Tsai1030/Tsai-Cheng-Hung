"use client";

import { useEffect, useRef } from "react";

/** Crosshair cursor: dot follows instantly, ring lerps behind. Desktop only. */
export default function Cursor() {
  const dotRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!window.matchMedia("(pointer: fine)").matches) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const dot = dotRef.current;
    const ring = ringRef.current;
    if (!dot || !ring) return;
    document.documentElement.classList.add("has-cursor");

    let x = -100;
    let y = -100;
    let rx = -100;
    let ry = -100;

    const onMove = (e: MouseEvent) => {
      x = e.clientX;
      y = e.clientY;
      dot.style.transform = `translate(${x}px, ${y}px)`;
    };

    const onOver = (e: MouseEvent) => {
      const hot = (e.target as Element | null)?.closest?.("a, button, [data-hover]");
      ring.classList.toggle("hot", Boolean(hot));
    };

    let raf = 0;
    const loop = () => {
      raf = requestAnimationFrame(loop);
      rx += (x - rx) * 0.16;
      ry += (y - ry) * 0.16;
      ring.style.transform = `translate(${rx}px, ${ry}px)`;
    };
    loop();

    window.addEventListener("mousemove", onMove, { passive: true });
    window.addEventListener("mouseover", onOver, { passive: true });
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseover", onOver);
      document.documentElement.classList.remove("has-cursor");
    };
  }, []);

  return (
    <>
      <div ref={dotRef} className="cur-dot" aria-hidden="true" />
      <div ref={ringRef} className="cur-ring" aria-hidden="true" />
    </>
  );
}
