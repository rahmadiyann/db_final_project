import { Prisma } from "@prisma/client";

export type TrackWithRelations = Prisma.fact_historyGetPayload<{
  include: {
    dim_song: true;
    dim_album: true;
    dim_artist: true;
  };
}>;
