"use client";

import { L, Rich } from "./LangContext";

export default function Hero() {
  return (
    <div className="hero">
      <div className="hero-text">
        <div className="eyebrow">
          <L en="AI Application Engineer · Frontend Engineer" zh="AI 應用工程師 · 全端工程師" />
        </div>
        <Rich
          as="h1"
          en="Tsai<br><span class='last'>Cheng-Hung</span>"
          zh="蔡<br><span class='last'>承紘</span>"
        />
        <div className="altname"><L en="蔡承紘" zh="Tsai Cheng-Hung" /></div>
        <Rich
          as="p"
          className="role"
          en="I build AI that speaks human — <b>RAG systems, autonomous agents, and the interfaces that make them effortless</b>."
          zh="我打造能與人對話的 AI——<b>RAG 系統、自主代理，以及讓它們毫不費力的前端介面</b>。"
        />
        <div className="hero-meta">
          <div>
            <span><L en="Based in" zh="所在地" /></span>
            <span className="val"><L en="Kaohsiung / Taipei, TW" zh="台灣 高雄 / 台北" /></span>
          </div>
          <div>
            <span><L en="Education" zh="學歷" /></span>
            <span className="val"><L en="M.S. Medical Informatics (AI)" zh="醫療資訊碩士（AI 組）" /></span>
          </div>
          <div>
            <span><L en="Currently" zh="現職" /></span>
            <span className="val"><L en="AI Engineer @ BES" zh="中華工程 AI 工程師" /></span>
          </div>
        </div>
      </div>
      <div className="photo-card">
        <span className="tape"><L en="Portrait" zh="個人照" /></span>
        <div className="frame">
          <img src="/about.jpg" alt="Tsai Cheng-Hung" />
          <div className="cap">
            <span>Tsai Cheng-Hung</span>
            <span>2026</span>
          </div>
        </div>
      </div>
    </div>
  );
}
