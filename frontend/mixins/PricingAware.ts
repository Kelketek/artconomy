import {Component} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import {ArtVue} from '@/lib/lib'

@Component
export default class PricingAware extends ArtVue {
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
