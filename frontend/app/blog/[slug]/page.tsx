import type { Metadata } from "next";
import { notFound } from "next/navigation";

import Header from "@/components/Header";
import PostDetailView from "@/components/PostDetailView";
import { getPost } from "@/lib/api";

export const revalidate = 300;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const p = await getPost(slug);
  if (!p) return { title: "Post not found" };

  const title = p.meta_title_en || p.title_en;
  const description = p.meta_description_en || p.excerpt_en;
  const image = p.og_image || p.cover_image || undefined;

  return {
    title: `${title} — Tsai Cheng-Hung`,
    description,
    openGraph: { title, description, images: image ? [image] : undefined },
  };
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug);
  if (!post) notFound();

  return (
    <>
      <Header />
      <PostDetailView post={post} />
    </>
  );
}
