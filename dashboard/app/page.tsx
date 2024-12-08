import ClientWrapper from "./components/ClientWrapper";
import { fetchListeningStats } from "@/lib/data/fetchListeningStats";

export default async function Home() {
  const stats = await fetchListeningStats();
  return (
    <div>
      <ClientWrapper stats={stats} />
    </div>
  );
}
