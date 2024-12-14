# Music Listening Dashboard

This is a [Next.js](https://nextjs.org) project that visualizes a user's Spotify listening statistics in an interactive dashboard.

## Features

- Overview of total minutes listened and songs played
- Album completion rates
- Listening preferences by song duration and explicit content
- Daily and hourly listening patterns
- Longest artist listening streak
- Longest listening day
- Song popularity distribution
- Release year distribution
- Listening session types (focused, background, etc.)
- Empty state with music facts and quiz while waiting for data
- Responsive design for mobile and desktop

## Technologies Used

- [Next.js](https://nextjs.org) (App Router)
- [React](https://reactjs.org)
- [TypeScript](https://www.typescriptlang.org)
- [Tailwind CSS](https://tailwindcss.com)
- [Chart.js](https://www.chartjs.org) (with [react-chartjs-2](https://react-chartjs-2.js.org))
- [Framer Motion](https://www.framer.com/motion/) (for animations)
- [Prisma](https://www.prisma.io) (for database access)

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

## Folder Structure

- `app/`: Next.js App Router files
  - `components/`: React components used in the dashboard
    - `statistics/`: Individual statistic visualization components
  - `types/`: TypeScript type definitions
  - `utils/`: Utility functions
- `lib/`: Library code (e.g., Prisma client)
- `public/`: Static assets
- `prisma/`: Prisma schema and migrations

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out the [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.
