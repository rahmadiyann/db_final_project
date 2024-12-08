import ClientWrapper from "./components/ClientWrapper";
import EmptyState from "./components/EmptyState";
import { fetchListeningStats } from "@/lib/data/fetchListeningStats";

// Force dynamic rendering
export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function Home() {
  try {
    // Add timestamp to force fresh data fetch
    const stats = await fetchListeningStats();

    // More specific check for data presence
    const hasData =
      stats.totalSongsPlayed > 0 || stats.albumCompletions.length > 0;

    if (!hasData) {
      return <EmptyState />;
    }

    return (
      <div>
        <ClientWrapper stats={stats} />
      </div>
    );
  } catch (error) {
    console.error("Error in Home component:", error);
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-white">
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold">Oops! Something went wrong</h1>
          <p className="text-gray-400">
            We&apos;re having trouble loading your listening statistics. Please
            try again later. 🎵
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-full"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
}
