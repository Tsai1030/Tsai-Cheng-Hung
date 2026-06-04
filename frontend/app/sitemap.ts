import type { MetadataRoute } from "next";
import { getPostsSafe, getProjectsSafe } from "@/lib/api";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://tsai-cheng-hung.vercel.app";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date();
  const [projects, posts] = await Promise.all([getProjectsSafe(), getPostsSafe()]);

  return [
    {
      url: siteUrl,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 1,
    },
    {
      url: `${siteUrl}/projects`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${siteUrl}/blog`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.7,
    },
    ...projects.map((project) => ({
      url: `${siteUrl}/projects/${project.slug}`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    })),
    ...posts.map((post) => ({
      url: `${siteUrl}/blog/${post.slug}`,
      lastModified: post.published_at ? new Date(post.published_at) : now,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
  ];
}
