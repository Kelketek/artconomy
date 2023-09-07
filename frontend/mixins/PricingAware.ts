import Component from 'vue-class-component'
import Vue from 'vue'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'

@Component
export default class PricingAware extends Vue {
  public pricing = null as unknown as SingleController<Pricing>

  public getPlan(planName: string) {
    if (!this.pricing.x) {
      return null
    }
    return this.pricing.x.plans.filter((plan) => plan.name === planName)[0] || null
  }

  public created() {
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
    this.pricing.get()
  }
}
