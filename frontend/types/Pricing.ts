import {ServicePlan} from '@/types/ServicePlan.ts'

export default interface Pricing {
  plans: ServicePlan[],
  minimum_price: string,
  table_percentage: string,
  table_static: string,
  table_tax: string,
  international_conversion_percentage: string,
  preferred_plan: string,
}
