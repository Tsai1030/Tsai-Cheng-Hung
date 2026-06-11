import Header from "@/components/Header";
import Hero from "@/components/Hero";
import CareerSlices from "@/components/CareerSlices";
import Marquee from "@/components/fx/Marquee";
import { About, Experience, Skills, Projects, Publication, Footer } from "@/components/Sections";
import { getProjectsSafe } from "@/lib/api";

export const revalidate = 300;

const TICKER = [
  "RAG SYSTEMS",
  "LANGGRAPH",
  "AGENTIC WORKFLOW",
  "NEXT.JS",
  "FASTAPI",
  "THREE.JS",
  "PYTORCH",
  "TYPESCRIPT",
  "PGVECTOR",
  "PROMPT ENGINEERING",
];

export default async function Page() {
  const all = await getProjectsSafe();
  const featured = all.filter((p) => p.featured).slice(0, 4);

  return (
    <>
      <Header />
      <main>
        <Hero />
        <Marquee items={TICKER} />
        <About />
        <CareerSlices />
        <Experience />
        <Skills />
        <Projects projects={featured} />
        <Publication />
        <Footer />
      </main>
    </>
  );
}
