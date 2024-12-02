import { getListeningStats } from "../utils/fetch_data";

export async function Analytics() {
  const { analyticsData } = await getListeningStats();
  const sessions = Array.isArray(analyticsData.listening_session_analysis)
    ? analyticsData.listening_session_analysis
    : [analyticsData.listening_session_analysis];

  return (
    <div className="col-span-full bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Listening Analytics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium mb-3">Top Album Completion</h3>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <p className="font-medium">
              {analyticsData.album_completion_rate.album_title}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              by {analyticsData.album_completion_rate.artist_name}
            </p>
            <p className="mt-2">
              {analyticsData.album_completion_rate.completion_percentage}%
              Complete
            </p>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium mb-3">Listening Sessions</h3>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            {sessions.map((session, index) => (
              <div key={index} className="mb-2">
                <p className="font-medium">{session.session_type}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {session.percentage}% of sessions
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
