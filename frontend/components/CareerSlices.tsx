"use client";

import { useEffect, useRef } from "react";
import Image from "next/image";
import { L } from "./LangContext";

type Bi = { en: string; zh: string };
type Card = { img: string; badge: Bi; role: Bi; org: Bi | string; desc: Bi; pos?: string };

const cards: Card[] = [
  {
    img: "/life.jpg",
    pos: "left 25%",
    badge: { en: "Profile", zh: "個人" },
    role: { en: "Portrait", zh: "個人照片" },
    org: "蔡承紘 · Tsai Cheng-Hung",
    desc: { en: "My journey, left → right.", zh: "我的歷程，由左至右。" },
  },
  {
    img: "/healthcare%20administration.png",
    badge: { en: "Undergraduate", zh: "大學" },
    role: { en: "Healthcare Administration", zh: "醫務管理學系" },
    org: { en: "I-Shou University", zh: "義守大學" },
    desc: { en: "Where my healthcare foundation began.", zh: "醫務管理的起點。" },
  },
  {
    img: "/Healthcare%20Quality%20Intern.png",
    badge: { en: "Internship", zh: "實習" },
    role: { en: "Healthcare Quality Intern", zh: "醫療品質實習" },
    org: { en: "National Defense Medical Center", zh: "國防醫學院" },
    desc: { en: "Exposure to hospital quality & process.", zh: "接觸醫療品質與流程管理。" },
  },
  {
    img: "/Preventive%20Medicine%20Admin.png",
    badge: { en: "Hospital", zh: "醫院" },
    role: { en: "Preventive Medicine Admin", zh: "預防醫學科 行政" },
    org: { en: "E-Da Hospital", zh: "義大醫院" },
    desc: { en: "Records, tracking & health-check reports.", zh: "病歷、追蹤與體檢報告。" },
  },
  {
    img: "/Master's%20Researcher.png",
    badge: { en: "Master's", zh: "碩士" },
    role: { en: "Master's Researcher", zh: "碩士研究生" },
    org: { en: "Medical Informatics · KMU", zh: "醫療資訊學系 · 高雄醫學大學" },
    desc: { en: "Built & deployed a RAG thesis system.", zh: "打造並部署 RAG 論文系統。" },
  },
  {
    img: "/Assistant%20TA.png",
    badge: { en: "Teaching", zh: "教學" },
    role: { en: "Assistant TA", zh: "助理助教" },
    org: { en: "Taiwan AI Course Alliance", zh: "臺灣大專院校 AI 學程聯盟" },
    desc: { en: "Guided ~100 students in generative AI.", zh: "指導約 100 位學生的生成式 AI。" },
  },
  {
    img: "/RAG%20Engineer%20(Intern).png",
    badge: { en: "Internship", zh: "實習" },
    role: { en: "RAG Engineer (Intern)", zh: "RAG 工程師（實習）" },
    org: "學思行數位行銷",
    desc: { en: "Agent flows, RAG & full-stack product.", zh: "Agent flow、RAG 與全端產品。" },
  },
  {
    img: "/AI%20Application%20Engineer.png",
    badge: { en: "Current", zh: "現職" },
    role: { en: "AI Application Engineer", zh: "AI 應用工程師" },
    org: "中華工程 / BES",
    desc: { en: "Production RAG systems, agents & automation.", zh: "產品級 RAG 系統、Agent 與自動化。" },
  },
];

export default function CareerSlices() {
  const pinRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const fillRef = useRef<HTMLSpanElement>(null);
  const pctRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const pin = pinRef.current;
    const track = trackRef.current;
    if (!pin || !track) return;

    const horiz = () => {
      // mobile: native swipe — don't drive the track with scroll position
      if (window.matchMedia("(max-width: 880px)").matches) {
        track.style.transform = "";
        return;
      }
      const total = pin.offsetHeight - window.innerHeight;
      if (total <= 0) return;
      const prog = Math.min(Math.max(-pin.getBoundingClientRect().top / total, 0), 1);
      const max = Math.max(0, track.scrollWidth - window.innerWidth + 48);
      track.style.transform = `translateX(${-prog * max}px)`;
      if (fillRef.current) fillRef.current.style.width = `${prog * 100}%`;
      if (pctRef.current)
        pctRef.current.textContent = String(Math.round(prog * 100)).padStart(3, "0");
    };

    window.addEventListener("scroll", horiz, { passive: true });
    window.addEventListener("resize", horiz);
    horiz();
    return () => {
      window.removeEventListener("scroll", horiz);
      window.removeEventListener("resize", horiz);
    };
  }, []);

  return (
    <section id="career" className="cr-section">
      <div className="cr-pin" ref={pinRef}>
        <div className="cr-sticky">
          <div className="cr-head">
            <div className="left">
              <div className="idx" data-reveal>SYS/02</div>
              <h2 data-reveal><L en="Career Slices" zh="職涯切片" /></h2>
            </div>
            <p className="sub" data-reveal>
              <L
                en="A horizontal look back at every role I've worn — from hospital floors to AI engineering."
                zh="橫向回顧我扮演過的每個身分——從醫院現場到 AI 工程。"
              />
            </p>
          </div>
          <div className="cr-track" ref={trackRef}>
            {cards.map((c, i) => (
              <article className="cr-card" key={i} data-hover>
                <span className="cr-no">{String(i + 1).padStart(2, "0")} / {String(cards.length).padStart(2, "0")}</span>
                <div className="ph">
                  <Image
                    src={c.img}
                    alt=""
                    fill
                    sizes="(max-width: 880px) 80vw, 420px"
                    style={{ objectFit: "cover", objectPosition: c.pos }}
                  />
                  <span className="badge"><L {...c.badge} /></span>
                  <div className="role">
                    <h3><L {...c.role} /></h3>
                    <div className="org">{typeof c.org === "string" ? c.org : <L {...c.org} />}</div>
                  </div>
                </div>
                <p className="desc"><L {...c.desc} /></p>
              </article>
            ))}
          </div>
          <div className="cr-hud">
            <span className="cr-note"><L en="SCROLL ↓ — TRACK SLIDES →" zh="向下捲動 ↓ — 卡片橫向滑動 →" /></span>
            <span className="cr-meter"><span className="cr-fill" ref={fillRef} /></span>
            <span className="cr-pct">TRK_<span ref={pctRef}>000</span>%</span>
          </div>
        </div>
      </div>
    </section>
  );
}
