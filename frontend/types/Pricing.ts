import {ServicePlan} from '@/types/ServicePlan'

export default interface Pricing {
  plans: ServicePlan[],
  minimum_price: number,
  table_percentage: number,
  table_static: number,
  table_tax: number,
  international_conversion_percentage: number,
  preferred_plan: string,
}
