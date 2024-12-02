import { prisma } from "@/lib/prisma";
import { fetchAnalyticsData } from "@/lib/fetch_api/pull_data";
import { unstable_noStore as noStore } from "next/cache";

export async function getListeningStats() {
  noStore();
  const [{ recentTracks, totalTracks }, analyticsData] = await Promise.all([
    prisma.fact_history
      .findMany({
        take: 10,
        orderBy: { played_at: "desc" },
        include: {
          dim_song: true,
          dim_album: true,
          dim_artist: true,
        },
      })
      .then(async (recentTracks) => ({
        recentTracks,
        totalTracks: await prisma.fact_history.count(),
      })),
    fetchAnalyticsData(),
  ]);

  return { recentTracks, totalTracks, analyticsData };
}
