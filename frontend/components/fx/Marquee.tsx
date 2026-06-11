"use client";

/** Infinite scrolling ticker. Duplicated track for a seamless CSS loop. */
export default function Marquee({ items }: { items: string[] }) {
  const row = items.map((it, i) => (
    <span className="mq-item" key={i}>
      {it}
      <span className="mq-sep">◇</span>
    </span>
  ));
  return (
    <div className="mq" aria-hidden="true">
      <div className="mq-track">
        {row}
        {row}
      </div>
    </div>
  );
}
