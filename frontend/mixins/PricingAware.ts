import {Component} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller.ts'
import Pricing from '@/types/Pricing.ts'
import {ArtVue} from '@/lib/lib.ts'
import {useSingle} from '@/store/singles/hooks.ts'

@Component
export default class PricingAware extends ArtVue {
  public pricing = null as unknown as SingleController<Pricing>

  public getPlan(planName: string) {
    return getPlan(this.pricing, planName)
  }

  public created() {
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
    this.pricing.get()
  }
}


const getPlan = (pricing: SingleController<Pricing>, planName: string) => {
  if (!pricing.x) {
    return null
  }
  return pricing.x.plans.filter((plan) => plan.name === planName)[0] || null
}


export const usePricing = () => {
  const pricing = useSingle<Pricing>('pricing', {endpoint: '/api/sales/pricing-info/'})
  return {promise: pricing.get(), pricing, getPlan: (planName: string) => getPlan(pricing, planName)}
}
