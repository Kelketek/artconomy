export type StaffPower = 'handle_disputes' | 'view_social_data' | 'view_financials' | 'moderate_content' | 'moderate_discussion' | 'table_seller' | 'view_as' | 'administrate_users'

export interface StaffPowers extends Record<StaffPower, boolean> {
  id: number,
}
