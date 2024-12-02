import { Suspense } from "react";
import { Overview } from "./components/Overview";
import { Analytics } from "./components/Analytics";
import { RecentTracks } from "./components/RecentTracks";
import {
  OverviewSkeleton,
  AnalyticsSkeleton,
  RecentTracksSkeleton,
} from "./components/Skeletons";

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

        <Suspense fallback={<AnalyticsSkeleton />}>
          <Analytics />
        </Suspense>

        <Suspense fallback={<RecentTracksSkeleton />}>
          <RecentTracks />
        </Suspense>
      </div>
    </div>
  );
}
