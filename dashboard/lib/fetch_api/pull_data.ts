import { SpotifyAnalyticsResponse } from "../../app/utils/analytic_type";

export async function fetchAnalyticsData() {
  try {
    // Fetch Spotify access token
    const tokenResponse = await fetch("http://flask:8000/spotify_analytics", {
      method: "GET",
    });

    const data: SpotifyAnalyticsResponse = await tokenResponse.json();
    console.log(data);

    return data;
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
}
