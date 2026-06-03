import Header from "@/components/Header";
import Hero from "@/components/Hero";
import CareerSlices from "@/components/CareerSlices";
import { About, Experience, Skills, Projects, Publication, Footer } from "@/components/Sections";

export default function Page() {
  return (
    <>
      <Header />
      <Hero />
      <About />
      <CareerSlices />
      <Experience />
      <Skills />
      <Projects />
      <Publication />
      <Footer />
    </>
  );
}
