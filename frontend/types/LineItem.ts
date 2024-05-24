export default interface LineItem {
  id: number,
  priority: number,
  amount: string,
  frozen_value: string|null,
  percentage: string,
  cascade_percentage: boolean,
  cascade_amount: boolean,
  back_into_percentage: boolean,
  type: number,
  description: string,
  destination_account?: number|null,
  destination_user?: number|null,
  targets?: Array<{model: string, id: string|number}>,
}
