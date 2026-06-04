import Header from "@/components/Header";
import Hero from "@/components/Hero";
import CareerSlices from "@/components/CareerSlices";
import { About, Experience, Skills, Projects, Publication, Footer } from "@/components/Sections";
import { getProjectsSafe } from "@/lib/api";

export const revalidate = 300;

export default async function Page() {
  const all = await getProjectsSafe();
  const featured = all.filter((p) => p.featured).slice(0, 4);

  return (
    <>
      <Header />
      <Hero />
      <About />
      <CareerSlices />
      <Experience />
      <Skills />
      <Projects projects={featured} />
      <Publication />
      <Footer />
    </>
  );
}
