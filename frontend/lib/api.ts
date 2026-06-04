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
};

export type ProjectDetail = ProjectCard & {
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

export { API_BASE };
