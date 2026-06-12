import type { Metadata, Viewport } from "next";
import { Syne, Space_Grotesk, JetBrains_Mono, Noto_Sans_TC } from "next/font/google";
import "./globals.css";
import { LangProvider } from "@/components/LangContext";
import ChatWidget from "@/components/ChatWidget";
import Chrome from "@/components/fx/Chrome";
import Cursor from "@/components/fx/Cursor";
import Reveals from "@/components/fx/Reveals";

const display = Syne({
  subsets: ["latin"],
  weight: ["500", "600", "700", "800"],
  variable: "--font-display",
  display: "swap",
});

const body = Space_Grotesk({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-body",
  display: "swap",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-mono",
  display: "swap",
});

const tc = Noto_Sans_TC({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-tc",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Tsai Cheng-Hung — AI Application & Full-Stack Engineer",
  description:
    "Tsai Cheng-Hung (蔡承紘) — AI Application & Full-Stack Engineer. RAG systems, agentic workflows, and the interfaces that bring them to life.",
  icons: {
    icon: [{ url: "/favicon.ico?v=20260604", type: "image/x-icon" }],
    shortcut: [{ url: "/favicon.ico?v=20260604", type: "image/x-icon" }],
  },
};

export const viewport: Viewport = {
  themeColor: "#04060b",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      data-lang="en"
      className={`${display.variable} ${body.variable} ${mono.variable} ${tc.variable}`}
    >
      <body>
        <LangProvider>
          <Chrome />
          {children}
          <ChatWidget />
          <Cursor />
          <Reveals />
        </LangProvider>
      </body>
    </html>
  );
}
