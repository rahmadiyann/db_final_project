/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [
      "i.scdn.co", // Spotify image domain
      // Add any other domains you might be using for artist images
    ],
  },
};

module.exports = nextConfig;
