export default interface CommissionStats {
  load: number,
  max_load: number,
  delinquent: boolean,
  commissions_closed: boolean,
  commissions_disabled: boolean,
  products_available: number,
  active_orders: number,
  new_orders: number,
  escrow_enabled: boolean,
}
