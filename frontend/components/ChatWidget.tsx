"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLang } from "./LangContext";
import { API_BASE } from "@/lib/api";

type Source = { title: string; url: string };
type ChatMsg = { role: "user" | "assistant"; content: string; sources?: Source[] };

const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));
const TYPE_DELAY = 14; // ms per tick
const TYPE_CHARS = 2; // chars revealed per tick

export default function ChatWidget() {
  const { lang } = useLang();
  const router = useRouter();
  const t = <T,>(en: T, zh: T) => (lang === "en" ? en : zh);

  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const msgsRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // typewriter buffers
  const queueRef = useRef(""); // received-but-not-yet-shown text
  const doneRef = useRef(true); // stream finished?
  const sourcesRef = useRef<Source[] | null>(null);

  useEffect(() => {
    msgsRef.current?.scrollTo({ top: msgsRef.current.scrollHeight });
  }, [messages, open]);

  const go = (href: string) => {
    setOpen(false);
    router.push(href);
  };

  const patchLast = (fn: (m: ChatMsg) => ChatMsg) =>
    setMessages((ms) => ms.map((m, i) => (i === ms.length - 1 ? fn(m) : m)));

  // Reveal queued text one slice at a time, decoupled from network chunks.
  async function typewriter() {
    while (!doneRef.current || queueRef.current.length) {
      if (queueRef.current.length) {
        const take = queueRef.current.slice(0, TYPE_CHARS);
        queueRef.current = queueRef.current.slice(TYPE_CHARS);
        patchLast((m) => ({ ...m, content: m.content + take }));
      }
      await sleep(TYPE_DELAY);
    }
    if (sourcesRef.current) {
      const s = sourcesRef.current;
      patchLast((m) => ({ ...m, sources: s }));
    }
  }

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    const history = [...messages, { role: "user" as const, content: text }];
    setMessages([...history, { role: "assistant", content: "" }]);
    setInput("");
    if (inputRef.current) inputRef.current.style.height = "auto";
    setBusy(true);

    queueRef.current = "";
    sourcesRef.current = null;
    doneRef.current = false;
    const typing = typewriter();

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: history.map((m) => ({ role: m.role, content: m.content })),
          lang,
        }),
      });
      if (!res.body) throw new Error("no stream");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const blocks = buffer.split("\n\n");
        buffer = blocks.pop() ?? "";
        for (const block of blocks) {
          let ev = "";
          let data = "";
          for (const line of block.split("\n")) {
            if (line.startsWith("event:")) ev = line.slice(6).trim();
            else if (line.startsWith("data:")) data += line.slice(5).trim();
          }
          if (!data) continue;
          if (ev === "token") queueRef.current += JSON.parse(data).t;
          else if (ev === "sources") sourcesRef.current = JSON.parse(data).sources;
          else if (ev === "error") queueRef.current += `\n\n_${JSON.parse(data).message}_`;
        }
      }
    } catch {
      queueRef.current += t("Sorry, something went wrong.", "抱歉，發生了一點問題。");
    } finally {
      doneRef.current = true;
      await typing;
      setBusy(false);
    }
  }

  const mdComponents = {
    a: ({ href, children }: { href?: string; children?: React.ReactNode }) =>
      href && href.startsWith("/") ? (
        <a
          href={href}
          onClick={(e) => {
            e.preventDefault();
            go(href);
          }}
        >
          {children}
        </a>
      ) : (
        <a href={href} target="_blank" rel="noopener noreferrer">
          {children}
        </a>
      ),
  };

  return (
    <>
      <button
        className="chat-fab"
        aria-label={t("Open chat", "開啟聊天")}
        onClick={() => setOpen((o) => !o)}
      >
        {open ? "✕" : t("Ask", "問我")}
      </button>

      {open && (
        <div className="chat-panel" role="dialog" aria-label={t("Chat assistant", "聊天助手")}>
          <div className="chat-head">
            <div>
              <strong>{t("Ask about me", "問問關於我")}</strong>
              <span>{t("Projects · blog · background", "專案 · 部落格 · 背景")}</span>
            </div>
            <button className="chat-x" aria-label={t("Close", "關閉")} onClick={() => setOpen(false)}>✕</button>
          </div>

          <div className="chat-msgs" ref={msgsRef}>
            {messages.length === 0 && (
              <div className="chat-intro">
                {t(
                  "Hi! I'm Tsai's assistant. Ask me about his projects, blog, or background — I'll point you to the right page.",
                  "嗨！我是蔡承紘的小助手。問我關於他的專案、部落格或背景，我會幫你帶到對應頁面。"
                )}
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>
                {m.role === "assistant" ? (
                  <div className="chat-md">
                    {m.content ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                        {m.content}
                      </ReactMarkdown>
                    ) : (
                      <span className="chat-typing">···</span>
                    )}
                    {m.sources && m.sources.length > 0 && (
                      <div className="chat-sources">
                        <span>{t("Sources", "來源")}</span>
                        {m.sources.map((s) => (
                          <a
                            key={s.url}
                            href={s.url}
                            onClick={(e) => {
                              e.preventDefault();
                              go(s.url);
                            }}
                          >
                            {s.title}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  m.content
                )}
              </div>
            ))}
          </div>

          <form
            className="chat-input"
            onSubmit={(e) => {
              e.preventDefault();
              send();
            }}
          >
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = `${el.scrollHeight}px`;
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              placeholder={t("Ask a question…", "輸入問題…")}
              disabled={busy}
            />
            <button type="submit" disabled={busy || !input.trim()}>
              {t("Send", "送出")}
            </button>
          </form>
        </div>
      )}
    </>
  );
}
