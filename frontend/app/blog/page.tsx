import Header from "@/components/Header";
import BlogView from "@/components/BlogView";
import { getPosts } from "@/lib/api";

export const revalidate = 300;

const PAGE_SIZE = 6;

export const metadata = {
  title: "Blog — Tsai Cheng-Hung",
  description: "Notes on RAG, agents, and building AI products.",
};

export default async function BlogPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const sp = await searchParams;
  const all = await getPosts();

  const total = Math.max(1, Math.ceil(all.length / PAGE_SIZE));
  let page = Number.parseInt(sp.page ?? "1", 10);
  if (Number.isNaN(page) || page < 1) page = 1;
  if (page > total) page = total;

  const start = (page - 1) * PAGE_SIZE;
  const items = all.slice(start, start + PAGE_SIZE);

  return (
    <>
      <Header />
      <BlogView items={items} current={page} total={total} />
    </>
  );
}
