export function OverviewSkeleton() {
  return (
    <div className="col-span-full bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm animate-pulse">
      <div className="h-7 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="h-24 bg-gray-100 dark:bg-gray-700 rounded-lg"></div>
      </div>
    </div>
  );
}

export function AnalyticsSkeleton() {
  return (
    <div className="col-span-full bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm animate-pulse">
      <div className="h-7 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[...Array(2)].map((_, i) => (
          <div
            key={i}
            className="h-48 bg-gray-100 dark:bg-gray-700 rounded-lg"
          ></div>
        ))}
      </div>
    </div>
  );
}

export function RecentTracksSkeleton() {
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
