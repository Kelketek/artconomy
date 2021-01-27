import {rs} from './index'
import {User} from '@/store/profiles/types/User'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile'
import {BankStatus} from '@/store/profiles/types/BankStatus'
import {CreditCardToken} from '@/types/CreditCardToken'
import Revision from '@/types/Revision'
import Order from '@/types/Order'
import {DeliverableStatus} from '@/types/DeliverableStatus'
import Product from '@/types/Product'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Deliverable from '@/types/Deliverable'
import Reference from '@/types/Reference'
import CommissionStats from '@/types/CommissionStats'

export function genUser(overrides?: Partial<User>): User {
  return {
    rating: 1,
    sfw_mode: false,
    username: 'Fox',
    id: 1,
    is_staff: false,
    is_superuser: false,
    avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    email: 'fox@artconomy.com',
    favorites_hidden: false,
    blacklist: [],
    biography: '',
    taggable: true,
    watching: false,
    blocked: false,
    stars: null,
    rating_count: 0,
    guest: false,
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
    birthday: '1988-08-01',
    ...overrides,
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

export function genArtistProfile(overrides?: Partial<ArtistProfile>): ArtistProfile {
  return {
    max_load: 10,
    commission_info: 'I draw porn',
    dwolla_configured: false,
    has_products: false,
    commissions_closed: false,
    auto_withdraw: true,
    lgbt: false,
    artist_of_color: false,
    escrow_disabled: false,
    max_rating: 2,
    bank_account_status: 0 as BankStatus.UNSET,
    ...overrides,
  }
}

export function userResponse() {
  return rs(genUser())
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

export function genRevision(overrides?: Partial<Revision>): Revision {
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
    read: true,
    ...overrides,
  }
}

export function genProduct(overrides?: Partial<Product>): Product {
  return {
    id: 1,
    name: 'Test product',
    description: 'This is a test product',
    revisions: 2,
    hidden: false,
    max_parallel: 0,
    task_weight: 3,
    expected_turnaround: 3.00,
    track_inventory: false,
    table_product: false,
    escrow_disabled: false,
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
    primary_submission: genSubmission(),
    base_price: 10.00,
    starting_price: 10.00,
    tags: [],
    available: true,
    featured: false,
    wait_list: false,
    catalog_enabled: true,
    ...overrides,
  }
}

export function genDeliverable(overrides?: Partial<Deliverable>): Deliverable {
  const order = genOrder()
  return {
    id: 5,
    name: 'Main',
    created_on: '2019-07-26T15:04:41.078424-05:00',
    status: DeliverableStatus.NEW,
    price: 10.00,
    details: 'Stuff and things',
    adjustment: 0,
    commission_info: '',
    adjustment_revisions: 0,
    stream_link: 'https://google.com/',
    revisions: 1,
    outputs: [],
    subscribed: true,
    table_order: false,
    adjustment_task_weight: 0,
    adjustment_expected_turnaround: 0,
    expected_turnaround: 1,
    task_weight: 1,
    trust_finalized: false,
    paid_on: null,
    dispute_available_on: null,
    auto_finalize_on: null,
    started_on: null,
    escrow_disabled: false,
    revisions_hidden: false,
    final_uploaded: false,
    rating: 0,
    read: true,
    arbitrator: null,
    order,
    product: genProduct({user: order.seller}),
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
    ...overrides,
  }
}

export function genReference(overrides?: Partial<Reference>): Reference {
  return {
    id: 6,
    created_on: '2019-07-26T15:04:41.078424-05:00',
    owner: 'Fox',
    read: true,
    rating: 0,
    file: {
      thumbnail: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png',
      gallery: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png',
      notification: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.80x80_q85.png',
      full: 'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png',
      __type__: 'data:image',
    },
    ...overrides,
  }
}

export function genOrder(overrides?: Partial<Order>): Order {
  const buyer = genUser()
  buyer.username = 'Fox'
  buyer.id = 1

  const seller = genUser()
  seller.username = 'Vulpes'
  seller.id = 2
  return {
    id: 1,
    created_on: '2019-07-26T15:04:41.078424-05:00',
    seller,
    buyer,
    customer_email: '',
    claim_token: null,
    private: false,
    product_name: 'Test product',
    deliverable_count: 1,
    read: true,
    default_path: {name: 'Order', params: {orderId: '1', username: 'Fox'}},
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
    ...overrides,
  }
}

export function genCommissionStats(overrides?: Partial<CommissionStats>): CommissionStats {
  return {
    load: 5,
    max_load: 10,
    commissions_closed: false,
    commissions_disabled: false,
    products_available: 2,
    active_orders: 1,
    new_orders: 2,
    ...overrides,
  }
}
