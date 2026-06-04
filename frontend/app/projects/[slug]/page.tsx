import type { Metadata } from "next";
import { notFound } from "next/navigation";

import Header from "@/components/Header";
import ProjectDetailView from "@/components/ProjectDetailView";
import { getProject } from "@/lib/api";

export const revalidate = 300;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const p = await getProject(slug);
  if (!p) return { title: "Project not found" };

  const title = p.meta_title_en || p.title_en;
  const description = p.meta_description_en || p.summary_en;
  const image = p.og_image || p.cover_image || undefined;

  return {
    title: `${title} — Tsai Cheng-Hung`,
    description,
    openGraph: { title, description, images: image ? [image] : undefined },
  };
}

export default async function ProjectPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProject(slug);
  if (!project) notFound();

  return (
    <>
      <Header />
      <ProjectDetailView project={project} />
    </>
  );
}
