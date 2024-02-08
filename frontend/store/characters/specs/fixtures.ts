import {Character} from '@/store/characters/types/Character.ts'

export function genCharacter(overrides?: Partial<Character>) {
  return {
    id: 1,
    name: 'Kai',
    description: "Kai is a red panda gal standing at about five foot four. She's got golden eyes, " +
      'and they flicker with curiosity.\n \nHer muzzle is white, capped with a black nosepad, and her face is the ' +
      'brilliant russet of her species, save for her eartufts and a couple of lines on her cheeks, which are also a ' +
      "brilliant white.\n \nThe girl's body is lithe and toned. She wears a low-crop top that hugs C-cup breasts and " +
      'shows off the firm lines of her abs. Her legs are proportionally long for her, ending in cute little footpaws ' +
      'that have pads-- perhaps a bit divergent from her base species.\n \nShe wears a pair of short jeans, frayed ' +
      'at the bottom and a bit washed out, though they hug her hips well, and she seems to have a good deal of ' +
      'flexibility. Her tail, striped with darker shades of her red fur, swishes this way and that as she moves to ' +
      'keep her balance quite precise.',
    private: false,
    open_requests: true,
    hits: 5,
    open_requests_restrictions: 'Can only be awesome.',
    user: {
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
    },
    primary_submission: {
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
      favorites: false,
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
      },
      comment_count: 0,
      favorite_count: 0,
      comments_disabled: false,
      tags: [
        'red_panda', 'wah', 'cool', 'nosings', 'awesome', 'stuff', 'floofy',
        'feets', 'female', 'notable', 'fuzzy', 'fuckable', 'soft_paws',
      ],
      subscribed: true,
      preview: null,
      hits: 5,
      commission_link: null,
    },
    tags: [
      'red_panda', 'female', 'wah', 'stuff', 'cool', 'awesome', 'fuzzy', 'floofy',
      'notable', 'soft_paws', 'feets', 'nosings',
    ],
    nsfw: false,
    taggable: true,
    ...overrides,
  } as Character
}
