"use client";

import Link from "next/link";
import { L } from "@/components/LangContext";

export default function ProjectsPage() {
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "60px 24px", textAlign: "center" }}>
      <div>
        <div style={{ fontSize: ".8rem", letterSpacing: ".32em", textTransform: "uppercase", color: "var(--deep)", marginBottom: "22px" }}>
          <L en="Projects" zh="專案" />
        </div>
        <h1 style={{ fontFamily: "var(--serif)", fontSize: "clamp(2.6rem, 8vw, 5.5rem)", fontWeight: 500, lineHeight: 1 }}>
          <L en="Coming soon." zh="即將推出。" />
        </h1>
        <p style={{ marginTop: "18px", fontSize: "1.05rem" }}>
          <L en="Detailed project write-ups are on the way." zh="完整的專案介紹即將上線。" />
        </p>
        <Link
          href="/"
          style={{ display: "inline-block", marginTop: "34px", color: "var(--deep)", textDecoration: "none", borderBottom: "1px solid var(--deep)", paddingBottom: "3px" }}
        >
          <L en="← Back home" zh="← 返回首頁" />
        </Link>
      </div>
    </main>
  );
}
