export default interface CommissionStats {
  load: number,
  max_load: number,
  commissions_closed: boolean,
  commissions_disabled: boolean,
  products_available: number,
  active_orders: number,
  new_orders: number,
}
