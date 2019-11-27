import {rs} from './index'
import {User} from '@/store/profiles/types/User'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile'
import {BankStatus} from '@/store/profiles/types/BankStatus'
import colors from 'vuetify/es5/util/colors'
import {CreditCardToken} from '@/types/CreditCardToken'
import Revision from '@/types/Revision'
import Order from '@/types/Order'
import {OrderStatus} from '@/types/OrderStatus'
import Product from '@/types/Product'
import {genSubmission} from '@/store/submissions/specs/fixtures'

export function genUser(): User {
  return {
    rating: 1,
    sfw_mode: false,
    username: 'Fox',
    id: 1,
    is_staff: true,
    is_superuser: true,
    csrftoken: 'w3rigun4rgi34untbweildsfunvcsirsunfwe',
    avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    email: 'fox@artconomy.com',
    authtoken: 'fd3445236cba34342352452346',
    favorites_hidden: false,
    blacklist: [],
    biography: '',
    taggable: true,
    watching: false,
    blocked: false,
    stars: null,
    guest: false,
    percentage_fee: '8.00',
    static_fee: '0.75',
    portrait: false,
    portrait_enabled: false,
    portrait_paid_through: null,
    landscape: false,
    landscape_enabled: false,
    landscape_paid_through: null,
    telegram_link: 'https://t.me/ArtconomyDevBot/?start=Fox_a0b1a06d-7f8d-4294-96d9-4e3713',
    offered_mailchimp: true,
    artist_mode: true,
    hits: 1,
    watches: 0,
    guest_email: '',
  }
}

export function genGuest(): User {
  const user = genUser()
  user.username = '__1'
  user.guest = true
  user.guest_email = 'test@example.com'
  user.email = '324iodf@localhost'
  return user
}

export function genArtistProfile(): ArtistProfile {
  return {
    max_load: 10,
    commission_info: 'I draw porn',
    dwolla_configured: false,
    has_products: false,
    commissions_closed: false,
    auto_withdraw: true,
    escrow_disabled: false,
    max_rating: 2,
    bank_account_status: 0 as BankStatus.UNSET,
  }
}

export function userResponse() {
  return rs(genUser())
}

export function vuetifyOptions() {
  return {
    theme: {
      primary: colors.blue,
      secondary: colors.purple,
      danger: colors.red,
      darkBase: colors.grey,
    },
    options: {
      customProperties: true,
    },
  }
}

export function genCard(base?: Partial<CreditCardToken>): CreditCardToken {
  base = base || {}
  return {
    ...{
      last_four: '1234',
      id: 1,
      cvv_verified: true,
      type: 2,
      primary: false,
    },
    ...base,
  }
}

export function genRevision(): Revision {
  return {
    id: 1,
    rating: 0,
    file: {
      thumbnail: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png',
      gallery: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png',
      notification: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.80x80_q85.png',
      full: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png',
      __type__: 'data:image',
    },
  }
}

export function genProduct(): Product {
  return {
    id: 1,
    name: 'Test product',
    description: 'This is a test product',
    revisions: 2,
    hidden: false,
    max_parallel: 0,
    task_weight: 3,
    expected_turnaround: 3.00,
    escrow_disabled: false,
    user: {
      id: 1,
      username: 'Fox',
      avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
      stars: null,
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: true,
      taggable: true,
    },
    primary_submission: genSubmission(),
    price: 10.00,
    tags: [],
    available: true,
    featured: false,
  }
}

export function genOrder(): Order {
  const buyer = genUser()
  buyer.username = 'Fox'
  buyer.id = 1

  const seller = genUser()
  seller.username = 'Vulpes'
  seller.id = 2
  return {
    id: 1,
    created_on: '2019-07-26T15:04:41.078424-05:00',
    status: OrderStatus.NEW,
    price: 10.00,
    product: genProduct(),
    details: 'Stuff and things',
    seller,
    buyer,
    arbitrator: null,
    adjustment: 0,
    commission_info: '',
    adjustment_revisions: 0,
    customer_email: '',
    stream_link: 'https://google.com/',
    revisions: 1,
    outputs: [],
    private: false,
    subscribed: true,
    adjustment_task_weight: 0,
    adjustment_expected_turnaround: 0,
    expected_turnaround: 1,
    task_weight: 1,
    paid_on: null,
    dispute_available_on: null,
    auto_finalize_on: null,
    started_on: null,
    escrow_disabled: false,
    revisions_hidden: false,
    final_uploaded: false,
    rating: 0,
    claim_token: null,
    display: {
      file: {
        thumbnail: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png',
        gallery: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png',
        notification: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.80x80_q85.png',
        full: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png',
        __type__: 'data:image',
      },
      preview: null,
    },
  }
}