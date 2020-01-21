export default interface LineItem {
  id: number,
  priority: number,
  amount: number,
  percentage: number,
  cascade_percentage: boolean,
  cascade_amount: boolean,
  type: number,
  description: string,
  destination_account?: number,
  destination_user?: number|null
}
