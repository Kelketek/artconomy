export function genJournal() {
  return {
    id: 6,
    user: {
      id: 3,
      username: 'Fox',
      avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
      stars: '4.25',
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: null,
    },
    subject: 'Fire',
    body: 'And ice and wind',
    created_on: '2019-06-24T18:40:19.253032-05:00',
    edited_on: '2019-06-28T11:33:35.870239-05:00',
    edited: false,
    comments_disabled: false,
    subscribed: true,
  }
}

export function genMessage() {
  return {
    id: 8,
    sender: {
      id: 3,
      username: 'Fox',
      avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
      stars: '4.25',
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: null,
    },
    subject: 'Test test',
    body: 'This is a test.',
    created_on: '2019-07-01T18:17:36.701607-05:00',
    edited_on: '2019-07-01T18:17:36.701673-05:00',
    read: true,
    edited: false,
  }
}
