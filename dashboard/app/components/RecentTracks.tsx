import { getListeningStats } from "../utils/fetch_data";
import { TrackWithRelations } from "../utils/types";

export async function RecentTracks() {
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
