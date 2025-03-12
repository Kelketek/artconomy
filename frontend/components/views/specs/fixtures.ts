import type { Conversation } from "@/types/main"
import { TerseUser } from "@/store/profiles/types/main"

export function genJournal() {
  return {
    id: 6,
    user: {
      id: 3,
      username: "Fox",
      avatar_url:
        "https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80",
      stars: "4.25",
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: null,
    },
    subject: "Fire",
    body: "And ice and wind",
    created_on: "2019-06-24T18:40:19.253032-05:00",
    edited_on: "2019-06-28T11:33:35.870239-05:00",
    edited: false,
    comments_disabled: false,
    subscribed: true,
  }
}

export function genConversation(): Conversation {
  return {
    id: 99,
    participants: [
      {
        id: 642,
        username: "Vulpes",
        avatar_url:
          "/media/avatars/642/resized/80/2badea4d-d949-474d-bb74-f933cbc28cc2.png",
        stars: null,
        is_staff: false,
        is_superuser: false,
        guest: false,
        artist_mode: true,
        taggable: true,
      },
      {
        id: 1,
        username: "Fox",
        avatar_url: "/media/avatars/1/resized/80/icon.png",
        stars: 5.0,
        is_staff: true,
        is_superuser: true,
        guest: false,
        artist_mode: true,
        taggable: true,
      },
    ] as TerseUser[],
    created_on: "2019-11-26T11:20:14.715623-06:00",
    read: false,
    last_comment: {
      id: 1093,
      text: "Stuff.",
      created_on: "2019-11-26T18:45:38.025521-06:00",
      edited_on: "2019-11-29T15:44:10.510736-06:00",
      user: {
        id: 642,
        username: "Vulpes",
        avatar_url:
          "/media/avatars/642/resized/80/2badea4d-d949-474d-bb74-f933cbc28cc2.png",
        stars: null,
        is_staff: false,
        is_superuser: false,
        guest: false,
        artist_mode: true,
        taggable: true,
      } as TerseUser,
      comments: [],
      comment_count: 0,
      edited: false,
      deleted: false,
      subscribed: false,
      system: false,
    },
  }
}
