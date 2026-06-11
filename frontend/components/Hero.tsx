"use client";

import { useCallback, useRef } from "react";
import dynamic from "next/dynamic";
import { L, useLang } from "./LangContext";
import Decode from "./fx/Decode";

const AssemblyScene = dynamic(() => import("./fx/AssemblyScene"), { ssr: false });

const PHASES = [
  { en: "BOOT // SCATTERED", zh: "BOOT // 元件離散" },
  { en: "LINK // ASSEMBLING", zh: "LINK // 組裝中" },
  { en: "CORE // ONLINE", zh: "CORE // 系統上線" },
];

export default function Hero() {
  const { lang } = useLang();
  const wrapRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const phaseRef = useRef<HTMLSpanElement>(null);
  const pctRef = useRef<HTMLSpanElement>(null);
  const barRef = useRef<HTMLSpanElement>(null);
  const langRef = useRef(lang);
  langRef.current = lang;

  // Driven by the 3D scene's rAF — write straight to the DOM, no re-renders.
  const onProgress = useCallback((p: number) => {
    const stage = stageRef.current;
    if (stage) stage.style.setProperty("--hp", p.toFixed(4));
    const idx = p < 0.4 ? 0 : p < 0.78 ? 1 : 2;
    const phase = PHASES[idx];
    if (phaseRef.current) {
      const txt = langRef.current === "en" ? phase.en : phase.zh;
      if (phaseRef.current.textContent !== txt) phaseRef.current.textContent = txt;
      phaseRef.current.dataset.idx = String(idx);
    }
    if (pctRef.current) pctRef.current.textContent = String(Math.round(p * 100)).padStart(3, "0");
    if (barRef.current) barRef.current.style.width = `${p * 100}%`;
  }, []);

  return (
    <section className="hero-pin" ref={wrapRef} id="top">
      <div className="hero-stage" ref={stageRef}>
        <AssemblyScene wrapRef={wrapRef} onProgress={onProgress} />

        <div className="hero-copy">
          <div className="hero-boot">
            <span className="prompt">$</span> whoami<span className="caret">▌</span>
          </div>
          <h1 className="hero-name">
            {lang === "en" ? (
              <>
                <Decode text="TSAI" delay={10} />
                <br />
                <span className="accent">
                  <Decode text="CHENG-HUNG" delay={26} />
                </span>
              </>
            ) : (
              <span className="accent">
                <Decode text="蔡承紘" delay={10} />
              </span>
            )}
          </h1>
          <div className="hero-alt">
            <L en="蔡承紘 — AI Application · Frontend Engineer" zh="Tsai Cheng-Hung — AI 應用 · 全端工程師" />
          </div>
          <p className="hero-role">
            <L
              en="I build AI that speaks human — RAG systems, autonomous agents, and the interfaces that make them effortless."
              zh="我打造能與人對話的 AI——RAG 系統、自主代理，以及讓它們毫不費力的前端介面。"
            />
          </p>
          <div className="hero-meta">
            <div>
              <span className="k"><L en="BASED_IN" zh="所在地" /></span>
              <span className="v"><L en="Kaohsiung / Taipei, TW" zh="台灣 高雄 / 台北" /></span>
            </div>
            <div>
              <span className="k"><L en="EDUCATION" zh="學歷" /></span>
              <span className="v"><L en="M.S. Medical Informatics (AI)" zh="醫療資訊碩士（AI 組）" /></span>
            </div>
            <div>
              <span className="k"><L en="CURRENTLY" zh="現職" /></span>
              <span className="v"><L en="AI Engineer @ BES" zh="中華工程 AI 工程師" /></span>
            </div>
          </div>
        </div>

        <div className="hero-final" aria-hidden="true">
          <div className="hf-line"><L en="SYSTEM ONLINE" zh="系統上線" /></div>
          <div className="hf-sub"><L en="Scroll to explore the build" zh="繼續往下探索" /></div>
        </div>

        <div className="hero-hud">
          <span className="hud-phase" ref={phaseRef} data-idx="0">
            BOOT // SCATTERED
          </span>
          <span className="hud-bar">
            <span className="hud-fill" ref={barRef} />
          </span>
          <span className="hud-pct">
            ASM_<span ref={pctRef}>000</span>%
          </span>
        </div>

        <div className="hero-scroll" aria-hidden="true">
          <L en="SCROLL TO ASSEMBLE" zh="向下捲動・開始組裝" />
          <span className="hero-scroll-line" />
        </div>
      </div>
    </section>
  );
}
