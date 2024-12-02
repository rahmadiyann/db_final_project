import { getListeningStats } from "../utils/fetch_data";

export async function Overview() {
  const { totalTracks, analyticsData } = await getListeningStats();

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

        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Most Active Hour
          </p>
          <p className="text-2xl font-bold">
            {analyticsData.hour_of_day_play_count.hour_of_day}:00
          </p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Favorite Duration
          </p>
          <p className="text-2xl font-bold">
            {analyticsData.song_duration_preference.duration_category}
          </p>
        </div>
      </div>
    </div>
  );
}
