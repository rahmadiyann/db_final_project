import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic"; // Disable route caching

export async function GET() {
  try {
    const stats = await prisma.statistics.findFirst();
    const hasData = Boolean(stats?.total_songs_played);
    return NextResponse.json({ hasData });
  } catch (error) {
    console.error("Error checking data status:", error);
    return NextResponse.json({
      hasData: false,
      error: "Failed to check data status",
    });
  }
}
