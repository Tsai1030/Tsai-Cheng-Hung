import Header from "@/components/Header";
import BlogView from "@/components/BlogView";
import { getPosts, DAILY_TAG } from "@/lib/api";

export const revalidate = 300;

const PAGE_SIZE = 10;

export const metadata = {
  title: "AI Daily — Tsai Cheng-Hung",
  description: "Automated daily digest of AI news and LLM research.",
};

export default async function BlogDailyPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const sp = await searchParams;
  const all = await getPosts({ tag: DAILY_TAG });

  const total = Math.max(1, Math.ceil(all.length / PAGE_SIZE));
  let page = Number.parseInt(sp.page ?? "1", 10);
  if (Number.isNaN(page) || page < 1) page = 1;
  if (page > total) page = total;

  const start = (page - 1) * PAGE_SIZE;
  const items = all.slice(start, start + PAGE_SIZE);

  return (
    <>
      <Header />
      <BlogView items={items} current={page} total={total} variant="daily" />
    </>
  );
}
