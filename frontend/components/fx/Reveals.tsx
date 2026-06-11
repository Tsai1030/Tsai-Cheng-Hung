"use client";

import { useEffect } from "react";

/**
 * Global scroll-reveal driver: any element with [data-reveal] gets `.in`
 * when it enters the viewport. Watches the DOM so route changes and
 * client-rendered content are picked up automatically.
 */
export default function Reveals() {
  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }
    );

    const scan = () => {
      document.querySelectorAll("[data-reveal]:not(.in)").forEach((el) => io.observe(el));
    };
    scan();

    const mo = new MutationObserver(scan);
    mo.observe(document.body, { childList: true, subtree: true });

    return () => {
      mo.disconnect();
      io.disconnect();
    };
  }, []);

  return null;
}
