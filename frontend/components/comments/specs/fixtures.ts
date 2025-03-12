export const commentSet = () => ({
  links: {
    next: null,
    previous: null,
  },
  count: 3,
  results: [
    {
      id: 17,
      text: "This is another test.",
      created_on: "2019-06-26T05:38:35.922476-05:00",
      edited_on: "2019-06-26T05:38:35.922499-05:00",
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
      comments: [],
      comment_count: 0,
      edited: false,
      deleted: false,
      subscribed: true,
      system: false,
    },
    {
      id: 16,
      text: "This is a test. @Vulpes.\n\n```\nThis had better not transform. @Vulpes\n```",
      created_on: "2019-06-26T05:37:16.035331-05:00",
      edited_on: "2019-06-28T11:33:56.060789-05:00",
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
      comments: [
        {
          id: 31,
          text: "vbhmfghjk",
          created_on: "2019-06-28T10:56:13.335809-05:00",
          edited_on: "2019-06-28T10:56:13.335850-05:00",
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
          comments: [],
          comment_count: 2,
          edited: false,
          deleted: false,
          subscribed: true,
          system: false,
        },
        {
          id: 35,
          text: "vbhmfghjk",
          created_on: "2019-06-28T10:56:13.335809-05:00",
          edited_on: "2019-06-28T10:56:13.335850-05:00",
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
          comments: [],
          comment_count: 0,
          edited: false,
          deleted: false,
          subscribed: true,
          system: false,
        },
      ],
      comment_count: 0,
      edited: true,
      deleted: false,
      subscribed: true,
      system: false,
    },
    {
      id: 13,
      text: "",
      created_on: "2019-06-26T03:25:10.132490-05:00",
      edited_on: "2019-06-28T10:56:18.782169-05:00",
      user: null,
      comments: [
        {
          id: 30,
          text: "vbhmfghjk",
          created_on: "2019-06-28T10:56:13.335809-05:00",
          edited_on: "2019-06-28T10:56:13.335850-05:00",
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
          comments: [],
          comment_count: 0,
          edited: false,
          deleted: false,
          subscribed: true,
          system: false,
        },
      ],
      comment_count: 1,
      edited: true,
      deleted: true,
      subscribed: true,
      system: false,
    },
  ],
  size: 5,
})
