export interface ServicePlan {
  id: number,
  name: string,
  description: string,
  features: string[],
  monthly_charge: string,
  waitlisting: boolean,
  paypal_invoicing: boolean,
  shield_static_price: string,
  per_deliverable_price: string,
  shield_percentage_price: string,
  max_simultaneous_orders: number,
}
