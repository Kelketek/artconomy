import { SingleController } from "@/store/singles/controller.ts"
import { useSingle } from "@/store/singles/hooks.ts"
import type { Pricing } from "@/types/main"

const getPlan = (pricing: SingleController<Pricing>, planName: string) => {
  if (!pricing.x) {
    return null
  }
  return pricing.x.plans.filter((plan) => plan.name === planName)[0] || null
}

export const usePricing = () => {
  const pricing = useSingle<Pricing>("pricing", {
    endpoint: "/api/sales/pricing-info/",
  })
  return {
    promise: pricing.get(),
    pricing,
    getPlan: (planName: string) => getPlan(pricing, planName),
  }
}
