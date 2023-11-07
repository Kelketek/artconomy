import Submission from '@/types/Submission'

export function genSubmission(overrides?: Partial<Submission>): Submission {
  return {
    id: 322,
    title: '',
    caption: '',
    rating: 0,
    file: {
      thumbnail: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png',
      gallery: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png',
      notification: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.80x80_q85.png',
      full: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png',
      __type__: 'data:image',
    },
    private: false,
    created_on: '2019-07-26T15:04:41.078424-05:00',
    owner: {
      id: 1,
      username: 'Fox',
      avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
      stars: null,
      rating_count: 0,
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: true,
      taggable: true,
      verified_email: false,
    },
    comment_count: 0,
    favorite_count: 0,
    comments_disabled: false,
    display_position: 0,
    tags: [
      'red_panda', 'wah', 'cool', 'nosings', 'awesome', 'stuff', 'floofy',
      'feets', 'female', 'notable', 'fuzzy', 'fuckable', 'soft_paws',
    ],
    subscribed: true,
    preview: null,
    hits: 5,
    favorites: false,
    commission_link: null,
    order: null,
    ...overrides,
  }
}
