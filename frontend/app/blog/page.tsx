import Header from "@/components/Header";
import BlogView from "@/components/BlogView";
import { getPosts, DAILY_TAG } from "@/lib/api";

export const revalidate = 300;

const PAGE_SIZE = 6;

export const metadata = {
  title: "Blog — Tsai Cheng-Hung",
  description: "Notes on RAG, agents, and building AI products.",
};

export default async function BlogPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; tag?: string }>;
}) {
  const sp = await searchParams;
  const all = await getPosts({ excludeTag: DAILY_TAG });

  // Topic dropdown options, derived from the posts themselves so new tags
  // show up automatically. Most-used first, then alphabetical.
  const counts = new Map<string, number>();
  for (const p of all) for (const t of p.tags) counts.set(t, (counts.get(t) ?? 0) + 1);
  const tags = [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([name]) => name);

  const tag = sp.tag && counts.has(sp.tag) ? sp.tag : undefined;
  const filtered = tag ? all.filter((p) => p.tags.includes(tag)) : all;

  const total = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  let page = Number.parseInt(sp.page ?? "1", 10);
  if (Number.isNaN(page) || page < 1) page = 1;
  if (page > total) page = total;

  const start = (page - 1) * PAGE_SIZE;
  const items = filtered.slice(start, start + PAGE_SIZE);

  return (
    <>
      <Header />
      <BlogView items={items} current={page} total={total} tags={tags} activeTag={tag} />
    </>
  );
}
