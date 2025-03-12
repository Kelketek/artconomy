import { AnonUser, User } from "@/store/profiles/types/main"
import type { ShoppingCart } from "@/types/main"
import { Stripe, StripeConstructor } from "@stripe/stripe-js"

declare global {
  interface Window {
    // We shouldn't be referencing this directly anywhere.
    // We use it during debugging.
    artconomy: any
    chrome?: boolean
    PRERENDERING: number
    windowId: string
    USER_PRELOAD: User | AnonUser
    SANDBOX_APIS: boolean
    RECAPTCHA_SITE_KEY: string
    STRIPE_PUBLIC_KEY: string
    THEOCRATIC_BAN: boolean
    DEFAULT_SERVICE_PLAN_NAME: string
    CART?: ShoppingCart
    Stripe?: StripeConstructor
    StripeInstance: Stripe
    _drip: () => void
    _fb: () => void
    fbq: (...args: any) => void
  }
}
