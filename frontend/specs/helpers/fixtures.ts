import { genShortcode } from "short-stuff"
import { rs } from "./index.ts"
import { DeliverableStatus } from "@/types/enums/DeliverableStatus.ts"
import { genSubmission } from "@/store/submissions/specs/fixtures.ts"
import { InvoiceStatus } from "@/types/enums/InvoiceStatus.ts"
import { InvoiceType } from "@/types/enums/InvoiceType.ts"
import { Ratings } from "@/types/enums/Ratings.ts"
import { POWER_LIST } from "@/mixins/viewer.ts"
import type {
  Deliverable,
  CommissionStats,
  CreditCardToken,
  Invoice,
  Order,
  Product,
  Reference,
  Revision,
  SocialSettings,
} from "@/types/main"
import {
  AnonUser,
  ArtistProfile,
  StaffPower,
  StaffPowers,
  User,
} from "@/store/profiles/types/main"
import { BankStatus } from "@/store/profiles/types/enums.ts"

export function genUser(overrides?: Partial<User>): User {
  return {
    rating: 1,
    sfw_mode: false,
    username: "Fox",
    id: 1,
    is_staff: false,
    is_superuser: false,
    avatar_url:
      "https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80",
    email: "fox@artconomy.com",
    favorites_hidden: false,
    blacklist: [],
    nsfw_blacklist: [],
    biography: "",
    taggable: true,
    watching: false,
    blocking: false,
    stars: null,
    rating_count: 0,
    guest: false,
    landscape: false,
    landscape_enabled: false,
    landscape_paid_through: null,
    telegram_link:
      "https://t.me/ArtconomyDevBot/?start=Fox_a0b1a06d-7f8d-4294-96d9-4e3713",
    artist_mode: true,
    international: false,
    hits: 1,
    watches: 0,
    guest_email: "",
    birthday: "1988-08-01",
    service_plan: "Free",
    next_service_plan: "Free",
    verified_email: false,
    paypal_configured: false,
    verified_adult: false,
    ...overrides,
  }
}

export function genGuest(): User {
  const user = genUser()
  user.username = "__1"
  user.guest = true
  user.guest_email = "test@example.com"
  user.email = "324iodf@localhost"
  return user
}

export function genArtistProfile(
  overrides?: Partial<ArtistProfile>,
): ArtistProfile {
  return {
    max_load: 10,
    commission_info: "I draw porn",
    dwolla_configured: false,
    has_products: false,
    commissions_closed: false,
    lgbt: false,
    artist_of_color: false,
    escrow_enabled: true,
    bank_account_status: BankStatus.UNSET,
    public_queue: true,
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
      last_four: "1234",
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
      thumbnail:
        "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png",
      gallery:
        "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png",
      notification:
        "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.80x80_q85.png",
      full: "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png",
      __type__: "data:image",
    },
    read: true,
    submissions: [],
    approved_on: "2023-03-26T09:15:03.507123-05:00",
    ...overrides,
  }
}

export function genProduct(overrides?: Partial<Product>): Product {
  return {
    id: 1,
    name: "Test product",
    description: "This is a test product",
    details_template: "",
    revisions: 2,
    hidden: false,
    max_rating: 2,
    max_parallel: 0,
    task_weight: 3,
    hits: 1,
    expected_turnaround: 3.0,
    track_inventory: false,
    table_product: false,
    international: false,
    escrow_enabled: true,
    removed_on: null,
    removed_reason: null,
    user: {
      id: 1,
      username: "Fox",
      avatar_url:
        "https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80",
      stars: null,
      rating_count: 0,
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: true,
      taggable: true,
      verified_email: false,
    },
    primary_submission: genSubmission(),
    base_price: "10.00",
    starting_price: "10.00",
    compare_at_price: null,
    shield_price: "10.00",
    tags: [],
    available: true,
    featured: false,
    wait_list: false,
    catalog_enabled: true,
    cascade_fees: true,
    escrow_upgradable: false,
    display_position: 0,
    over_order_limit: false,
    paypal: false,
    name_your_price: false,
    ...overrides,
  }
}

