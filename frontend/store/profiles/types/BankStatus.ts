export const BankStatus = {
  UNSET: 0,
  IN_SUPPORTED_COUNTRY: 1,
  NO_SUPPORTED_COUNTRY: 2,
} as const

export type BankStatusValue = typeof BankStatus[keyof typeof BankStatus]
