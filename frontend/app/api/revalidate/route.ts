import { revalidatePath } from "next/cache";
import { NextResponse, type NextRequest } from "next/server";

// POST /api/revalidate?secret=...
// Call after seeding / editing content to refresh the cached pages immediately.
export async function POST(req: NextRequest) {
  const secret = req.nextUrl.searchParams.get("secret");
  if (!process.env.REVALIDATE_SECRET || secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ revalidated: false, message: "Invalid secret" }, { status: 401 });
  }

  revalidatePath("/");
  revalidatePath("/projects");
  revalidatePath("/projects/[slug]", "page");
  revalidatePath("/blog");
  revalidatePath("/blog/daily");
  revalidatePath("/blog/[slug]", "page");

  return NextResponse.json({ revalidated: true });
}
