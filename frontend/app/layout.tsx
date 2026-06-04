import type { Metadata } from "next";
import { Cormorant_Garamond, Spectral } from "next/font/google";
import "./globals.css";
import { LangProvider } from "@/components/LangContext";
import ChatWidget from "@/components/ChatWidget";

const serif = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-serif",
  display: "swap",
});

const body = Spectral({
  subsets: ["latin"],
  weight: ["300", "400", "500"],
  style: ["normal", "italic"],
  variable: "--font-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Tsai Cheng-Hung — AI Application & Frontend Engineer",
  description:
    "Tsai Cheng-Hung (蔡承紘) — AI Application & Frontend Engineer. RAG systems, agentic workflows, and the interfaces that bring them to life.",
  icons: {
    icon: [{ url: "/favicon.ico?v=20260604", type: "image/x-icon" }],
    shortcut: [{ url: "/favicon.ico?v=20260604", type: "image/x-icon" }],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-lang="en" className={`${serif.variable} ${body.variable}`}>
      <body>
        <LangProvider>
          {children}
          <ChatWidget />
        </LangProvider>
      </body>
    </html>
  );
}
