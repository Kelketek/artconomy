export interface TOTPDevice {
  id: number,
  name: string,
  config_url: string,
  confirmed: boolean,
  code?: string
}
