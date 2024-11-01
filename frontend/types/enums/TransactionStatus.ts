export const TransactionStatus = {
  SUCCESS: 0,
  FAILURE: 1,
  PENDING: 2,
} as const

export type TransactionStatusValue = typeof TransactionStatus[keyof typeof TransactionStatus]
