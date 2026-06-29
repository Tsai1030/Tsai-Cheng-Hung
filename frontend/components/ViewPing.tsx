"use client";

import { useEffect } from "react";
import { viewPost, viewProject } from "@/lib/api";

type Kind = "project" | "post";

// Mounted on the detail page. Increments the shared view counter once per
// browser session (sessionStorage dedup avoids inflating on refresh), then
// renders nothing — the count is displayed on the list cards, not here.
export default function ViewPing({ kind, id }: { kind: Kind; id: number }) {
  useEffect(() => {
    const key = `view:${kind}:${id}`;
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, "1");
    const view = kind === "project" ? viewProject : viewPost;
    view(id).catch(() => sessionStorage.removeItem(key));
  }, [kind, id]);

  return null;
}
