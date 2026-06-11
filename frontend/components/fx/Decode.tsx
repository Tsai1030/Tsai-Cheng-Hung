"use client";

import { useEffect, useRef } from "react";

const GLYPHS = "█▓▒░<>/\\_[]{}#%&*+=~";

/**
 * Text that "decodes" into place: characters scramble through glyphs and
 * settle left-to-right. Re-runs whenever `text` changes (e.g. lang toggle).
 */
export default function Decode({
  text,
  className,
  delay = 0,
}: {
  text: string;
  className?: string;
  delay?: number;
}) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      el.textContent = text;
      return;
    }

    const chars = Array.from(text);
    let frame = 0;
    let raf = 0;
    const settleAt = chars.map((_, i) => delay + i * 2 + 6);

    const tick = () => {
      frame++;
      let done = true;
      let out = "";
      for (let i = 0; i < chars.length; i++) {
        if (chars[i] === " ") {
          out += " ";
        } else if (frame >= settleAt[i]) {
          out += chars[i];
        } else if (frame >= delay) {
          out += GLYPHS[(frame * 7 + i * 13) % GLYPHS.length];
          done = false;
        } else {
          out += " ";
          done = false;
        }
      }
      el.textContent = out;
      if (!done) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [text, delay]);

  return (
    <span ref={ref} className={className}>
      {text}
    </span>
  );
}
