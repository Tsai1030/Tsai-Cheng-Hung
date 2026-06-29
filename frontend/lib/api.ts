// Typed client for the FastAPI backend.
// Base URL comes from NEXT_PUBLIC_API_URL (see .env.local); defaults to local dev.
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

const REVALIDATE = 300; // ISR window (seconds)

export type ProjectCard = {
  id: number;
  slug: string;
  title_en: string;
  title_zh: string;
  summary_en: string;
  summary_zh: string;
  cover_image: string | null;
  tech: string[];
  links: Record<string, string>;
  period: string | null;
  role_en: string | null;
  role_zh: string | null;
  featured: boolean;
  likes: number;
  views: number;
};

export type ProjectDetail = ProjectCard & {
  body_en: string;
  body_zh: string;
  video_url: string | null;
  github_stars: number | null;
  github_forks: number | null;
  meta_title_en: string | null;
  meta_title_zh: string | null;
  meta_description_en: string | null;
  meta_description_zh: string | null;
  og_image: string | null;
  created_at: string;
  updated_at: string;
};

export async function getProjects(): Promise<ProjectCard[]> {
  const res = await fetch(`${API_BASE}/projects`, { next: { revalidate: REVALIDATE } });
  if (!res.ok) throw new Error(`GET /projects failed: ${res.status}`);
  return res.json();
}

// Degrades to [] if the backend is unreachable (e.g. at build time) so the
// homepage still renders. Use on the homepage; routes that *are* the data
// (e.g. /projects) should use getProjects() and surface errors.
export async function getProjectsSafe(): Promise<ProjectCard[]> {
  try {
    return await getProjects();
  } catch {
    return [];
  }
}

export async function getProject(slug: string): Promise<ProjectDetail | null> {
  const res = await fetch(`${API_BASE}/projects/${encodeURIComponent(slug)}`, {
    next: { revalidate: REVALIDATE },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`GET /projects/${slug} failed: ${res.status}`);
  return res.json();
}

export type PostCard = {
  id: number;
  slug: string;
  title_en: string;
  title_zh: string;
  excerpt_en: string;
  excerpt_zh: string;
  cover_image: string | null;
  tags: string[];
  reading_minutes: number;
  published_at: string | null;
  likes: number;
  views: number;
};

export type PostDetail = PostCard & {
  body_en: string;
  body_zh: string;
  meta_title_en: string | null;
  meta_title_zh: string | null;
  meta_description_en: string | null;
  meta_description_zh: string | null;
  og_image: string | null;
  created_at: string;
  updated_at: string;
};

export async function getPosts(): Promise<PostCard[]> {
  const res = await fetch(`${API_BASE}/posts`, { next: { revalidate: REVALIDATE } });
  if (!res.ok) throw new Error(`GET /posts failed: ${res.status}`);
  return res.json();
}

export async function getPostsSafe(): Promise<PostCard[]> {
  try {
    return await getPosts();
  } catch {
    return [];
  }
}

export async function getPost(slug: string): Promise<PostDetail | null> {
  const res = await fetch(`${API_BASE}/posts/${encodeURIComponent(slug)}`, {
    next: { revalidate: REVALIDATE },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`GET /posts/${slug} failed: ${res.status}`);
  return res.json();
}

// ---------- Likes ----------
// POST endpoints that mutate the shared count in Supabase. Not cached.
async function postLike(path: string): Promise<number> {
  const res = await fetch(`${API_BASE}${path}`, { method: "POST" });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return (await res.json()).likes as number;
}
export const likeProject = (id: number) => postLike(`/projects/${id}/like`);
export const unlikeProject = (id: number) => postLike(`/projects/${id}/unlike`);
export const likePost = (id: number) => postLike(`/posts/${id}/like`);
export const unlikePost = (id: number) => postLike(`/posts/${id}/unlike`);

// ---------- Views ----------
// Fired once per visitor session from the detail page (see ViewPing).
async function postView(path: string): Promise<number> {
  const res = await fetch(`${API_BASE}${path}`, { method: "POST" });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return (await res.json()).views as number;
}
export const viewProject = (id: number) => postView(`/projects/${id}/view`);
export const viewPost = (id: number) => postView(`/posts/${id}/view`);

export { API_BASE };
