export const getStripe = () => {
  if (window.StripeInstance) {
    return window.StripeInstance
  }
  /* istanbul ignore else */
  if (window.Stripe) {
    window.StripeInstance = window.Stripe(window.STRIPE_PUBLIC_KEY)
    return window.StripeInstance
  }
  /* istanbul ignore next */
  return null
}
