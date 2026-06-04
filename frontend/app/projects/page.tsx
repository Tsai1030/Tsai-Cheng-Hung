import Header from "@/components/Header";
import ProjectsView from "@/components/ProjectsView";
import { getProjects } from "@/lib/api";

export const revalidate = 300;

const PAGE_SIZE = 6;

export const metadata = {
  title: "Projects — Tsai Cheng-Hung",
  description: "Selected work — RAG systems, autonomous agents, and fully local knowledge bases.",
};

export default async function ProjectsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const sp = await searchParams;
  const all = await getProjects();

  const total = Math.max(1, Math.ceil(all.length / PAGE_SIZE));
  let page = Number.parseInt(sp.page ?? "1", 10);
  if (Number.isNaN(page) || page < 1) page = 1;
  if (page > total) page = total;

  const start = (page - 1) * PAGE_SIZE;
  const items = all.slice(start, start + PAGE_SIZE);

  return (
    <>
      <Header />
      <ProjectsView items={items} startIndex={start} current={page} total={total} />
    </>
  );
}
