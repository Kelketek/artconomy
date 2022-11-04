export default interface LineItem {
  id: number,
  priority: number,
  amount: number,
  frozen_value: number|null,
  percentage: number,
  cascade_percentage: boolean,
  cascade_amount: boolean,
  back_into_percentage: boolean,
  type: number,
  description: string,
  destination_account?: number,
  destination_user?: number|null
}
