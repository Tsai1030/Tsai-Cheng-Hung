"use client";

import { useEffect, useState } from "react";
import type { KeyboardEvent, MouseEvent } from "react";
import { likePost, likeProject, unlikePost, unlikeProject } from "@/lib/api";

type Kind = "project" | "post";

// Rendered as a <span role="button"> (not <button>) because each card is wrapped
// in a Next <Link> (<a>), and interactive content nested in <a> is invalid HTML.
export default function LikeButton({
  kind,
  id,
  initial,
}: {
  kind: Kind;
  id: number;
  initial: number;
}) {
  const [count, setCount] = useState(initial);
  const [liked, setLiked] = useState(false);
  const [busy, setBusy] = useState(false);

  const key = `like:${kind}:${id}`;

  // Read localStorage after mount to avoid SSR/CSR hydration mismatch.
  useEffect(() => {
    setLiked(localStorage.getItem(key) === "1");
  }, [key]);

  async function toggle() {
    if (busy) return;
    setBusy(true);

    const nextLiked = !liked;
    const like = kind === "project" ? likeProject : likePost;
    const unlike = kind === "project" ? unlikeProject : unlikePost;

    // Optimistic update.
    setLiked(nextLiked);
    setCount((c) => c + (nextLiked ? 1 : -1));

    try {
      const likes = await (nextLiked ? like(id) : unlike(id));
      setCount(likes);
      if (nextLiked) localStorage.setItem(key, "1");
      else localStorage.removeItem(key);
    } catch {
      // Revert on failure.
      setLiked(!nextLiked);
      setCount((c) => c - (nextLiked ? 1 : -1));
    } finally {
      setBusy(false);
    }
  }

  function onClick(e: MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    toggle();
  }

  function onKeyDown(e: KeyboardEvent) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      e.stopPropagation();
      toggle();
    }
  }

  return (
    <span
      role="button"
      tabIndex={0}
      aria-pressed={liked}
      aria-label={liked ? "Unlike" : "Like"}
      className={liked ? "like-btn liked" : "like-btn"}
      onClick={onClick}
      onKeyDown={onKeyDown}
    >
      <span aria-hidden="true">{liked ? "♥" : "♡"}</span>
      {count}
    </span>
  );
}
