import { prisma } from "@/lib/prisma";
import { Prisma } from "@prisma/client";
import { Suspense } from "react";
import { unstable_noStore as noStore } from "next/cache";

// Define the type for our track data including relations
type TrackWithRelations = Prisma.fact_historyGetPayload<{
  include: {
    dim_song: true;
    dim_album: true;
    dim_artist: true;
  };
}>;

async function getListeningStats() {
  noStore(); // Opt out of caching
  const recentTracks = await prisma.fact_history.findMany({
    take: 10,
    orderBy: {
      played_at: "desc",
    },
    include: {
      dim_song: true,
      dim_album: true,
      dim_artist: true,
    },
  });

  const totalTracks = await prisma.fact_history.count();
  return { recentTracks, totalTracks };
}

// Separate components for each section to enable independent updates
async function Overview() {
  const { totalTracks } = await getListeningStats();

  return (
    <div className="col-span-full bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Total Tracks Played
          </p>
          <p className="text-2xl font-bold">{totalTracks}</p>
        </div>
      </div>
    </div>
  );
}

async function RecentTracks() {
  const { recentTracks } = await getListeningStats();

  return (
    <div className="col-span-full bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Recent Tracks</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left border-b dark:border-gray-700">
              <th className="pb-3">Song</th>
              <th className="pb-3">Artist</th>
              <th className="pb-3">Album</th>
              <th className="pb-3">Played At</th>
            </tr>
          </thead>
          <tbody>
            {recentTracks.map((track: TrackWithRelations) => (
              <tr key={track.id} className="border-b dark:border-gray-700">
                <td className="py-3">{track.dim_song.title}</td>
                <td className="py-3">{track.dim_artist.name}</td>
                <td className="py-3">{track.dim_album.title}</td>
                <td className="py-3">
                  {new Date(track.played_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Loading fallback components
function OverviewSkeleton() {
  return (
    <div className="col-span-full bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm animate-pulse">
      <div className="h-7 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="h-24 bg-gray-100 dark:bg-gray-700 rounded-lg"></div>
      </div>
    </div>
  );
}

function RecentTracksSkeleton() {
  return (
    <div className="col-span-full bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm animate-pulse">
      <div className="h-7 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="h-12 bg-gray-100 dark:bg-gray-700 rounded"
          ></div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Spotify Analytics Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Your listening history insights
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Suspense fallback={<OverviewSkeleton />}>
          <Overview />
        </Suspense>

        <Suspense fallback={<RecentTracksSkeleton />}>
          <RecentTracks />
        </Suspense>
      </div>
    </div>
  );
}
