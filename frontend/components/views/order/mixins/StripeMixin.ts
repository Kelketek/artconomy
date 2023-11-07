import {Component, Vue} from 'vue-facing-decorator'

@Component
export default class StripeMixin extends Vue {
  public stripe() {
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
}
