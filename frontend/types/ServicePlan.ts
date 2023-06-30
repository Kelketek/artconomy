export interface ServicePlan {
  id: number,
  name: string,
  description: string,
  features: string[],
  monthly_charge: number,
  waitlisting: boolean,
  paypal_invoicing: boolean,
  shield_static_price: number,
  per_deliverable_price: number,
  shield_percentage_price: number,
  max_simultaneous_orders: number,
}