export function genDeliverable(overrides?: Partial<Deliverable>): Deliverable {
  const order = genOrder()
  return {
    id: 5,
    name: "Main",
    created_on: "2019-07-26T15:04:41.078424-05:00",
    status: DeliverableStatus.NEW,
    price: 10.0,
    details: "Stuff and things",
    notes: "",
    adjustment: 0,
    commission_info: "",
    adjustment_revisions: 0,
    stream_link: "https://google.com/",
    revisions: 1,
    outputs: [],
    subscribed: true,
    table_order: false,
    international: false,
    adjustment_task_weight: 0,
    adjustment_expected_turnaround: 0,
    expected_turnaround: 1,
    task_weight: 1,
    trust_finalized: false,
    paid_on: null,
    dispute_available_on: null,
    auto_finalize_on: null,
    redacted_on: null,
    redact_available_on: null,
    auto_redact_on: null,
    started_on: null,
    escrow_enabled: true,
    revisions_hidden: false,
    final_uploaded: false,
    rating: 0,
    read: true,
    arbitrator: null,
    cascade_fees: true,
    order,
    product: genProduct({ user: order.seller }),
    display: {
      file: {
        thumbnail:
          "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png",
        gallery:
          "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png",
        notification:
          "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.80x80_q85.png",
        full: "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png",
        __type__: "data:image",
      },
      rating: 0,
      preview: null,
    },
    invoice: "234gsdgsdfg4",
    tip_invoice: null,
    paypal: false,
    paypal_token: "",
    ...overrides,
  }
}

export function genReference(overrides?: Partial<Reference>): Reference {
  return {
    id: 6,
    created_on: "2019-07-26T15:04:41.078424-05:00",
    owner: "Fox",
    read: true,
    rating: 0,
    file: {
      thumbnail:
        "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png",
      gallery:
        "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png",
      notification:
        "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.80x80_q85.png",
      full: "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png",
      __type__: "data:image",
    },
    ...overrides,
  }
}

export function genOrder(overrides?: Partial<Order>): Order {
  const buyer = genUser()
  buyer.username = "Fox"
  buyer.id = 1

  const seller = genUser()
  seller.username = "Vulpes"
  seller.id = 2
  return {
    id: 1,
    created_on: "2019-07-26T15:04:41.078424-05:00",
    seller,
    buyer,
    customer_email: "",
    customer_display_name: "",
    guest_email: "",
    claim_token: null,
    private: false,
    hide_details: false,
    product_name: "Test product",
    deliverable_count: 1,
    read: true,
    status: DeliverableStatus.NEW,
    default_path: { name: "Order", params: { orderId: "1", username: "Fox" } },
    display: {
      file: {
        thumbnail:
          "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png",
        gallery:
          "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png",
        notification:
          "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.80x80_q85.png",
        full: "https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png",
        __type__: "data:image",
      },
      rating: 0,
      preview: null,
    },
    ...overrides,
  }
}

export function genCommissionStats(
  overrides?: Partial<CommissionStats>,
): CommissionStats {
  return {
    load: 5,
    max_load: 10,
    delinquent: false,
    commissions_closed: false,
    commissions_disabled: false,
    products_available: 2,
    active_orders: 1,
    new_orders: 2,
    escrow_enabled: true,
    ...overrides,
  }
}

export function genInvoice(overrides?: Partial<Invoice>): Invoice {
  return {
    id: genShortcode(),
    status: InvoiceStatus.OPEN,
    type: InvoiceType.SALE,
    record_only: false,
    created_on: "2019-07-26T15:04:41.078424-05:00",
    bill_to: genUser({ username: "Fox" }),
    issued_by: genUser({ username: "Vulpes" }),
    targets: [],
    total: 10.0,
    ...overrides,
  }
}

export function genAnon(overrides?: Partial<AnonUser>): AnonUser {
  return {
    rating: Ratings.GENERAL,
    blacklist: [],
    nsfw_blacklist: [],
    sfw_mode: false,
    username: "_",
    birthday: null,
    verified_adult: false,
    ...overrides,
  }
}

export function genPowers(
  overrides?: Partial<Record<StaffPower, boolean>>,
): StaffPowers {
  return {
    id: 1,
    ...Object.fromEntries(POWER_LIST.map((entry) => [entry, false])),
    ...overrides,
  } as StaffPowers
}

export function genSocialSettings(
  overrides?: Partial<SocialSettings>,
): SocialSettings {
  return {
    id: 1,
    allow_promotion: false,
    allow_site_promotion: false,
    nsfw_promotion: false,
    quick_description: "",
    promotion_notes: "",
    display_socials: false,
    ...overrides,
  }
}
